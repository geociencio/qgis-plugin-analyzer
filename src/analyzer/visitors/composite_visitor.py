"""Composite visitor that orchestrates all specialized visitors."""

import ast
from typing import Any, Dict, List, Optional

from .imports_visitor import ImportsVisitor
from .metrics_visitor import MetricsVisitor
from .qgis_rules_visitor import QGISRulesVisitor
from .safety_visitor import SafetyVisitor
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
        self._qgis_rules_visitor = QGISRulesVisitor(rel_path, rules_config)
        self._safety_visitor = SafetyVisitor(rel_path, rules_config)

        # Configure visitors for single-pass mode
        for visitor in [
            self._imports_visitor,
            self._metrics_visitor,
            self._standards_visitor,
            self._qgis_rules_visitor,
            self._safety_visitor,
        ]:
            visitor._is_single_pass = True

        # Aggregated results
        self.issues: List[Dict[str, Any]] = []
        self._node_stack: List[ast.AST] = []

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

    @property
    def qgis_context(self) -> Dict[str, Any]:
        """Returns QGIS-specific context and metrics."""
        return {
            "processing_framework": self._qgis_rules_visitor.processing_framework,
            "gdal_style": self._qgis_rules_visitor.gdal_style,
            "pyqt_transition": self._qgis_rules_visitor.qt_imports,
            "legacy_signals_count": self._qgis_rules_visitor.legacy_signals,
            "signal_leaks": self._safety_visitor.signal_leaks,
        }

    def visit(self, node: ast.AST) -> None:
        """Visits a node with all specialized visitors in a single pass.

        Args:
            node: The AST node to visit.
        """
        parent = self._node_stack[-1] if self._node_stack else None

        # 1. Notify all visitors (Enter)
        for visitor in [
            self._imports_visitor,
            self._metrics_visitor,
            self._standards_visitor,
            self._qgis_rules_visitor,
            self._safety_visitor,
        ]:
            visitor.enter_node(node, parent=parent)

        # 2. Recurse to children
        self._node_stack.append(node)
        self.generic_visit(node)
        self._node_stack.pop()

        # 3. Notify all visitors (Exit)
        for visitor in [
            self._imports_visitor,
            self._metrics_visitor,
            self._standards_visitor,
            self._qgis_rules_visitor,
            self._safety_visitor,
        ]:
            visitor.exit_node(node, parent=parent)

        # 4. Aggregate issues (only once at the end of root visit)
        if isinstance(node, ast.Module):
            self.issues = []
            self.issues.extend(self._imports_visitor.issues)
            self.issues.extend(self._metrics_visitor.issues)
            self.issues.extend(self._standards_visitor.issues)
            self.issues.extend(self._qgis_rules_visitor.issues)
            self.issues.extend(self._safety_visitor.issues)
