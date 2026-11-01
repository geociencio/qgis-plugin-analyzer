"""Alias and loop bindings for the signal collector."""

from __future__ import annotations

import ast


def _call_name(node: ast.AST) -> str:
    """Return the last attribute/name of a call target."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def _unwrap_sequence(node: ast.AST) -> ast.AST:
    """Unwrap ``list``/``tuple`` around a literal sequence."""
    if (
        isinstance(node, ast.Call)
        and _call_name(node.func) in {"list", "tuple"}
        and len(node.args) == 1
    ):
        return node.args[0]
    return node


class _ScopeState:
    """Alias and loop bindings for one file's signal collector."""

    def __init__(self) -> None:
        self.aliases: list[dict[str, str | None]] = [{}]
        self.loops: list[dict[str, list[str | None] | None]] = []
        self.factory_classes: dict[str, str] = {}
        self.deleted_classes: set[str] = set()

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

    def record_factory(self, target: str, value: ast.AST) -> None:
        """Remember the class instantiated into a local/self target."""
        if not isinstance(value, ast.Call):
            return
        name = _call_name(value.func)
        if name and name[0].isupper():
            self.factory_classes[target] = name

    def mark_deleted(self, expression: str) -> None:
        """Mark the class behind a ``deleteLater`` receiver as disposed."""
        for target, class_name in self.factory_classes.items():
            if expression == target or expression.startswith(target + "."):
                self.deleted_classes.add(class_name)

    def is_deleted_class(self, name: str | None) -> bool:
        """Return whether a class instance is explicitly disposed locally."""
        return name is not None and name in self.deleted_classes

    def loop_values(self, iterable: ast.AST) -> list[str | None] | None:
        """Expand a literal tuple/list loop into canonical values."""
        iterable = _unwrap_sequence(iterable)
        if not isinstance(iterable, (ast.Tuple, ast.List)):
            return None
        values: list[str | None] = []
        for element in iterable.elts:
            values.extend(self.expand(element))
        return values or None

    def loop_bindings(
        self, iterable: ast.AST, targets: list[str]
    ) -> dict[str, list[str | None] | None]:
        """Expand a loop, including tuple-unpacked targets."""
        iterable = _unwrap_sequence(iterable)
        if len(targets) > 1 and isinstance(iterable, (ast.Tuple, ast.List)):
            bindings: dict[str, list[str | None]] = {target: [] for target in targets}
            for row in iterable.elts:
                if not isinstance(row, (ast.Tuple, ast.List)) or len(row.elts) != len(targets):
                    return {target: None for target in targets}
                for index, target in enumerate(targets):
                    bindings[target].extend(self.expand(row.elts[index]))
            return {target: values or None for target, values in bindings.items()}
        values = self.loop_values(iterable)
        return {target: values for target in targets}

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
