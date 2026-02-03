"""AST visitor for QGIS-specific standards and best practices."""

import ast
from typing import Any, Dict, List, Optional, Set

from ..rules.qgis_rules import I18N_METHODS
from .base import BaseVisitor


class StandardsVisitor(BaseVisitor):
    """Visitor focused on QGIS-specific standards and best practices.

    Detects issues like:
    - Missing i18n translations
    - Missing signal slots
    - Mandatory cleanup methods
    - Obsolete API usage
    - Blocking network calls in UI
    - Spatial index optimization opportunities
    - Non-pythonic loops
    """

    def __init__(self, rel_path: str, rules_config: Optional[Dict[str, Any]] = None) -> None:
        """Initializes the standards visitor.

        Args:
            rel_path: Relative path to the file being analyzed.
            rules_config: Optional configuration for audit rules and severities.
        """
        super().__init__(rel_path, rules_config)
        self.class_methods_stack: List[Set[str]] = []
        self.i18n_methods = I18N_METHODS

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Analyzes class definitions.

        Args:
            node: The class definition AST node.
        """
        methods = {
            item.name
            for item in node.body
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        self.class_methods_stack.append(methods)

        # MANDATORY_CLEANUP
        has_init_gui = "initGui" in methods
        has_unload = "unload" in methods

        if has_init_gui and not has_unload:
            self._report_issue(
                "MANDATORY_CLEANUP",
                node.lineno,
                f"Class '{node.name}' implements 'initGui()' but is missing 'unload()'.",
                f"class {node.name}...",
            )

        self.generic_visit(node)
        self.class_methods_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Analyzes function definitions.

        Args:
            node: The function definition AST node.
        """
        # IFACE_AS_ARGUMENT
        for arg in node.args.args:
            if arg.annotation and isinstance(arg.annotation, ast.Name):
                if arg.annotation.id == "QgisInterface":
                    self._report_issue(
                        "IFACE_AS_ARGUMENT",
                        node.lineno,
                        f"Function '{node.name}' receives 'QgisInterface' as an argument. Use the global 'iface' or Singleton pattern.",
                        ast.unparse(node).split("\n")[0],
                    )

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Analyzes function calls.

        Args:
            node: The call AST node.
        """
        self._check_obsolete_api(node)
        self._check_missing_i18n(node)
        self._check_missing_slot(node)
        self._check_unsafe_subprocess(node)
        self._check_blocking_network(node)
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        """Analyzes loop nodes.

        Args:
            node: The for-loop AST node.
        """
        # SPATIAL_INDEX check
        if (
            isinstance(node.iter, ast.Call)
            and isinstance(node.iter.func, ast.Attribute)
            and node.iter.func.attr == "getFeatures"
        ):
            warn = False
            if not node.iter.args:
                warn = True
            elif len(node.iter.args) == 1:
                arg = node.iter.args[0]
                if (
                    isinstance(arg, ast.Call)
                    and isinstance(arg.func, ast.Name)
                    and arg.func.id == "QgsFeatureRequest"
                ):
                    if not arg.args and not arg.keywords:
                        warn = True

            if warn:
                self._report_issue(
                    "SPATIAL_INDEX",
                    node.lineno,
                    "Iteration over features with getFeatures() and no filter.",
                    ast.unparse(node.iter),
                )

        # NON_PYTHONIC_LOOP
        for body_node in ast.walk(node):
            if isinstance(body_node, ast.AugAssign) and isinstance(body_node.op, ast.Add):
                if (
                    isinstance(body_node.target, ast.Name)
                    and isinstance(body_node.value, ast.Constant)
                    and body_node.value.value == 1
                ):
                    self._report_issue(
                        "NON_PYTHONIC_LOOP",
                        body_node.lineno,
                        f"Manual counter '{body_node.target.id} += 1' detected inside loop.",
                        ast.unparse(body_node),
                    )

        self.generic_visit(node)

    def _check_obsolete_api(self, node: ast.Call) -> None:
        """Checks for obsolete API usage.

        Args:
            node: The call AST node.
        """
        if isinstance(node.func, ast.Attribute) and node.func.attr == "writeAsVectorFormat":
            self._report_issue(
                "OBSOLETE_API",
                node.lineno,
                "Obsolete writeAsVectorFormat() usage. Use writeAsVectorFormatV3().",
                ast.unparse(node),
            )

    def _check_missing_i18n(self, node: ast.Call) -> None:
        """Checks for missing i18n translations.

        Args:
            node: The call AST node.
        """
        if isinstance(node.func, ast.Attribute) and node.func.attr in self.i18n_methods:
            if (
                node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
            ):
                val = node.args[0].value
                if val.strip() and not val.startswith("%"):
                    self._report_issue(
                        "MISSING_I18N",
                        node.lineno,
                        f"Untranslated UI text string in '{node.func.attr}': '{val}'. Use self.tr().",
                        ast.unparse(node),
                    )

    def _check_missing_slot(self, node: ast.Call) -> None:
        """Checks for potentially missing signal slots.

        Args:
            node: The call AST node.
        """
        if isinstance(node.func, ast.Attribute) and node.func.attr == "connect" and node.args:
            arg = node.args[0]
            if (
                isinstance(arg, ast.Attribute)
                and isinstance(arg.value, ast.Name)
                and arg.value.id == "self"
            ):
                slot = arg.attr
                if self.class_methods_stack and slot not in self.class_methods_stack[-1]:
                    self._report_issue(
                        "POTENTIAL_MISSING_SLOT",
                        node.lineno,
                        f"Connected slot 'self.{slot}' not found in class definitions.",
                    )

    def _check_unsafe_subprocess(self, node: ast.Call) -> None:
        """Checks for unsafe subprocess usage.

        Args:
            node: The call AST node.
        """
        is_subprocess = False
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            if node.func.value.id == "subprocess" and node.func.attr in {
                "run",
                "call",
                "Popen",
                "check_call",
                "check_output",
            }:
                is_subprocess = True

        if not is_subprocess:
            return

        shell_true = False
        for kw in node.keywords:
            if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                shell_true = True
                break

        if shell_true:
            self._report_issue(
                "UNSAFE_SUBPROCESS",
                node.lineno,
                "Subprocess called with 'shell=True'.",
                ast.unparse(node),
            )
            return

        if node.args:
            cmd_arg = node.args[0]
            if isinstance(cmd_arg, (ast.JoinedStr, ast.BinOp)):
                self._report_issue(
                    "UNSAFE_SUBPROCESS",
                    node.lineno,
                    "Possible unquoted variable injection.",
                    ast.unparse(node),
                )

    def _check_blocking_network(self, node: ast.Call) -> None:
        """Checks for blocking network calls in UI files.

        Args:
            node: The call AST node.
        """
        is_network = False
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            if node.func.value.id == "requests" and node.func.attr in {
                "get",
                "post",
                "put",
                "delete",
                "patch",
            }:
                is_network = True

        if not is_network:
            # Heuristic for urlopen
            attr_chain = []
            curr = node.func
            while isinstance(curr, ast.Attribute):
                attr_chain.append(curr.attr)
                curr = curr.value
            if isinstance(curr, ast.Name):
                attr_chain.append(curr.id)
            if attr_chain == ["urlopen", "request", "urllib"]:
                is_network = True

        if is_network:
            is_ui_file = any(
                kw in self.rel_path.lower() for kw in ["gui", "ui", "dialog", "widget"]
            )
            if is_ui_file:
                self._report_issue(
                    "BLOCKING_NETWORK_CALL",
                    node.lineno,
                    "Synchronous network call detected in UI file.",
                    ast.unparse(node),
                )
