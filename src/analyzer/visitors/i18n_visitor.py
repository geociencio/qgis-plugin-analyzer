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

"""AST visitor for internationalization (i18n) and translation standards.

This visitor ports the portable AST-based i18n hygiene rule from
``scripts/upstream/i18n_ast_rule.py`` into the analyzer pipeline. It flags
hardcoded string literals that look user-facing but are not wrapped in a
translation call (``tr`` / ``translate``) and lack an inline ``# no-i18n``
exclusion.
"""

import ast
import re
from typing import Any, Dict, List, Optional, Set

from ..rules.qgis_rules import I18N_METHODS
from .base import BaseVisitor

# --- Constants ---

# Calls whose string arguments are safe to ignore (translations, logging, etc.).
DEFAULT_SAFE_CALL_SUFFIXES: Set[str] = {
    # Translation wrappers — already translated
    "tr",
    "translate",
    # Logging — not user-facing
    "debug",
    "info",
    "warning",
    "error",
    "critical",
    "exception",
    "log",
    # QGIS / Qt internals
    "connect",
    "disconnect",
    "mapLayerByName",
    "setValue",
    "setObjectName",
    "setProperty",
    "setToolTip",
    "setWhatsThis",
    "setPlaceholderText",
    "setAttribute",
    "setStyleSheet",
    "addItem",
    "insertItem",
    "findText",
    # Exception constructors — developer-facing
    "ValueError",
    "RuntimeError",
    "TypeError",
    "AttributeError",
    "KeyError",
    "NotImplementedError",
    "OSError",
    "IOError",
    "Exception",
    # Regular expression / path operations
    "compile",
    "match",
    "search",
    "sub",
    "split",
    "join",
    "format",
    "encode",
    "decode",
    "open",
    "makedirs",
    "startswith",
    "endswith",
    "with_suffix",
    "parent",
}

# Regex patterns for strings that are always technical (not user-facing).
DEFAULT_TECHNICAL_PATTERNS: List[re.Pattern[str]] = [
    # Python format specifiers
    re.compile(r"^[{.+<>^-]?\d*[dfsfeExXgGoO%nbDBcdnrsa]$"),  # e.g. '.2f', '+.2f'
    # File extensions
    re.compile(r"^\.[a-z]{2,4}$"),  # e.g. '.png', '.jpg', '.svg', '.shp'
    # MIME-style filter strings
    re.compile(r"\*\.\w+"),  # e.g. '*.png'
    # CSS / Qt stylesheet fragments
    re.compile(
        r"(background-color|border|font-weight|color:|margin|padding|QPush|QDialog|QLabel|QCombo)"
    ),
    # QGIS memory layer URI / field specs
    re.compile(r"field=\w+:\w+"),
    # Color codes (R,G,B or R,G,B,A)
    re.compile(r"^\d{1,3},\d{1,3},\d{1,3}(,\d{1,3})?$"),
    # SVG icon names
    re.compile(r"^m[A-Z][a-zA-Z]+\.svg$"),
    # Pure HTML tags (e.g. '<b>', '</b>', '<br>')
    re.compile(r"^</?[a-zA-Z][a-zA-Z0-9]*\s*/?>$"),
    # HTML attribute or fragment (contains '<' or '>' and no full readable word phrase)
    re.compile(r"^[^a-zA-Z]*<[^>]*>[^a-zA-Z]*$"),
    # Strings that are mostly HTML/special chars with minimal alpha
    re.compile(r"^[\s\|:;.,!?<>\-=\"'/\\{}()]+[a-zA-Z]{0,3}[\s\|:;.,!?<>\-=\"'/\\{}()]*$"),
    # Hex color codes
    re.compile(r"^#[0-9a-fA-F]{3,8}$"),
    # Geometry type keywords
    re.compile(r"^(Point|LineString|Polygon|MultiPoint|MultiLineString|MultiPolygon)$"),
    # Single-word QGIS layer types or geometry keywords
    re.compile(r"^(EPSG|WKT|CRS|SHP|CSV|GeoJSON|GPKG|GeoTIFF)$", re.IGNORECASE),
    # Format specifiers or pure punctuation/symbols
    re.compile(r"^[^a-zA-Z]*$"),
    # Log-level strings
    re.compile(r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$"),
    # QSettings keys (contain '/' or are camelCase)
    re.compile(r"^[a-zA-Z]+/[a-zA-Z/_]+$"),  # e.g. 'MyApp/last_dir'
    # Default filename values (just a filename, no spaces)
    re.compile(r"^\w[\w.-]*\.(png|jpg|jpeg|pdf|svg|shp|csv|json|html|txt|xml|qml)$"),
    # Pure numbers (including floats)
    re.compile(r"^-?\d+(\.\d+)?$"),
    # HTML attribute opening fragments (e.g. "<a href='", '<span style="')
    re.compile(r"^<[a-zA-Z]+\s+[a-zA-Z-]+=[\"']"),
]

# Exact strings that are always safe to ignore.
DEFAULT_SAFE_EXACT_STRINGS: Set[str] = {
    "utf-8",
    "r",
    "w",
    "rb",
    "wb",
    "a",
    "en",
    "es",
}


def collect_docstring_lines(tree: ast.AST) -> Set[int]:
    """Collect line numbers of all docstrings (module, class, function) via AST.

    Docstrings are the first string expression in a module, class body, or
    function body, possibly preceded by import statements (e.g. future imports).

    Args:
        tree: Parsed AST of the Python source file.

    Returns:
        Set of line numbers that belong to docstrings.
    """
    docstring_lines: Set[int] = set()

    def _find_first_str_expr(body: List[ast.stmt]) -> Optional[ast.Constant]:
        """Return the first string Constant Expr, skipping leading imports."""
        for stmt in body:
            if isinstance(stmt, (ast.Import, ast.ImportFrom)):
                continue
            if (
                isinstance(stmt, ast.Expr)
                and isinstance(stmt.value, ast.Constant)
                and isinstance(stmt.value.value, str)
            ):
                return stmt.value
            break
        return None

    for node in ast.walk(tree):
        docstring_node: Optional[ast.Constant] = None

        if isinstance(node, ast.Module):
            docstring_node = _find_first_str_expr(node.body)
        elif isinstance(node, (ast.ClassDef, ast.AsyncFunctionDef, ast.FunctionDef)):
            docstring_node = _find_first_str_expr(node.body)

        if docstring_node is not None:
            for lineno in range(
                docstring_node.lineno,
                (docstring_node.end_lineno or docstring_node.lineno) + 1,
            ):
                docstring_lines.add(lineno)

    return docstring_lines


def is_technical_string(val: str, patterns: List[re.Pattern[str]]) -> bool:
    """Return True if the string value is clearly technical/non-translatable.

    Args:
        val: String value to inspect.
        patterns: Regex patterns identifying technical strings.

    Returns:
        True if the string should be ignored as technical.
    """
    stripped = val.strip()

    for pattern in patterns:
        if pattern.search(stripped):
            return True

    return False


class I18nVisitor(BaseVisitor):
    """Visitor focused on internationalization and missing translations.

    Detects hardcoded user-facing strings that are not wrapped in ``tr()`` or
    ``QCoreApplication.translate()`` and lack an inline ``# no-i18n`` /
    ``# noqa`` exclusion.
    """

    def __init__(
        self,
        rel_path: str,
        rules_config: Optional[Dict[str, Any]] = None,
        scope: str = "all",
        lines: Optional[List[str]] = None,
    ) -> None:
        """Initializes the i18n visitor.

        Args:
            rel_path: Relative path to the file being analyzed.
            rules_config: Optional configuration for audit rules and severities.
            scope: Analysis scope.
            lines: Source lines of the file, used for inline ``# no-i18n`` /
                ``# noqa`` comment detection.
        """
        super().__init__(rel_path, rules_config, scope)
        self.i18n_methods = I18N_METHODS
        self.lines: List[str] = lines or []
        self.docstring_lines: Set[int] = set()
        self._current_call_stack: List[str] = []

        # Config-driven overrides for the MISSING_I18N rule.
        rule_cfg = self.rules_config.get("MISSING_I18N", {})
        if not isinstance(rule_cfg, dict):
            rule_cfg = {}
        self.safe_call_suffixes: Set[str] = set(DEFAULT_SAFE_CALL_SUFFIXES) | set(
            rule_cfg.get("extra_ignore_calls", [])
        )
        self.safe_exact_strings: Set[str] = set(DEFAULT_SAFE_EXACT_STRINGS) | set(
            rule_cfg.get("extra_exact_ignores", [])
        )
        self.technical_patterns: List[re.Pattern[str]] = DEFAULT_TECHNICAL_PATTERNS

    def visit_Call(self, node: ast.Call) -> None:
        """Tracks the current call stack to detect safe translation wrappers."""
        self._current_call_stack.append(self._get_call_name(node.func))

    def leave_Call(self, node: ast.Call) -> None:
        """Pops the current call stack when leaving a call."""
        if self._current_call_stack:
            self._current_call_stack.pop()

    def visit_Constant(self, node: ast.Constant, parent: Optional[ast.AST] = None) -> None:
        """Inspects string constants for i18n hygiene violations."""
        if not isinstance(node.value, str):
            return

        val = node.value.strip()

        # 1. Empty, very short, or numeric-only strings.
        if len(val) <= 1 or val.replace(".", "").replace("-", "").isdigit():
            return

        # 2. This line belongs to a docstring.
        if node.lineno in self.docstring_lines:
            return

        # 3. Exact safe strings.
        if val in self.safe_exact_strings:
            return

        # 4. Technical/non-translatable pattern match.
        if is_technical_string(val, self.technical_patterns):
            return

        # 5. String must look user-facing: contain a letter and either a space
        #    or trailing label punctuation (e.g. 'Name:', 'Save', 'Open...').
        has_spaces = " " in val
        has_alpha = any(c.isalpha() for c in val)
        if not has_alpha:
            return
        if not (has_spaces or val.endswith((":", ".", "!", "?"))):
            return

        # 6. Check if the string is inside a safe call wrapper.
        for active_call in reversed(self._current_call_stack):
            if any(active_call.endswith(suffix) for suffix in self.safe_call_suffixes):
                return

        # 7. Check for inline exclusion comments on the source line.
        line_num = node.lineno
        if 1 <= line_num <= len(self.lines):
            line_content = self.lines[line_num - 1]
            if "# no-i18n" in line_content or "# noqa" in line_content:
                return

        self._report_issue(
            "MISSING_I18N",
            node.lineno,
            f"Untranslated user-facing string: '{val}'. "
            "Use self.tr() or QCoreApplication.translate().",
        )

    @staticmethod
    def _get_call_name(func: ast.expr) -> str:
        """Resolves the qualified name of a function call node.

        Args:
            func: Call function expression.

        Returns:
            Dotted name (e.g. ``self.tr`` -> ``self.tr``), or empty string.
        """
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute):
            base = I18nVisitor._get_call_name(func.value)
            return f"{base}.{func.attr}" if base else func.attr
        return ""
