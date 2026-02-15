"""Visitor for QGIS safety and runtime hazard detection."""

import ast
from typing import Any, Dict, List, Optional, Set

from .base import BaseVisitor


class SafetyVisitor(BaseVisitor):
    """Visitor to detect QGIS runtime hazards and safety violations.

    Detects:
    - Signal Leaks: Signals connected but not disconnected in 'unload'.
    - UI Blocking: Intensive loops in UI handlers without QgsTask.
    """

    def __init__(
        self,
        rel_path: str,
        rules_config: Optional[Dict[str, Any]] = None,
        scope: str = "all",
    ) -> None:
        """Initializes the safety visitor.

        Args:
            rel_path: Relative path to the file being analyzed.
            rules_config: Optional configuration for audit rules and severities.
            scope: Analysis scope.
        """
        super().__init__(rel_path, rules_config, scope)
        self.connections: Set[str] = set()
        self.disconnections: Set[str] = set()
        self.in_ui_handler = False
        self.has_qgs_task = False

        # Heuristics for UI-bound methods in QGIS plugins
        self.ui_handlers = {"run", "initGui", "unload", "moveEvent", "resizeEvent", "showEvent"}

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Tracks if we are inside a UI-critical handler."""
        # Store state for this function's subtree
        # Note: CompositeVisitor will visit children and then call leave_FunctionDef
        self._old_ui_handler = self.in_ui_handler
        self._old_has_task = self.has_qgs_task

        self.in_ui_handler = node.name in self.ui_handlers or node.name.endswith("Event")
        self.has_qgs_task = False  # Reset for this function

        # Check if function body uses QgsTask (we still use walk here as a shorthand)
        for sub_node in ast.walk(node):
            if isinstance(sub_node, ast.Name) and sub_node.id == "QgsTask":
                self.has_qgs_task = True
                break
            if isinstance(sub_node, ast.Attribute) and sub_node.attr == "fromFunction":
                self.has_qgs_task = True  # Common QgsTask.fromFunction
                break

        self.generic_visit(node)

    def leave_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Restores state after visiting function children."""
        self.in_ui_handler = self._old_ui_handler
        self.has_qgs_task = self._old_has_task

    def visit_Call(self, node: ast.Call) -> None:
        """Detects signal connections and disconnections."""
        func_name = self._get_full_attribute_name(node.func)

        if func_name.endswith(".connect"):
            # Try to identify the signal name (e.g. self.iface.mapCanvas().xyCoordinates)
            signal = func_name.rsplit(".connect", 1)[0]
            self.connections.add(signal)

        elif func_name.endswith(".disconnect"):
            signal = func_name.rsplit(".disconnect", 1)[0]
            self.disconnections.add(signal)

        # UI Blocking checks
        if self.in_ui_handler and not self.has_qgs_task:
            if func_name.endswith(".getFeatures") or func_name == "requests.get":
                # We are calling a potentially slow op inside a UI handler without QgsTask
                pass  # Will be flagged if inside a loop
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        """Checks for intensive loops in UI handlers."""
        self._check_blocking_loop(node)
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        """Checks for intensive loops in UI handlers."""
        self._check_blocking_loop(node)
        self.generic_visit(node)

    def _check_blocking_loop(self, node: ast.AST) -> None:
        """Heuristic to detect if a loop is 'intensive' and UI-blocking."""
        if not self.in_ui_handler or self.has_qgs_task:
            return

        is_intensive = False
        for sub_node in ast.walk(node):
            if isinstance(sub_node, ast.Call):
                name = self._get_full_attribute_name(sub_node.func)
                # Operations that suggest large data processing or latency
                if any(x in name for x in (".getFeatures", ".request", "sleep", "exec_")):
                    is_intensive = True
                    break

        if is_intensive:
            self._report_issue(
                "UI_BLOCKING_LOOP",
                getattr(node, "lineno", 0),
                "Intensive loop detected in UI handler without QgsTask. This may freeze QGIS.",
                ast.unparse(node).split("\n")[0] + " ...",
            )

    def _get_full_attribute_name(self, node: ast.AST) -> str:
        """Helper to extract full attribute path (e.g. self.layer.getFeatures)."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return f"{self._get_full_attribute_name(node.value)}.{node.attr}"
        return ""

    @property
    def signal_leaks(self) -> List[str]:
        """Returns signals that are connected but never disconnected."""
        return sorted(list(self.connections - self.disconnections))
