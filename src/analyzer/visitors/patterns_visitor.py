"""Visitor detecting design patterns and reporting code anti-patterns.

Design-pattern matches are informational and collected in :attr:`patterns`.
Anti-patterns are reported as ``info`` (low severity) issues so they honor the
transversal ``# noqa`` opt-out.
"""

import ast
from typing import Any

from ..utils.ast_utils import calculate_complexity
from .base import BaseVisitor

_MAGIC_ALLOWED = {0, 1, -1, 2}
_GOD_METHOD_LIMIT = 20
_GOD_ATTR_LIMIT = 15
_SPAGHETTI_CC = 20
_SPAGHETTI_DEPTH = 4

_FACTORY_METHODS = {"create", "make", "build"}
_FACTORY_PREFIXES = ("create_", "make_", "build_")
_OBSERVER_METHODS = (
    {"subscribe", "unsubscribe", "notify"},
    {"attach", "detach", "notify"},
)
_STRATEGY_METHODS = {"set_strategy", "set_algorithm"}

_NESTING_NODES = (ast.If, ast.For, ast.While, ast.With, ast.Try)


class PatternsVisitor(BaseVisitor):
    """Detects design patterns and reports code anti-patterns."""

    def __init__(
        self,
        rel_path: str,
        rules_config: dict[str, Any] | None = None,
        scope: str = "all",
    ) -> None:
        """Initializes the patterns visitor.

        Args:
            rel_path: Relative path to the file being analyzed.
            rules_config: Optional rule/severity configuration.
            scope: Analysis scope.
        """
        super().__init__(rel_path, rules_config, scope)
        self.patterns: dict[str, list[str]] = {}

    # --- Design patterns + god object (class-level) ---

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Detects class-level patterns and the god-object anti-pattern."""
        methods = [
            child.name
            for child in node.body
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        method_set = set(methods)

        self._detect_singleton(node)
        self._detect_factory(node, method_set)
        self._detect_observer(method_set, node.name)
        self._detect_strategy(method_set, node.name)
        self._report_god_object(node, methods)

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Detects the decorator pattern and the spaghetti anti-pattern."""
        self._detect_decorator(node)
        self._report_spaghetti(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Reports the spaghetti anti-pattern for async functions."""
        self._report_spaghetti(node)
        self.generic_visit(node)

    # --- Anti-patterns (expression-level) ---

    def visit_Compare(self, node: ast.Compare) -> None:
        """Reports magic numbers used in comparisons."""
        operands = [node.left, *node.comparators]
        for operand in operands:
            if self._is_magic_number(operand):
                self._report_issue(
                    "MAGIC_NUMBER",
                    node.lineno,
                    "Magic number in comparison; extract it into a named constant.",
                    ast.unparse(node),
                )
                break
        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        """Reports dead code guarded by an always-false condition."""
        if self._is_constant_false(node.test):
            self._report_issue(
                "DEAD_CODE", node.lineno, "Unreachable block: condition is always false."
            )
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        """Reports dead loops guarded by an always-false condition."""
        if self._is_constant_false(node.test):
            self._report_issue(
                "DEAD_CODE", node.lineno, "Unreachable loop: condition is always false."
            )
        self.generic_visit(node)

    # --- Pattern helpers ---

    def _detect_singleton(self, node: ast.ClassDef) -> None:
        for stmt in node.body:
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name) and "instance" in target.id.lower():
                        self._add_pattern("singleton", node.name)
                        return

    def _detect_factory(self, node: ast.ClassDef, method_set: set[str]) -> None:
        if node.name.endswith("Factory"):
            self._add_pattern("factory", node.name)
            return
        if method_set & _FACTORY_METHODS:
            self._add_pattern("factory", node.name)
            return
        if any(method.startswith(_FACTORY_PREFIXES) for method in method_set):
            self._add_pattern("factory", node.name)

    def _detect_observer(self, method_set: set[str], name: str) -> None:
        if any(required <= method_set for required in _OBSERVER_METHODS):
            self._add_pattern("observer", name)

    def _detect_strategy(self, method_set: set[str], name: str) -> None:
        if method_set & _STRATEGY_METHODS:
            self._add_pattern("strategy", name)

    def _detect_decorator(self, node: ast.FunctionDef) -> None:
        nested = [child for child in node.body if isinstance(child, ast.FunctionDef)]
        returns_nested = any(
            isinstance(child, ast.Return) and isinstance(child.value, ast.Name)
            for child in node.body
        )
        if nested and returns_nested:
            self._add_pattern("decorator", node.name)

    def _add_pattern(self, pattern: str, name: str) -> None:
        self.patterns.setdefault(pattern, []).append(name)

    # --- Anti-pattern helpers ---

    def _report_god_object(self, node: ast.ClassDef, methods: list[str]) -> None:
        if len(methods) > _GOD_METHOD_LIMIT:
            self._report_issue(
                "GOD_OBJECT",
                node.lineno,
                f"Class '{node.name}' has {len(methods)} methods "
                f"(> {_GOD_METHOD_LIMIT}); consider splitting responsibilities.",
            )
            return
        attribute_count = self._count_instance_attributes(node)
        if attribute_count > _GOD_ATTR_LIMIT:
            self._report_issue(
                "GOD_OBJECT",
                node.lineno,
                f"Class '{node.name}' holds {attribute_count} instance attributes "
                f"(> {_GOD_ATTR_LIMIT}); consider splitting responsibilities.",
            )

    @staticmethod
    def _count_instance_attributes(node: ast.ClassDef) -> int:
        attributes: set[str] = set()
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for sub in ast.walk(child):
                    if (
                        isinstance(sub, ast.Attribute)
                        and isinstance(sub.value, ast.Name)
                        and sub.value.id == "self"
                    ):
                        attributes.add(sub.attr)
        return len(attributes)

    def _report_spaghetti(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        complexity = calculate_complexity(node)
        depth = _max_nesting_depth(node)
        if complexity > _SPAGHETTI_CC or depth > _SPAGHETTI_DEPTH:
            self._report_issue(
                "SPAGHETTI_CODE",
                node.lineno,
                f"Function '{node.name}' is deeply nested/hard to follow "
                f"(complexity={complexity}, depth={depth}).",
            )

    @staticmethod
    def _is_magic_number(node: ast.AST) -> bool:
        if not isinstance(node, ast.Constant):
            return False
        value = node.value
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return False
        return value not in _MAGIC_ALLOWED

    @staticmethod
    def _is_constant_false(node: ast.AST) -> bool:
        if not isinstance(node, ast.Constant):
            return False
        return node.value is False or (isinstance(node.value, int) and node.value == 0)


def _max_nesting_depth(node: ast.AST, depth: int = 0) -> int:
    """Computes the maximum control-flow nesting depth of a function body.

    Args:
        node: The AST node to inspect.
        depth: Current accumulated depth.

    Returns:
        The maximum nesting depth found.
    """
    max_depth = depth
    for child in ast.iter_child_nodes(node):
        child_depth = depth + 1 if isinstance(child, _NESTING_NODES) else depth
        max_depth = max(max_depth, _max_nesting_depth(child, child_depth))
    return max_depth
