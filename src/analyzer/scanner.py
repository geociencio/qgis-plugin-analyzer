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
from typing import Any, Dict, List, Optional

from .rules.qgis_rules import get_qgis_audit_rules
from .utils.ast_utils import (
    calculate_module_complexity,
    check_main_guard,
    extract_classes_from_ast,
    extract_functions_from_ast,
    extract_imports_from_ast,
)
from .visitors import QGISASTVisitor


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
    results: Dict[str, Any] = {"issues": [], "issues_count": 0}

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
