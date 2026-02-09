"""Base visitor class with shared functionality for all AST visitors."""

import ast
from typing import Any, Dict, List, Optional


class BaseVisitor(ast.NodeVisitor):
    """Base class for AST visitors with common reporting and configuration logic.

    Designed for both direct usage and single-pass traversal (CompositeVisitor).
    """

    def __init__(self, rel_path: str, rules_config: Optional[Dict[str, Any]] = None) -> None:
        """Initializes the base visitor.

        Args:
            rel_path: Relative path to the file being analyzed.
            rules_config: Optional configuration for audit rules and severities.
        """
        self.rel_path = rel_path
        self.issues: List[Dict[str, Any]] = []
        self.rules_config = rules_config or {}
        self._is_single_pass = False

    def generic_visit(self, node: ast.AST) -> None:
        """Controlled recursion: only recurses if not in single-pass mode.

        In single-pass mode, CompositeVisitor manages the recursion.
        """
        if not self._is_single_pass:
            super().generic_visit(node)

    def enter_node(self, node: ast.AST, parent: Optional[ast.AST] = None) -> None:
        """Dispatches to visit_XXX method when entering a node."""
        method_name = f"visit_{node.__class__.__name__}"
        visitor = getattr(self, method_name, None)
        if visitor:
            # Check if signature supports parent
            import inspect

            sig = inspect.signature(visitor)
            if "parent" in sig.parameters:
                visitor(node, parent=parent)
            else:
                visitor(node)

    def exit_node(self, node: ast.AST, parent: Optional[ast.AST] = None) -> None:
        """Dispatches to leave_XXX method when exiting a node."""
        method_name = f"leave_{node.__class__.__name__}"
        visitor = getattr(self, method_name, None)
        if visitor:
            import inspect

            sig = inspect.signature(visitor)
            if "parent" in sig.parameters:
                visitor(node, parent=parent)
            else:
                visitor(node)

    def _should_report(self, rule_id: str) -> bool:
        """Check if rule should be reported based on config.

        Args:
            rule_id: The rule identifier.

        Returns:
            True if the rule should be reported, False otherwise.
        """
        severity = self.rules_config.get(rule_id, "warning")
        return bool(severity != "ignore")

    def _get_severity(self, rule_id: str) -> str:
        """Get configured severity for rule (maps to 'high', 'medium', 'low').

        Args:
            rule_id: The rule identifier.

        Returns:
            The severity level as a string.
        """
        config_severity = self.rules_config.get(rule_id, "warning")
        severity_map = {
            "error": "high",
            "warning": "medium",
            "info": "low",
        }
        return severity_map.get(config_severity, "medium")

    def _report_issue(self, rule_id: str, line: int, message: str, code: str = "") -> None:
        """Helper to report an issue if enabled.

        Args:
            rule_id: The rule identifier.
            line: Line number where the issue was detected.
            message: Description of the issue.
            code: Optional code snippet related to the issue.
        """
        if self._should_report(rule_id):
            self.issues.append(
                {
                    "file": self.rel_path,
                    "line": line,
                    "type": rule_id,
                    "severity": self._get_severity(rule_id),
                    "message": message,
                    "code": code,
                }
            )
