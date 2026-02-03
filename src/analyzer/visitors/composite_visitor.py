"""Composite visitor that orchestrates all specialized visitors."""

import ast
from typing import Any, Dict, List, Optional

from .imports_visitor import ImportsVisitor
from .metrics_visitor import MetricsVisitor
from .standards_visitor import StandardsVisitor


class CompositeVisitor(ast.NodeVisitor):
    """Orchestrator that combines all specialized visitors.

    This class maintains compatibility with the original QGISASTVisitor API
    while delegating work to specialized visitors.

    Attributes:
        rel_path: Relative path to the file being analyzed.
        issues: Aggregated list of all issues from all visitors.
        docstring_styles: Aggregated docstring styles from metrics visitor.
        type_hint_stats: Type hint statistics from metrics visitor.
        docstring_stats: Docstring statistics from metrics visitor.
    """

    def __init__(self, rel_path: str, rules_config: Optional[Dict[str, Any]] = None) -> None:
        """Initializes the composite visitor.

        Args:
            rel_path: Relative path to the file being analyzed.
            rules_config: Optional configuration for audit rules and severities.
        """
        self.rel_path = rel_path
        self.rules_config = rules_config or {}

        # Initialize specialized visitors
        self._imports_visitor = ImportsVisitor(rel_path, rules_config)
        self._metrics_visitor = MetricsVisitor(rel_path, rules_config)
        self._standards_visitor = StandardsVisitor(rel_path, rules_config)

        # Aggregated results
        self.issues: List[Dict[str, Any]] = []

    @property
    def docstring_styles(self) -> List[str]:
        """Returns docstring styles from metrics visitor."""
        return self._metrics_visitor.docstring_styles

    @property
    def type_hint_stats(self) -> Dict[str, int]:
        """Returns type hint statistics from metrics visitor."""
        return self._metrics_visitor.type_hint_stats

    @property
    def docstring_stats(self) -> Dict[str, int]:
        """Returns docstring statistics from metrics visitor."""
        return self._metrics_visitor.docstring_stats

    def visit(self, node: ast.AST) -> None:
        """Visits a node with all specialized visitors.

        Args:
            node: The AST node to visit.
        """
        # Dispatch to all specialized visitors
        self._imports_visitor.visit(node)
        self._metrics_visitor.visit(node)
        self._standards_visitor.visit(node)

        # Aggregate issues
        self.issues = []
        self.issues.extend(self._imports_visitor.issues)
        self.issues.extend(self._metrics_visitor.issues)
        self.issues.extend(self._standards_visitor.issues)
