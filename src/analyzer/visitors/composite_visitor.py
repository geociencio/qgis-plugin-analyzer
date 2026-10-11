"""Composite visitor that orchestrates all specialized visitors."""

import ast
from typing import Any

from .i18n_visitor import I18nVisitor, collect_docstring_lines
from .imports_visitor import ImportsVisitor
from .metrics_visitor import MetricsVisitor
from .noqa import collect_noqa_directives
from .patterns_visitor import PatternsVisitor
from .qgis_rules_visitor import QGISRulesVisitor
from .qt_transition_visitor import QtTransitionVisitor
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

    def __init__(
        self,
        rel_path: str,
        rules_config: dict[str, Any] | None = None,
        scope: str = "all",
        lines: list[str] | None = None,
    ) -> None:
        """Initializes the composite visitor.

        Args:
            rel_path: Relative path to the file being analyzed.
            rules_config: Optional configuration for audit rules and severities.
            scope: The scope of analysis.
            lines: Source lines of the file, threaded to the i18n visitor for
                inline ``# no-i18n`` / ``# noqa`` comment detection.
        """
        self.rel_path = rel_path
        self.rules_config = rules_config or {}
        self.scope = scope
        self.lines = lines or []
        self._noqa_directives = collect_noqa_directives(self.lines) if self.lines else {}

        # Initialize specialized visitors
        self._imports_visitor = ImportsVisitor(rel_path, rules_config, scope)
        self._metrics_visitor = MetricsVisitor(rel_path, rules_config, scope)
        self._standards_visitor = StandardsVisitor(rel_path, rules_config, scope)
        self._i18n_visitor = I18nVisitor(rel_path, rules_config, scope, lines)
        self._qgis_rules_visitor = QGISRulesVisitor(rel_path, rules_config, scope)
        self._qt_transition_visitor = QtTransitionVisitor(rel_path, rules_config, scope)
        self._safety_visitor = SafetyVisitor(rel_path, rules_config, scope)
        self._patterns_visitor = PatternsVisitor(rel_path, rules_config, scope)

        # Filter visitors based on scope
        self._active_visitors = []
        if self.scope == "all":
            self._active_visitors = [
                self._imports_visitor,
                self._metrics_visitor,
                self._standards_visitor,
                self._i18n_visitor,
                self._qgis_rules_visitor,
                self._qt_transition_visitor,
                self._safety_visitor,
                self._patterns_visitor,
            ]
        elif self.scope == "i18n":
            self._active_visitors = [self._i18n_visitor]
        elif self.scope == "performance":
            self._active_visitors = [self._standards_visitor, self._safety_visitor]
        elif self.scope == "architecture":
            self._active_visitors = [
                self._imports_visitor,
                self._metrics_visitor,
                self._qt_transition_visitor,
                self._patterns_visitor,
            ]
        elif self.scope == "security":
            # StandardsVisitor also has some security rules (subprocess)
            self._active_visitors = [self._standards_visitor]

        # Configure visitors for single-pass mode
        for visitor in [
            self._imports_visitor,
            self._metrics_visitor,
            self._standards_visitor,
            self._i18n_visitor,
            self._qgis_rules_visitor,
            self._qt_transition_visitor,
            self._safety_visitor,
            self._patterns_visitor,
        ]:
            visitor._is_single_pass = True

        # Aggregated results
        self.issues: list[dict[str, Any]] = []
        self._node_stack: list[ast.AST] = []

    @property
    def docstring_styles(self) -> list[str]:
        """Returns docstring styles from metrics visitor."""
        return self._metrics_visitor.docstring_styles

    @property
    def type_hint_stats(self) -> dict[str, int]:
        """Returns type hint statistics from metrics visitor."""
        return self._metrics_visitor.type_hint_stats

    @property
    def docstring_stats(self) -> dict[str, int]:
        """Returns docstring statistics from metrics visitor."""
        return self._metrics_visitor.docstring_stats

    @property
    def patterns(self) -> dict[str, list[str]]:
        """Returns design patterns detected by the patterns visitor."""
        return self._patterns_visitor.patterns

    @property
    def qgis_context(self) -> dict[str, Any]:
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

        # Pre-compute docstring lines for the i18n visitor before traversal.
        if isinstance(node, ast.Module):
            self._i18n_visitor.docstring_lines = collect_docstring_lines(node)

        # 1. Notify all visitors (Enter)
        for visitor in self._active_visitors:
            visitor.enter_node(node, parent=parent)

        # 2. Recurse to children
        self._node_stack.append(node)
        self.generic_visit(node)
        self._node_stack.pop()

        # 3. Notify all visitors (Exit)
        for visitor in self._active_visitors:
            visitor.exit_node(node, parent=parent)

        # 4. Aggregate issues (only once at the end of root visit)
        if isinstance(node, ast.Module):
            self.issues = []
            for visitor in self._active_visitors:
                self.issues.extend(visitor.issues)
            if self._noqa_directives:
                self.issues = [issue for issue in self.issues if not self._is_suppressed(issue)]

    def _is_suppressed(self, issue: dict[str, Any]) -> bool:
        """Checks whether an issue is suppressed by an inline ``# noqa`` comment.

        Args:
            issue: An aggregated issue dictionary (uses ``line`` and ``type``).

        Returns:
            True if a ``# noqa`` directive on the issue's line covers it.
        """
        line = issue.get("line")
        if not isinstance(line, int) or line not in self._noqa_directives:
            return False

        codes = self._noqa_directives[line]
        if codes is None:
            return True
        return str(issue.get("type", "")) in codes
