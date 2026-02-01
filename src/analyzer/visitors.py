"""AST Visitors for QGIS Plugin Analysis."""

import ast
import re
from typing import Any, Dict, List, Optional, Set

# Import to trigger registration of checks
from .rules.qgis_rules import I18N_METHODS
from .security_checker import SecurityContext, SecurityRegistry
from .utils.ast_utils import calculate_complexity


class QGISASTVisitor(ast.NodeVisitor):
    """AST visitor to detect QGIS-specific issues."""

    def __init__(self, rel_path: str, rules_config: Optional[Dict[str, Any]] = None) -> None:
        """Initializes the AST visitor for a specific file.

        Args:
            rel_path: Relative path to the file being analyzed.
            rules_config: Optional configuration for audit rules and severities.
        """
        self.rel_path = rel_path
        self.issues: List[Dict[str, Any]] = []
        self.rules_config = rules_config or {}
        self.class_methods_stack: List[Set[str]] = []

        # New metrics for research-based scoring
        self.docstring_styles: List[str] = []
        self.type_hint_stats = {
            "total_parameters": 0,
            "annotated_parameters": 0,
            "has_return_hint": 0,
            "total_functions": 0,
        }
        self.docstring_stats = {"total_public_items": 0, "has_docstring": 0}
        self.i18n_methods = I18N_METHODS

    def _should_report(self, rule_id: str) -> bool:
        """Check if rule should be reported based on config."""
        severity = self.rules_config.get(rule_id, "warning")
        return bool(severity != "ignore")

    def _get_severity(self, rule_id: str) -> str:
        """Get configured severity for rule (maps to 'high', 'medium', 'low')."""
        config_severity = self.rules_config.get(rule_id, "warning")
        severity_map = {
            "error": "high",
            "warning": "medium",
            "info": "low",
        }
        return severity_map.get(config_severity, "medium")

    def _check_docstring_style(self, doc: Optional[str]) -> None:
        """Identifies Google or NumPy docstring styles within a string."""
        if not doc:
            return
        # Google: Args: or Returns: or Raises: as headers
        if re.search(r"\n\s*(Args|Returns|Raises|Yields):\s*\n", doc):
            self.docstring_styles.append("Google")
        # NumPy: Underlined headers
        elif re.search(r"\n(Parameters|Returns|Raises|Yields)\n\s*-{3,}", doc):
            self.docstring_styles.append("NumPy")

    def _report_issue(self, rule_id: str, line: int, message: str, code: str = "") -> None:
        """Helper to report an issue if enabled."""
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

    def visit_Module(self, node: ast.Module) -> None:
        """Analyzes a module-level AST node."""
        doc = ast.get_docstring(node)
        self.docstring_stats["total_public_items"] += 1
        if doc:
            self.docstring_stats["has_docstring"] += 1
            self._check_docstring_style(doc)
        else:
            self._report_issue(
                "MISSING_DOCSTRING",
                1,
                "Module is missing a docstring (PEP 257).",
                f"Module: {self.rel_path}",
            )
        self.generic_visit(node)

    def _check_import_name(self, name: str, node: ast.AST, code_snippet: str) -> None:
        """Checks a single import name for violations."""
        # 5. Detect QGIS_PROTECTED_MEMBER
        if name.startswith("qgis._") and not name.startswith("qgis._3d"):
            self._report_issue(
                "QGIS_PROTECTED_MEMBER",
                node.lineno,
                f"Protected member import detected: '{name}'. Protected members are unstable.",
                code_snippet,
            )

        # 6. Detect GDAL_DIRECT_IMPORT
        if name == "gdal":
            self._report_issue(
                "GDAL_DIRECT_IMPORT",
                node.lineno,
                "Direct 'gdal' import detected. Use 'from osgeo import gdal'.",
                code_snippet,
            )

        # Detect QGIS_LEGACY_IMPORT
        if name.startswith(("PyQt4", "PyQt5")):
            self._report_issue(
                "QGIS_LEGACY_IMPORT",
                node.lineno,
                f"Legacy import detected: '{name}'. Use 'qgis.PyQt' for compatibility.",
                code_snippet,
            )

    def visit_Import(self, node: ast.Import) -> None:
        """Analyzes import nodes."""
        for alias in node.names:
            self._check_import_name(alias.name, node, ast.unparse(node))
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Analyzes 'from import' nodes."""
        if node.module:
            self._check_import_name(node.module, node, ast.unparse(node))

            # 7. Detect HEAVY_LOGIC_UI
            heavy_libs = {"pandas", "numpy", "scipy", "sklearn", "matplotlib"}
            is_ui_file = "gui" in self.rel_path.lower() or "ui" in self.rel_path.lower()
            if is_ui_file and (
                node.module in heavy_libs or node.module.split(".")[0] in heavy_libs
            ):
                self._report_issue(
                    "HEAVY_LOGIC_UI",
                    node.lineno,
                    f"Heavy dependency '{node.module}' detected in UI file. Move logic to core.",
                    ast.unparse(node),
                )
        self.generic_visit(node)

    def _check_docstring_and_metrics(self, node: ast.FunctionDef) -> None:
        """Checks docstrings and collects metrics."""
        if not node.name.startswith("_") and node.name != "__init__":
            doc = ast.get_docstring(node)
            self.docstring_stats["total_public_items"] += 1
            if doc:
                self.docstring_stats["has_docstring"] += 1
                self._check_docstring_style(doc)
            else:
                self._report_issue(
                    "MISSING_DOCSTRING",
                    node.lineno,
                    f"Public function '{node.name}' is missing a docstring.",
                    f"def {node.name}...",
                )

    def _check_type_hints(self, node: ast.FunctionDef) -> None:
        """Checks for type hints."""
        if node.name == "__init__":
            return

        self.type_hint_stats["total_functions"] += 1
        params = [a for a in node.args.args if a.arg != "self" and a.arg != "cls"]
        self.type_hint_stats["total_parameters"] += len(params)
        annotated = [a for a in params if a.annotation]
        self.type_hint_stats["annotated_parameters"] += len(annotated)
        if node.returns:
            self.type_hint_stats["has_return_hint"] += 1

        if params and not annotated and not node.returns:
            self._report_issue(
                "MISSING_TYPE_HINTS",
                node.lineno,
                f"Function '{node.name}' has no type annotations.",
                f"def {node.name}...",
            )

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Analyzes function definitions."""
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

        # HIGH_COMPLEXITY
        complexity = calculate_complexity(node)
        if complexity > 15:
            self._report_issue(
                "HIGH_COMPLEXITY",
                node.lineno,
                f"Function '{node.name}' is too complex (CC={complexity} > 15). Consider extracting methods.",
                f"def {node.name}...",
            )

        self._check_docstring_and_metrics(node)
        self._check_type_hints(node)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Analyzes class definitions."""
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

        # Missing Docstring
        if not node.name.startswith("_"):
            doc = ast.get_docstring(node)
            self.docstring_stats["total_public_items"] += 1
            if doc:
                self.docstring_stats["has_docstring"] += 1
                self._check_docstring_style(doc)
            else:
                self._report_issue(
                    "MISSING_DOCSTRING",
                    node.lineno,
                    f"Public class '{node.name}' is missing a docstring.",
                    f"class {node.name}...",
                )

        self.generic_visit(node)
        self.class_methods_stack.pop()

    def visit_Call(self, node: ast.Call) -> None:
        """Analyzes function calls."""
        self._check_obsolete_api(node)
        self._check_missing_i18n(node)
        self._check_missing_slot(node)
        self._check_unsafe_subprocess(node)
        self._check_blocking_network(node)
        self.generic_visit(node)

    # ... Helper check methods (simplified) ...
    def _check_obsolete_api(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Attribute) and node.func.attr == "writeAsVectorFormat":
            self._report_issue(
                "OBSOLETE_API",
                node.lineno,
                "Obsolete writeAsVectorFormat() usage. Use writeAsVectorFormatV3().",
                ast.unparse(node),
            )

    def _check_missing_i18n(self, node: ast.Call) -> None:
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

    def visit_For(self, node: ast.For) -> None:
        """Analyzes loop nodes."""
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


class QGISSecurityVisitor(ast.NodeVisitor):
    """AST visitor focused on security vulnerabilities (Bandit-inspired)."""

    def __init__(self, rel_path: str):
        self.rel_path = rel_path
        self.findings: List[Dict[str, Any]] = []

    def visit(self, node: ast.AST):
        """Dispatches security checks for the current node."""
        checks = SecurityRegistry.get_checks_for_node(type(node))
        context = SecurityContext(node, self.rel_path)

        for check_func in checks:
            finding = check_func(context)
            if finding:
                self.findings.append(
                    {
                        "file": self.rel_path,
                        "line": finding.line,
                        "type": finding.id,
                        "severity": finding.severity.lower(),
                        "message": finding.message,
                        "code": finding.code_snippet,
                        "confidence": finding.confidence.lower()
                        if hasattr(finding, "confidence")
                        else "medium",
                    }
                )

        super().generic_visit(node)
