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

"""Module for scanning and auditing QGIS plugin Python files.

This module provides functionalities to analyze individual Python modules using AST,
check for security vulnerabilities, and audit against QGIS coding standards.
"""

import ast
import pathlib
from typing import Any, Dict, List, Optional, TypedDict

from .rules.qgis_rules import get_qgis_audit_rules
from .secrets import SecretScanner
from .utils.ast_utils import (
    calculate_module_complexity,
    check_main_guard,
    extract_classes_from_ast,
    extract_functions_from_ast,
    extract_imports_from_ast,
)
from .visitors import QGISASTVisitor, QGISSecurityVisitor

# --- Types ---


class ResearchMetrics(TypedDict):
    """Structured research metrics for a module."""

    docstring_styles: List[str]
    type_hint_stats: Dict[str, Any]
    docstring_stats: Dict[str, Any]
    qgis_context: Dict[str, Any]
    security_findings_count: int


class ModuleAnalysisResult(TypedDict, total=False):
    """Formal structure for module analysis results."""

    path: str
    lines: int
    functions: List[Dict[str, Any]]
    classes: List[str]
    imports: List[str]
    complexity: int
    has_main: bool
    docstrings: Dict[str, bool]
    file_size_kb: float
    syntax_error: bool
    ast_issues: List[Dict[str, Any]]
    security_issues: List[Dict[str, Any]]
    resource_usages: List[str]
    research_metrics: ResearchMetrics
    content: Optional[str]


# --- Constants ---

SEVERITY_MAP = {
    "error": "high",
    "warning": "medium",
    "info": "low",
}


# --- Shared Worker Context ---

_worker_context: Optional[Dict[str, Any]] = None


def init_worker(context: Dict[str, Any]) -> None:
    """Initializes the worker process with shared context.

    Args:
        context: Shared data (e.g., rules_config, project_path).
    """
    global _worker_context
    _worker_context = context


def analyze_module_worker(
    py_file: pathlib.Path,
    project_path: Optional[pathlib.Path] = None,
    cached_data: Optional[Dict[str, Any]] = None,
    rules_config: Optional[Dict[str, Any]] = None,
) -> Optional[ModuleAnalysisResult]:
    """Worker function for module analysis, intended for parallel execution.

    Args:
        py_file: Path to the Python file to analyze.
        project_path: Root path of the project. If missing, uses shared context.
        cached_data: Optional previously cached analysis results.
        rules_config: Optional rule configuration overrides. If missing, uses shared context.

    Returns:
        A dictionary containing the analysis results, or None if the file
        could not be processed.
    """
    try:
        # Use shared context if available to reduce per-call serialization overhead
        ctx = _worker_context or {}
        p_path = project_path or ctx.get("project_path")
        r_config = rules_config or ctx.get("rules_config")

        if not p_path:
            return None

        rel_path = _get_relative_path(py_file, p_path)
        content = _read_file_content(py_file)
        if not content:
            return None

        # Parse AST with error handling
        tree_or_error = _parse_ast(content, rel_path, py_file)
        if isinstance(tree_or_error, dict) and tree_or_error.get("syntax_error"):
            # Ensure it fits the return type
            return tree_or_error  # type: ignore

        tree = tree_or_error

        # Run Audits (using the new CompositeVisitor for single-pass)
        visitor = QGISASTVisitor(rel_path, rules_config=r_config)
        visitor.visit(tree)

        # Extract information using helper functions
        results: ModuleAnalysisResult = {
            "path": rel_path,
            "lines": content.count("\n") + 1,
            "functions": extract_functions_from_ast(tree),
            "classes": extract_classes_from_ast(tree),
            "imports": extract_imports_from_ast(tree),
            "complexity": calculate_module_complexity(tree),
            "has_main": check_main_guard(tree),
            "docstrings": {"module": ast.get_docstring(tree) is not None},
            "file_size_kb": py_file.stat().st_size / 1024,
            "syntax_error": False,
            "content": content,
        }

        security_issues = _collect_security_issues(tree, content, rel_path)
        results.update(
            {
                "ast_issues": visitor.issues,
                "security_issues": security_issues,
                "resource_usages": getattr(visitor, "resource_usages", []),
                "research_metrics": {
                    "docstring_styles": list(set(visitor.docstring_styles)),
                    "type_hint_stats": visitor.type_hint_stats,
                    "docstring_stats": visitor.docstring_stats,
                    "qgis_context": visitor.qgis_context,
                    "security_findings_count": len(security_issues),
                },
            }
        )

        return results
    except Exception:
        return None


def _get_relative_path(py_file: pathlib.Path, project_path: pathlib.Path) -> str:
    """Safely calculates the relative path of a file."""
    if project_path.is_file():
        return py_file.name
    return str(py_file.relative_to(project_path))


def _read_file_content(py_file: pathlib.Path) -> Optional[str]:
    """Reads file content handling common encoding issues."""
    try:
        with open(py_file, encoding="utf-8-sig", errors="replace") as f:
            return f.read()
    except Exception:
        return None


def _parse_ast(content: str, rel_path: str, py_file: pathlib.Path) -> Any:
    """Parses AST or returns a structured error dictionary."""
    try:
        return ast.parse(content)
    except SyntaxError:
        return _create_empty_analysis_result(rel_path, py_file, content, syntax_error=True)


def _create_empty_analysis_result(
    rel_path: str, py_file: pathlib.Path, content: str, syntax_error: bool = False
) -> ModuleAnalysisResult:
    """Creates a basic results structure for errors or empty files."""
    return {
        "path": rel_path,
        "lines": content.count("\n") + 1,
        "syntax_error": syntax_error,
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
            "qgis_context": {
                "processing_framework": False,
                "gdal_style": "Modern",
                "pyqt_transition": {"PyQt5": [], "PyQt6": []},
                "legacy_signals_count": 0,
            },
            "security_findings_count": 0,
        },
    }


def _collect_security_issues(tree: ast.AST, content: str, rel_path: str) -> List[Dict[str, Any]]:
    """Consolidates issues from AST security visitor and secret scanner."""
    security_visitor = QGISSecurityVisitor(rel_path)
    security_visitor.visit(tree)
    issues = security_visitor.findings

    secret_scanner = SecretScanner()
    for sf in secret_scanner.scan_text(content):
        issues.append(
            {
                "file": rel_path,
                "line": sf.line,
                "type": sf.type,
                "severity": "high" if sf.confidence == "HIGH" else "medium",
                "message": sf.message,
                "confidence": sf.confidence.lower(),
            }
        )
    return issues


def audit_qgis_standards(
    modules_data: List[ModuleAnalysisResult],
    project_path: pathlib.Path,
    rules_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Executes a comprehensive QGIS standards audit using regex and AST results."""
    rules = get_qgis_audit_rules()
    results: Dict[str, Any] = {"issues": [], "issues_count": 0}

    for module in modules_data:
        # Add AST issues
        results["issues"].extend(module.get("ast_issues", []))

        # Run Regex rules
        path = module.get("path", "")
        content = module.get("content") or _try_read_module_file(path, project_path)

        if content:
            _run_regex_audit_on_module(content, path, rules, rules_config, results["issues"])

    results["issues_count"] = len(results["issues"])
    return results


def _run_regex_audit_on_module(
    content: str,
    path: str,
    rules: List[Dict[str, Any]],
    rules_config: Optional[Dict[str, Any]],
    issues_out: List[Dict[str, Any]],
) -> None:
    """Runs all regex rules on a module's content."""
    for rule in rules:
        internal_severity = _get_rule_severity(rule, rules_config)
        if internal_severity == "ignore":
            continue

        for match in rule["pattern"].finditer(content):
            line_no = content.count("\n", 0, match.start()) + 1
            issues_out.append(
                {
                    "file": path,
                    "line": line_no,
                    "type": rule["id"],
                    "severity": internal_severity,
                    "message": rule["message"],
                    "code": content[match.start() : match.end() + 20].strip(),
                }
            )


def _try_read_module_file(path: Optional[str], project_path: pathlib.Path) -> Optional[str]:
    """Attempts to read a module file from path if content is missing."""
    if not path:
        return None
    full_path = project_path / path
    if full_path.exists():
        return _read_file_content(full_path)
    return None


def _get_rule_severity(rule: Dict[str, Any], config: Optional[Dict[str, Any]]) -> str:
    """Calculates rule severity based on configuration."""
    rule_id = rule["id"]
    severity_val = config.get(rule_id, "warning") if config else "warning"

    if severity_val == "ignore":
        return "ignore"

    severity = SEVERITY_MAP.get(severity_val, rule["severity"])
    return str(severity)


# End of scanner.py
