"""Collect signal connect/disconnect events from a module's AST.

The collector is configuration-independent so its result can live in the
per-module analysis cache. Scope matching, lifetime policy and emission are
applied later by :mod:`analyzer.signal_resolver`.
"""

from __future__ import annotations

import ast
from dataclasses import asdict, dataclass, replace
from typing import Any

_CONNECTION_PREFIXES = ("Qt.", "QtCore.Qt.", "PyQt5.QtCore.Qt.", "PyQt6.QtCore.Qt.")
_PARENTED_CTOR_NAMES = {
    "QDialog",
    "QDockWidget",
    "QFrame",
    "QGroupBox",
    "QMainWindow",
    "QScrollArea",
    "QSplitter",
    "QTabWidget",
    "QWidget",
}
_MAX_TEXT = 160
_RECEIVER_AND_SLOT_ARGS = 2
_CONNECTION_TYPE_ARGS = 3


@dataclass(frozen=True)
class SignalEvent:
    """One signal connect/disconnect observation."""

    file: str
    line: int
    scope: str
    class_name: str | None
    function_name: str
    kind: str
    sender: str
    receiver: str | None
    slot: str | None
    connection_type: str
    confidence: str
    text: str
    order: int
    lifetime: str | None = None

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return asdict(self)


def collect_signal_events(tree: ast.AST, rel_path: str) -> list[dict[str, Any]]:
    """Collect signal events from ``tree``.

    Args:
        tree: Parsed module AST.
        rel_path: Project-relative module path.

    Returns:
        JSON-serializable events with local lifetime hints attached.
    """
    collector = _SignalCollector(rel_path)
    collector.visit(tree)
    collector.finalize()
    return [event.as_dict() for event in collector.events]


def _target_name(node: ast.AST) -> str | None:
    """Return the name of a simple assignment/loop target."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return ast.unparse(node)
    return None


def _slot_confidence(slot: str | None) -> str:
    """Return low confidence for unknown/dynamic slots."""
    if slot is None or slot.startswith("<"):
        return "low"
    return "high"


def _minimum_confidence(values: list[str]) -> str:
    """Combine confidence levels, keeping the weakest one."""
    if "low" in values:
        return "low"
    if "medium" in values:
        return "medium"
    return "high"


def _is_connection_type(node: ast.AST) -> bool:
    """Return whether a positional argument is a Qt connection type."""
    text = ast.unparse(node)
    return any(text.startswith(prefix) for prefix in _CONNECTION_PREFIXES) or (
        "ConnectionType" in text
    )


def _connection_type(node: ast.AST) -> str:
    """Map a Qt connection type expression to the report vocabulary."""
    text = ast.unparse(node).lower()
    if "uniqueconnection" in text:
        return "unique"
    if "queuedconnection" in text:
        return "queued"
    if "directconnection" in text:
        return "direct"
    return "unknown"


def _call_name(node: ast.AST) -> str:
    """Return the last attribute/name of a call target."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def _matches_hint(expression: str, hint: str) -> bool:
    """Return whether ``hint`` is the same expression or a parent chain."""
    return expression == hint or expression.startswith(hint + ".")


def _add_hint(hints: dict[str, set[str]], kind: str, expression: str) -> None:
    """Record a lifetime hint unless it is a generic self/empty expression."""
    if expression and expression != "self":
        hints[kind].add(expression)


def _record_parented_assignment(hints: dict[str, set[str]], target: str, value: ast.AST) -> None:
    """Record an explicit QWidget(parent)-style assignment."""
    if not isinstance(value, ast.Call):
        return
    if _call_name(value.func) in _PARENTED_CTOR_NAMES and value.args:
        _add_hint(hints, "parented", target)


class _ScopeState:
    """Alias and loop bindings for one file's signal collector."""

    def __init__(self) -> None:
        self.aliases: list[dict[str, str | None]] = [{}]
        self.loops: list[dict[str, list[str | None] | None]] = []

    def push_scope(self) -> None:
        """Enter a class/function alias scope."""
        self.aliases.append({})

    def pop_scope(self) -> None:
        """Leave the current alias scope."""
        self.aliases.pop()

    def push_loop(self, name: str, values: list[str | None] | None) -> None:
        """Bind a loop target for the loop body."""
        self.loops.append({name: values})

    def pop_loop(self) -> None:
        """Leave the current loop binding."""
        self.loops.pop()

    def record_alias(self, target: str, value: ast.AST) -> None:
        """Store a simple alias, invalidating ambiguous reassignments."""
        if not isinstance(value, (ast.Name, ast.Attribute)):
            return
        canonical = self.canonical(value)
        aliases = self.aliases[-1]
        if target in aliases and aliases[target] != canonical:
            aliases[target] = None
        else:
            aliases[target] = canonical

    def loop_values(self, iterable: ast.AST) -> list[str | None] | None:
        """Expand a literal tuple/list loop into canonical values."""
        if not isinstance(iterable, (ast.Tuple, ast.List)):
            return None
        values: list[str | None] = []
        for element in iterable.elts:
            values.extend(self.expand(element))
        return values or None

    def expand(self, node: ast.AST) -> list[str]:
        """Resolve a node to one or more canonical expressions."""
        if isinstance(node, ast.Name):
            binding = self.binding(node.id)
            if binding is not None:
                return [value if value is not None else node.id for value in binding]
            aliased = self.alias(node.id)
            return [aliased if aliased is not None else node.id]
        if isinstance(node, ast.Attribute):
            bases = self.expand(node.value)
            return [f"{base}.{node.attr}" for base in bases if base]
        return [ast.unparse(node)]

    def canonical(self, node: ast.AST) -> str:
        """Return the first canonical form for a node."""
        expanded = self.expand(node)
        return expanded[0] if expanded else ast.unparse(node)

    def binding(self, name: str) -> list[str | None] | None:
        """Return an active loop binding for ``name``, if any."""
        for bindings in reversed(self.loops):
            if name in bindings:
                return bindings[name]
        return None

    def alias(self, name: str) -> str | None:
        """Return an active alias for ``name``, if any."""
        for aliases in reversed(self.aliases):
            if name in aliases:
                return aliases[name]
        return None

    def alias_is_ambiguous(self, name: str) -> bool:
        """Return whether ``name`` was reassigned to conflicting expressions."""
        return any(name in aliases and aliases[name] is None for aliases in reversed(self.aliases))

    def expr_confidence(self, node: ast.AST) -> str:
        """Estimate whether a sender/receiver could be resolved statically."""
        if isinstance(node, ast.Name):
            binding = self.binding(node.id)
            if binding is not None:
                return "low" if any(value is None for value in binding) else "high"
            if self.alias_is_ambiguous(node.id):
                return "low"
            return "high"
        if isinstance(node, ast.Attribute):
            return self.expr_confidence(node.value)
        if isinstance(node, (ast.Subscript, ast.Call)):
            return "low" if isinstance(node, ast.Subscript) else "high"
        return "low"


class _SignalCollector(ast.NodeVisitor):
    """Single-pass signal event collector with local alias/loop resolution."""

    def __init__(self, rel_path: str) -> None:
        self.rel_path = rel_path
        self.events: list[SignalEvent] = []
        self._classes: list[str] = []
        self._functions: list[str] = []
        self._scope_state = _ScopeState()
        self._hints: dict[str, set[str]] = {
            "delete_later": set(),
            "parented": set(),
            "destroyed": set(),
        }
        self._order = 0

    @property
    def _scope(self) -> str:
        parts = [*self._classes, *self._functions]
        return ".".join(parts) if parts else "<module>"

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Enter a class scope."""
        self._classes.append(node.name)
        self._scope_state.push_scope()
        self.generic_visit(node)
        self._scope_state.pop_scope()
        self._classes.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Enter a function/method scope."""
        self._functions.append(node.name)
        self._scope_state.push_scope()
        self.generic_visit(node)
        self._scope_state.pop_scope()
        self._functions.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Enter an async function/method scope."""
        self.visit_FunctionDef(node)  # type: ignore[arg-type]

    def visit_Assign(self, node: ast.Assign) -> None:
        """Collect alias and parent/child hints from assignments."""
        for target in node.targets:
            target_name = _target_name(target)
            if target_name:
                _record_parented_assignment(self._hints, target_name, node.value)
                self._scope_state.record_alias(target_name, node.value)
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        """Expand literal tuple/list loop variables for the loop body."""
        target_name = _target_name(node.target)
        if target_name is None:
            self.generic_visit(node)
            return

        values = self._scope_state.loop_values(node.iter)
        self._scope_state.push_loop(target_name, values)
        for statement in [*node.body, *node.orelse]:
            self.visit(statement)
        self._scope_state.pop_loop()

    def visit_Call(self, node: ast.Call) -> None:
        """Record connect/disconnect and local lifetime evidence."""
        func = node.func
        if isinstance(func, ast.Attribute):
            if func.attr in {"connect", "disconnect"}:
                self._record_signal_call(node, func)
            elif func.attr == "deleteLater":
                _add_hint(self._hints, "delete_later", self._scope_state.canonical(func.value))
            elif func.attr == "setParent":
                _add_hint(self._hints, "parented", self._scope_state.canonical(func.value))
        self.generic_visit(node)

    def finalize(self) -> None:
        """Attach conservative lifetime hints to connect events."""
        for index, event in enumerate(self.events):
            if event.kind != "connect":
                continue
            lifetime = self._lifetime_for(event)
            if lifetime is not None:
                self.events[index] = replace(event, lifetime=lifetime)

    def _record_signal_call(self, node: ast.Call, func: ast.Attribute) -> None:
        """Create one event per resolved sender (loops can expand to many)."""
        senders = self._scope_state.expand(func.value)
        if not senders:
            return
        receiver, slot, connection_type = self._call_parts(node)
        confidence = _minimum_confidence(
            [self._scope_state.expr_confidence(func.value), _slot_confidence(slot)]
        )
        text = ast.unparse(node)[:_MAX_TEXT]
        for sender in senders:
            self.events.append(
                SignalEvent(
                    file=self.rel_path,
                    line=getattr(node, "lineno", 0),
                    scope=self._scope,
                    class_name=self._classes[-1] if self._classes else None,
                    function_name=self._functions[-1] if self._functions else "<module>",
                    kind=func.attr,
                    sender=sender,
                    receiver=receiver,
                    slot=slot,
                    connection_type=connection_type,
                    confidence=confidence,
                    text=text,
                    order=self._order,
                )
            )
            self._order += 1
            if func.attr == "connect" and sender.endswith(".destroyed"):
                _add_hint(self._hints, "destroyed", sender[: -len(".destroyed")])

    def _call_parts(self, node: ast.Call) -> tuple[str | None, str | None, str]:
        """Return ``(receiver, slot, connection_type)`` for a connect/disconnect."""
        args = list(node.args)
        connection_type = "auto"
        type_expr: ast.AST | None = None
        for keyword in node.keywords:
            if keyword.arg == "type":
                type_expr = keyword.value
                connection_type = _connection_type(keyword.value)

        if len(args) >= _CONNECTION_TYPE_ARGS:
            type_expr = args[_CONNECTION_TYPE_ARGS - 1]
            connection_type = _connection_type(type_expr)
            args = args[:_RECEIVER_AND_SLOT_ARGS]
        elif len(args) == _RECEIVER_AND_SLOT_ARGS and _is_connection_type(args[1]):
            type_expr = args[1]
            connection_type = _connection_type(type_expr)
            args = args[:1]
        if type_expr is not None and connection_type == "auto":
            connection_type = _connection_type(type_expr)

        receiver: str | None = None
        slot: str | None = None
        if len(args) >= _RECEIVER_AND_SLOT_ARGS:
            receiver = self._scope_state.canonical(args[0])
            slot = self._scope_state.canonical(args[1])
        elif args:
            slot = self._scope_state.canonical(args[0])
            receiver = "self" if slot.startswith("self.") or slot == "self" else None
        return receiver, slot, connection_type

    def _lifetime_for(self, event: SignalEvent) -> str | None:
        """Classify a connect event from local lifetime hints."""
        candidates = [event.sender, event.receiver or ""]
        for lifetime, hint_key in (
            ("local_widget", "delete_later"),
            ("parent_child", "parented"),
            ("destroyed_hook", "destroyed"),
        ):
            if any(
                _matches_hint(candidate, hint)
                for candidate in candidates
                for hint in self._hints[hint_key]
            ):
                return lifetime
        return None
