# /***************************************************************************
#  QGIS Plugin Analyzer
#                                  A QGIS tool
#  Static code analysis and standards audit for QGIS plugins.
#                               -------------------
#         begin                : 2025-12-28
#         git sha              : $Format:%H$
#         copyright            : (C) 2025 by Juan M Bernales
#         email                : juanbernales@gmail.com
#  ***************************************************************************/
#
# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

import ast
import pathlib
import re
from typing import Any, Dict, List, Optional

from .rules.qgis_rules import I18N_METHODS, get_qgis_audit_rules
from .utils.ast_utils import (
    calculate_complexity,
    calculate_module_complexity,
    check_main_guard,
    extract_classes_from_ast,
    extract_functions_from_ast,
    extract_imports_from_ast,
)


class QGISASTVisitor(ast.NodeVisitor):
    """AST visitor to detect QGIS-specific issues."""

    def __init__(self, rel_path: str, rules_config: Optional[Dict[str, Any]] = None) -> None:
        """Initializes the AST visitor for a specific file.

        Args:
            rel_path: Relative path to the file being analyzed.
            rules_config: Optional configuration for audit rules and severities.
        """
        self.rel_path = rel_path
        self.issues = []
        self.rules_config = rules_config or {}
        self.class_methods_stack = []

        # New metrics for research-based scoring
        self.docstring_styles = []  # List of detected styles (Google, NumPy)
        self.type_hint_stats = {
            "total_parameters": 0,
            "annotated_parameters": 0,
            "has_return_hint": 0,
            "total_functions": 0,
        }
        self.docstring_stats = {"total_public_items": 0, "has_docstring": 0}
        self.i18n_methods = I18N_METHODS

    def _check_docstring_style(self, doc: Optional[str]) -> None:
        """Identifies Google or NumPy docstring styles within a string.

        Args:
            doc: The docstring content to analyze.
        """
        if not doc:
            return
        # Google: Args: or Returns: or Raises: as headers
        if re.search(r"\n\s*(Args|Returns|Raises|Yields):\s*\n", doc):
            self.docstring_styles.append("Google")
        # NumPy: Underlined headers
        elif re.search(r"\n(Parameters|Returns|Raises|Yields)\n\s*-{3,}", doc):
            self.docstring_styles.append("NumPy")

    def visit_Module(self, node: ast.Module) -> None:
        """Analyzes a module-level AST node for docstrings and other metrics.

        Args:
            node: The module node to analyze.
        """
        doc = ast.get_docstring(node)
        self.docstring_stats["total_public_items"] += 1
        if doc:
            self.docstring_stats["has_docstring"] += 1
            self._check_docstring_style(doc)
        elif self._should_report("MISSING_DOCSTRING"):
            self.issues.append(
                {
                    "file": self.rel_path,
                    "line": 1,
                    "type": "MISSING_DOCSTRING",
                    "severity": self._get_severity("MISSING_DOCSTRING"),
                    "message": "Module is missing a docstring (PEP 257).",
                    "code": "Module: " + self.rel_path,
                }
            )
        self.generic_visit(node)

    def _should_report(self, rule_id: str) -> bool:
        """Check if rule should be reported based on config."""
        severity = self.rules_config.get(rule_id, "warning")
        return severity != "ignore"

    def _get_severity(self, rule_id: str) -> str:
        """Get configured severity for rule (maps to 'high', 'medium', 'low')."""
        config_severity = self.rules_config.get(rule_id, "warning")
        # Map config severity to internal severity
        severity_map = {
            "error": "high",
            "warning": "medium",
            "info": "low",
        }
        return severity_map.get(config_severity, "medium")

    def _check_obsolete_api(self, node: ast.Call) -> None:
        """Detects usage of obsolete QGIS APIs.

        Args:
            node: The function call node to analyze.
        """
        if isinstance(node.func, ast.Attribute) and node.func.attr == "writeAsVectorFormat":
            if self._should_report("OBSOLETE_API"):
                self.issues.append(
                    {
                        "file": self.rel_path,
                        "line": node.lineno,
                        "type": "OBSOLETE_API",
                        "severity": self._get_severity("OBSOLETE_API"),
                        "message": "Obsolete writeAsVectorFormat() usage. Use writeAsVectorFormatV3().",
                        "code": ast.unparse(node),
                    }
                )

    def _check_missing_i18n(self, node: ast.Call) -> None:
        """Detects untranslated UI strings in common PyQGIS methods.

        Args:
            node: The function call node to analyze.
        """
        if isinstance(node.func, ast.Attribute) and node.func.attr in self.i18n_methods:
            if (
                node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
            ):
                val = node.args[0].value
                if val.strip() and not val.startswith("%"):
                    if self._should_report("MISSING_I18N"):
                        self.issues.append(
                            {
                                "file": self.rel_path,
                                "line": node.lineno,
                                "type": "MISSING_I18N",
                                "severity": self._get_severity("MISSING_I18N"),
                                "message": f"Untranslated UI text string in '{node.func.attr}': '{val}'. Use self.tr().",
                                "code": ast.unparse(node),
                            }
                        )

    def _check_missing_slot(self, node: ast.Call) -> None:
        """Heuristically detects potentially missing signal slots in signal connections.

        Args:
            node: The function call node to analyze.
        """
        if isinstance(node.func, ast.Attribute) and node.func.attr == "connect":
            if node.args:
                arg = node.args[0]
                if (
                    isinstance(arg, ast.Attribute)
                    and isinstance(arg.value, ast.Name)
                    and arg.value.id == "self"
                ):
                    slot = arg.attr
                    if self.class_methods_stack:
                        current_methods = self.class_methods_stack[-1]
                        if slot not in current_methods:
                            if self._should_report("POTENTIAL_MISSING_SLOT"):
                                self.issues.append(
                                    {
                                        "file": self.rel_path,
                                        "line": node.lineno,
                                        "type": "POTENTIAL_MISSING_SLOT",
                                        "severity": self._get_severity("POTENTIAL_MISSING_SLOT"),
                                        "message": f"Connected slot 'self.{slot}' not found in class definitions. Verify it is defined or inherited.",
                                    }
                                )

    def _check_unsafe_subprocess(self, node: ast.Call) -> None:
        """Detects potentially unsafe subprocess usage.

        Args:
            node: The function call node to analyze.
        """
        # Targets: subprocess.run, call, Popen, check_call, check_output
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

        # 1. Check for shell=True
        shell_true = False
        for kw in node.keywords:
            if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                shell_true = True
                break

        if shell_true:
            if self._should_report("UNSAFE_SUBPROCESS"):
                self.issues.append(
                    {
                        "file": self.rel_path,
                        "line": node.lineno,
                        "type": "UNSAFE_SUBPROCESS",
                        "severity": self._get_severity("UNSAFE_SUBPROCESS"),
                        "message": "Subprocess called with 'shell=True'. This is a security risk if input is unsanitized.",
                        "code": ast.unparse(node),
                    }
                )
            return

        # 2. Check for unquoted variable interpolation in the command string (heuristic)
        # If the first argument is a string (not a list) and contains % or {} or f-string
        if node.args:
            cmd_arg = node.args[0]
            if isinstance(cmd_arg, (ast.JoinedStr, ast.BinOp)):
                if self._should_report("UNSAFE_SUBPROCESS"):
                    self.issues.append(
                        {
                            "file": self.rel_path,
                            "line": node.lineno,
                            "type": "UNSAFE_SUBPROCESS",
                            "severity": self._get_severity("UNSAFE_SUBPROCESS"),
                            "message": "Possible unquoted variable injection in subprocess command. Use a list of arguments instead.",
                            "code": ast.unparse(node),
                        }
                    )

    def _check_blocking_network(self, node: ast.Call) -> None:
        """Detects synchronous network calls in UI-related files.

        Args:
            node: The function call node to analyze.
        """
        is_network = False
        # requests.get/post...
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            if node.func.value.id == "requests" and node.func.attr in {
                "get",
                "post",
                "put",
                "delete",
                "patch",
            }:
                is_network = True

        # urllib.request.urlopen (can be deep)
        # Note: urllib.request.urlopen(...) or urlopen(...) if from urllib.request import urlopen
        # current AST logic check: urllib.request.urlopen
        if not is_network:
            attr_chain = []
            curr = node.func
            while isinstance(curr, ast.Attribute):
                attr_chain.append(curr.attr)
                curr = curr.value
            if isinstance(curr, ast.Name):
                attr_chain.append(curr.id)

            # Chain is reversed: ['urlopen', 'request', 'urllib']
            if attr_chain == ["urlopen", "request", "urllib"]:
                is_network = True
            elif attr_chain == ["urlopen"] and isinstance(node.func, ast.Name) and node.func.id == "urlopen":
                # This would need tracking imports, but let's stick to full path for now as per plan
                # Or check if it's just 'urlopen'
                is_network = True

        if not is_network:
            return

        # Check if it's a UI/GUI file
        is_ui_file = any(kw in self.rel_path.lower() for kw in ["gui", "ui", "dialog", "widget"])

        if is_ui_file:
            if self._should_report("BLOCKING_NETWORK_CALL"):
                self.issues.append(
                    {
                        "file": self.rel_path,
                        "line": node.lineno,
                        "type": "BLOCKING_NETWORK_CALL",
                        "severity": self._get_severity("BLOCKING_NETWORK_CALL"),
                        "message": "Synchronous network call detected in UI file. This will freeze QGIS. Use QgsTask or QNetworkAccessManager.",
                        "code": ast.unparse(node),
                    }
                )

    def visit_Call(self, node: ast.Call) -> None:
        """Analyzes function call nodes for multiple QGIS-specific rules.

        Args:
            node: The call node to analyze.
        """
        self._check_obsolete_api(node)
        self._check_missing_i18n(node)
        self._check_missing_slot(node)
        self._check_unsafe_subprocess(node)
        self._check_blocking_network(node)
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        """Analyzes loop nodes for performance (spatial indexing) and Pythonic patterns.

        Args:
            node: The loop node to analyze.
        """
        # Detect SPATIAL_INDEX (Looping features without filter)
        # Check if iterating over .getFeatures()
        if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Attribute):
            if node.iter.func.attr == "getFeatures":
                # If getFeatures() has no arguments or is passed QgsFeatureRequest() with no filter,
                # it's potentially heavy.
                warn = False
                if not node.iter.args:
                    warn = True
                elif len(node.iter.args) == 1:
                    arg = node.iter.args[0]
                    # Check if it's a blank QgsFeatureRequest()
                    if (
                        isinstance(arg, ast.Call)
                        and isinstance(arg.func, ast.Name)
                        and arg.func.id == "QgsFeatureRequest"
                    ):
                        if not arg.args and not arg.keywords:
                            warn = True

                if warn and self._should_report("SPATIAL_INDEX"):
                    self.issues.append(
                        {
                            "file": self.rel_path,
                            "line": node.lineno,
                            "type": "SPATIAL_INDEX",
                            "severity": self._get_severity("SPATIAL_INDEX"),
                            "message": "Iteration over features with getFeatures() and no filter. Use a spatial index and QgsFeatureRequest for large layers.",
                            "code": ast.unparse(node.iter),
                        }
                    )

        # Non-Pythonic Loop Detection (check for manual counters like i += 1)
        for body_node in ast.walk(node):
            if isinstance(body_node, ast.AugAssign) and isinstance(body_node.op, ast.Add):
                if isinstance(body_node.target, ast.Name):
                    if isinstance(body_node.value, ast.Constant) and body_node.value.value == 1:
                        if self._should_report("NON_PYTHONIC_LOOP"):
                            self.issues.append(
                                {
                                    "file": self.rel_path,
                                    "line": body_node.lineno,
                                    "type": "NON_PYTHONIC_LOOP",
                                    "severity": self._get_severity("NON_PYTHONIC_LOOP"),
                                    "message": f"Manual counter '{body_node.target.id} += 1' detected inside loop. Use enumerate() instead.",
                                    "code": ast.unparse(body_node),
                                }
                            )

        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Analyzes class definitions for mandatory methods and documentation.

        Args:
            node: The class definition node to analyze.
        """
        # Track methods defined in the current class context
        methods = {
            item.name
            for item in node.body
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        self.class_methods_stack.append(methods)

        # 3. Detect MANDATORY_CLEANUP
        # Simple check: if a class has initGui, it MUST have unload
        has_init_gui = any(
            isinstance(m, ast.FunctionDef) and m.name == "initGui" for m in node.body
        )
        has_unload = any(isinstance(m, ast.FunctionDef) and m.name == "unload" for m in node.body)

        if has_init_gui and not has_unload:
            if self._should_report("MANDATORY_CLEANUP"):
                self.issues.append(
                    {
                        "file": self.rel_path,
                        "line": node.lineno,
                        "type": "MANDATORY_CLEANUP",
                        "severity": self._get_severity("MANDATORY_CLEANUP"),
                        "message": f"Class '{node.name}' implements 'initGui()' but is missing 'unload()'. Mandatory for cleanup.",
                        "code": f"class {node.name}...",
                    }
                )

        # Research recommendation: Missing Docstring for Classes
        if not node.name.startswith("_"):
            doc = ast.get_docstring(node)
            self.docstring_stats["total_public_items"] += 1
            if doc:
                self.docstring_stats["has_docstring"] += 1
                self._check_docstring_style(doc)
            elif self._should_report("MISSING_DOCSTRING"):
                self.issues.append(
                    {
                        "file": self.rel_path,
                        "line": node.lineno,
                        "type": "MISSING_DOCSTRING",
                        "severity": self._get_severity("MISSING_DOCSTRING"),
                        "message": f"Public class '{node.name}' is missing a docstring.",
                        "code": f"class {node.name}...",
                    }
                )

        self.generic_visit(node)
        self.class_methods_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Analyzes function definitions for best practices and research-based metrics.

        Args:
            node: The function definition node to analyze.
        """
        # 4. Detect IFACE_AS_ARGUMENT (QGS105)
        # Avoid passing QgisInterface as an argument
        for arg in node.args.args:
            if arg.annotation and isinstance(arg.annotation, ast.Name):
                if arg.annotation.id == "QgisInterface":
                    if self._should_report("IFACE_AS_ARGUMENT"):
                        self.issues.append(
                            {
                                "file": self.rel_path,
                                "line": node.lineno,
                                "type": "IFACE_AS_ARGUMENT",
                                "severity": self._get_severity("IFACE_AS_ARGUMENT"),
                                "message": f"Function '{node.name}' receives 'QgisInterface' as an argument. Use the global 'iface' or Singleton pattern.",
                                "code": ast.unparse(node).split("\n")[0],
                            }
                        )

        # 5. Detect HIGH_COMPLEXITY
        complexity = calculate_complexity(node)
        if complexity > 15:
            if self._should_report("HIGH_COMPLEXITY"):
                self.issues.append(
                    {
                        "file": self.rel_path,
                        "line": node.lineno,
                        "type": "HIGH_COMPLEXITY",
                        "severity": self._get_severity("HIGH_COMPLEXITY"),
                        "message": f"Function '{node.name}' is too complex (CC={complexity} > 15). Consider extracting methods to improve maintainability.",
                        "code": f"def {node.name}...",
                    }
                )

        # Research recommendation: Missing Docstring and Type Hints
        if not node.name.startswith("_") and node.name != "__init__":
            doc = ast.get_docstring(node)
            self.docstring_stats["total_public_items"] += 1
            if doc:
                self.docstring_stats["has_docstring"] += 1
                self._check_docstring_style(doc)
            elif self._should_report("MISSING_DOCSTRING"):
                self.issues.append(
                    {
                        "file": self.rel_path,
                        "line": node.lineno,
                        "type": "MISSING_DOCSTRING",
                        "severity": self._get_severity("MISSING_DOCSTRING"),
                        "message": f"Public function '{node.name}' is missing a docstring.",
                        "code": f"def {node.name}...",
                    }
                )

        # Type Hint Stats (PEP 484)
        if node.name != "__init__":
            self.type_hint_stats["total_functions"] += 1
            params = [a for a in node.args.args if a.arg != "self" and a.arg != "cls"]
            self.type_hint_stats["total_parameters"] += len(params)
            annotated = [a for a in params if a.annotation]
            self.type_hint_stats["annotated_parameters"] += len(annotated)
            if node.returns:
                self.type_hint_stats["has_return_hint"] += 1

            # Rule: MISSING_TYPE_HINTS (if zero hints in a function with params)
            if params and not annotated and not node.returns:
                if self._should_report("MISSING_TYPE_HINTS"):
                    self.issues.append(
                        {
                            "file": self.rel_path,
                            "line": node.lineno,
                            "type": "MISSING_TYPE_HINTS",
                            "severity": self._get_severity("MISSING_TYPE_HINTS"),
                            "message": f"Function '{node.name}' has no type annotations.",
                            "code": f"def {node.name}...",
                        }
                    )

        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """Analyzes import nodes for protected members, legacy PyQt, and GDAL usage.

        Args:
            node: The import node to analyze.
        """
        for alias in node.names:
            # 5. Detect QGIS_PROTECTED_MEMBER (QGS101/102)
            if alias.name.startswith("qgis._") and not alias.name.startswith("qgis._3d"):
                if self._should_report("QGIS_PROTECTED_MEMBER"):
                    self.issues.append(
                        {
                            "file": self.rel_path,
                            "line": node.lineno,
                            "type": "QGIS_PROTECTED_MEMBER",
                            "severity": self._get_severity("QGIS_PROTECTED_MEMBER"),
                            "message": f"Protected member import detected: '{alias.name}'. Protected members are unstable.",
                            "code": ast.unparse(node),
                        }
                    )
            # 6. Detect GDAL_DIRECT_IMPORT (QGS106)
            if alias.name == "gdal":
                if self._should_report("GDAL_DIRECT_IMPORT"):
                    self.issues.append(
                        {
                            "file": self.rel_path,
                            "line": node.lineno,
                            "type": "GDAL_DIRECT_IMPORT",
                            "severity": self._get_severity("GDAL_DIRECT_IMPORT"),
                            "message": "Direct 'gdal' import detected. Use 'from osgeo import gdal'.",
                            "code": ast.unparse(node),
                        }
                    )
            # QGIS_LEGACY_IMPORT (already existing)
            if alias.name.startswith(("PyQt4", "PyQt5")):
                if self._should_report("QGIS_LEGACY_IMPORT"):
                    self.issues.append(
                        {
                            "file": self.rel_path,
                            "line": node.lineno,
                            "type": "QGIS_LEGACY_IMPORT",
                            "severity": self._get_severity("QGIS_LEGACY_IMPORT"),
                            "message": f"Legacy import detected: '{alias.name}'. Use 'qgis.PyQt' for compatibility.",
                            "code": ast.unparse(node),
                        }
                    )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Analyzes 'from import' nodes for protected members, legacy PyQt, and GDAL.

        Also detects heavy dependencies in UI-related files.

        Args:
            node: The import-from node to analyze.
        """
        if node.module:
            # Detect QGIS_PROTECTED_MEMBER
            if node.module.startswith("qgis._") and not node.module.startswith("qgis._3d"):
                if self._should_report("QGIS_PROTECTED_MEMBER"):
                    self.issues.append(
                        {
                            "file": self.rel_path,
                            "line": node.lineno,
                            "type": "QGIS_PROTECTED_MEMBER",
                            "severity": self._get_severity("QGIS_PROTECTED_MEMBER"),
                            "message": f"Protected member import detected: 'from {node.module} import ...'. Protected members are unstable.",
                            "code": ast.unparse(node),
                        }
                    )
            # Detect GDAL_DIRECT_IMPORT
            if node.module == "gdal":
                if self._should_report("GDAL_DIRECT_IMPORT"):
                    self.issues.append(
                        {
                            "file": self.rel_path,
                            "line": node.lineno,
                            "type": "GDAL_DIRECT_IMPORT",
                            "severity": self._get_severity("GDAL_DIRECT_IMPORT"),
                            "message": "Direct 'gdal' import detected. Use 'from osgeo import gdal'.",
                            "code": ast.unparse(node),
                        }
                    )
            # QGIS_LEGACY_IMPORT
            if node.module.startswith(("PyQt4", "PyQt5")):
                if self._should_report("QGIS_LEGACY_IMPORT"):
                    self.issues.append(
                        {
                            "file": self.rel_path,
                            "line": node.lineno,
                            "type": "QGIS_LEGACY_IMPORT",
                            "severity": self._get_severity("QGIS_LEGACY_IMPORT"),
                            "message": f"Legacy import detected: 'from {node.module} import ...'. Use 'qgis.PyQt' for compatibility.",
                            "code": ast.unparse(node),
                        }
                    )
            # 7. Detect HEAVY_LOGIC_UI (QGS107)
            heavy_libs = {"pandas", "numpy", "scipy", "sklearn", "matplotlib"}
            is_ui_file = "gui" in self.rel_path.lower() or "ui" in self.rel_path.lower()
            if is_ui_file and (
                node.module in heavy_libs or node.module.split(".")[0] in heavy_libs
            ):
                if self._should_report("HEAVY_LOGIC_UI"):
                    self.issues.append(
                        {
                            "file": self.rel_path,
                            "line": node.lineno,
                            "type": "HEAVY_LOGIC_UI",
                            "severity": self._get_severity("HEAVY_LOGIC_UI"),
                            "message": f"Heavy dependency '{node.module}' detected in UI file. Move logic to core.",
                            "code": ast.unparse(node),
                        }
                    )
        self.generic_visit(node)


# The helper functions previously here have been moved to src/analyzer/utils/ast_utils.py


def analyze_module_worker(
    py_file: pathlib.Path,
    project_path: pathlib.Path,
    cached_data: Optional[Dict[str, Any]] = None,
    rules_config: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """Worker function for module analysis, intended for parallel execution.

    Args:
        py_file: Path to the Python file to analyze.
        project_path: Root path of the project.
        cached_data: Optional previously cached analysis results.
        rules_config: Optional rule configuration overrides.

    Returns:
        A dictionary containing the analysis results, or None if the file
        could not be processed.
    """
    try:
        rel_path = str(py_file.relative_to(project_path))

        # Fast read
        with open(py_file, encoding="utf-8-sig", errors="replace") as f:
            content = f.read()

        if not content:
            return None

        # Parse AST
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return {
                "path": rel_path,
                "lines": content.count("\n") + 1,
                "syntax_error": True,
                "file_size_kb": py_file.stat().st_size / 1024,
                "complexity": 1,
                "functions": [],
                "classes": [],
                "imports": [],
                "has_main": False,
                "docstrings": {"module": False},
                "ast_issues": [],
                "research_metrics": {
                    "docstring_styles": [],
                    "type_hint_stats": {
                        "total_parameters": 0,
                        "annotated_parameters": 0,
                        "has_return_hint": 0,
                        "total_functions": 0,
                    },
                    "docstring_stats": {"total_public_items": 0, "has_docstring": 0},
                },
            }

        # Extract information using helper functions
        functions = extract_functions_from_ast(tree)
        classes = extract_classes_from_ast(tree)
        imports = extract_imports_from_ast(tree)
        module_complexity = calculate_module_complexity(tree)
        has_main = check_main_guard(tree)

        # Custom AST Audit
        visitor = QGISASTVisitor(rel_path, rules_config=rules_config)
        visitor.visit(tree)

        return {
            "path": rel_path,
            "lines": content.count("\n") + 1,
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "complexity": module_complexity,
            "has_main": has_main,
            "docstrings": {
                "module": ast.get_docstring(tree) is not None,
            },
            "file_size_kb": py_file.stat().st_size / 1024,
            "syntax_error": False,
            "ast_issues": visitor.issues,
            "resource_usages": getattr(visitor, "resource_usages", []),
            "research_metrics": {
                "docstring_styles": list(set(visitor.docstring_styles)),
                "type_hint_stats": visitor.type_hint_stats,
                "docstring_stats": visitor.docstring_stats,
            },
            "content": content,
        }
    except Exception:
        return None


def audit_qgis_standards(
    modules_data: List[Dict[str, Any]],
    project_path: pathlib.Path,
    rules_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Executes a comprehensive QGIS standards audit using regex and AST results.

    Args:
        modules_data: List of already analyzed module data.
        project_path: Root path of the project.
        rules_config: Optional rule configuration overrides.

    Returns:
        A dictionary consolidating all detected issues and the total issue count.
    """
    rules = get_qgis_audit_rules()
    results = {"issues": [], "issues_count": 0}

    for module in modules_data:
        # Add issues found via AST
        if "ast_issues" in module:
            results["issues"].extend(module["ast_issues"])

        # Use cached content if available
        path = module.get("path")
        content = module.get("content")

        if content is None and path:
            full_path = project_path / path
            if full_path.exists():
                try:
                    content = full_path.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    continue

        if content is None:
            continue

        for rule in rules:
            rule_id = rule["id"]
            severity_val = rules_config.get(rule_id, "warning") if rules_config else "warning"
            if severity_val == "ignore":
                continue

            # Map config severity to internal severity
            severity_map = {"error": "high", "warning": "medium", "info": "low"}
            internal_severity = severity_map.get(severity_val, rule["severity"])

            for match in rule["pattern"].finditer(content):
                line_no = content.count("\n", 0, match.start()) + 1
                results["issues"].append(
                    {
                        "file": path,
                        "line": line_no,
                        "type": rule["id"],
                        "severity": internal_severity,
                        "message": rule["message"],
                        "code": content[match.start() : match.end() + 20].strip(),
                    }
                )

    results["issues_count"] = len(results["issues"])
    return results


# End of scanner.py
