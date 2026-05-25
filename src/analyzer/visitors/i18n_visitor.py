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

"""AST visitor for internationalization (i18n) and translation standards."""

import ast
from typing import Any, Dict, Optional

from ..rules.qgis_rules import I18N_METHODS
from .base import BaseVisitor

# --- Constants ---

IGNORED_I18N_FUNCTIONS = {
    "debug",
    "info",
    "warning",
    "error",
    "critical",
    "log",
    "Exception",
    "ValueError",
    "TypeError",
    "RuntimeError",
    "setObjectName",
    "addItem",
    "setValue",
    "value",
    "key",
    "setProperty",
    "connect",
    "disconnect",
    "signal",
    "slot",
    "get",
    "post",
    "request",
    "arg",
    "group",
    "format",
    "join",
    "split",
    "replace",
}

# Recognized i18n wrapper functions. Strings passed as arguments to these
# calls are assumed to be already translated and are not flagged as
# MISSING_I18N. Covers:
#   - self.tr("...") / QObject.tr("...")
#   - QCoreApplication.translate("Context", "...")
#   - QObject.translate("Context", "...")
I18N_WRAPPER_FUNCTIONS = {"tr", "translate"}


class I18nVisitor(BaseVisitor):
    """Visitor focused on internationalization and missing translations.

    Detects:
    - Missing i18n translations in UI-facing strings.
    - Strings in assignments or calls that should be wrapped in tr()
      or QCoreApplication.translate().
    """

    def __init__(
        self,
        rel_path: str,
        rules_config: Optional[Dict[str, Any]] = None,
        scope: str = "all",
    ) -> None:
        """Initializes the i18n visitor.

        Args:
            rel_path: Relative path to the file being analyzed.
            rules_config: Optional configuration for audit rules and severities.
            scope: Analysis scope.
        """
        super().__init__(rel_path, rules_config, scope)
        self.i18n_methods = I18N_METHODS
        self._in_ignored_call = False
        self._in_i18n_wrapper = False

    def visit_Call(self, node: ast.Call) -> None:
        """Analyzes function calls for i18n-ignored context."""
        func_name = self._get_func_name(node.func)
        if func_name in IGNORED_I18N_FUNCTIONS:
            self._in_ignored_call = True
        if func_name in I18N_WRAPPER_FUNCTIONS:
            self._in_i18n_wrapper = True
        self.generic_visit(node)

    def leave_Call(self, node: ast.Call) -> None:
        """Resets ignored call state."""
        func_name = self._get_func_name(node.func)
        if func_name in IGNORED_I18N_FUNCTIONS:
            self._in_ignored_call = False
        if func_name in I18N_WRAPPER_FUNCTIONS:
            self._in_i18n_wrapper = False

    def visit_Constant(self, node: ast.Constant, parent: Optional[ast.AST] = None) -> None:
        """Analyzes string constants for missing translations."""
        # Skip strings that are already inside an i18n wrapper
        if self._in_i18n_wrapper:
            return

        # Ignore if inside ignored call or if it's a dict key or value
        is_dict_key = isinstance(parent, ast.Dict) and node in parent.keys
        is_dict_value = isinstance(parent, ast.Dict) and node in parent.values

        if (
            isinstance(node.value, str)
            and not self._in_ignored_call
            and not is_dict_key
            and not is_dict_value
        ):
            # Docstrings are strings directly under an Expr node.
            if isinstance(parent, ast.Expr):
                return

            self._check_potential_i18n_string(node.value, node.lineno)

    def _get_func_name(self, func: ast.expr) -> str:
        """Helper to get function name from a call."""
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute):
            return func.attr
        return ""

    def _check_potential_i18n_string(self, val: str, lineno: int) -> None:
        """Heuristic to detect strings that SHOULD be translated but aren't."""
        if not self.is_translatable_string(val):
            return

        self._report_issue(
            "MISSING_I18N",
            lineno,
            f"Untranslated user-facing string: '{val}'. "
            "Use self.tr() or QCoreApplication.translate().",
        )

    @staticmethod
    def is_translatable_string(value: str) -> bool:
        """Heuristic to determine if a string is user-facing."""
        if not value or len(value) < 3:
            return False

        # Ignore paths and technical patterns
        if "/" in value or "\\" in value or value.startswith(":/"):
            return False

        # If it contains spaces or ends with punctuation, it's very likely user-facing
        if " " in value or any(value.endswith(p) for p in ":.!?"):
            return True

        # TECHNICAL STRINGS: Ignore short strings that look like identifiers
        if len(value) <= 5:
            return False

        # Ignore snake_case, dotted names, CamelCase, and UPPERCASE
        if "_" in value or "." in value:
            return False
        if not value.islower() and not value.isupper() and any(c.isupper() for c in value):
            return False
        if value.isupper():
            return False

        # Technical words list
        technical_words = {
            "name",
            "type",
            "date",
            "color",
            "value",
            "label",
            "index",
            "field",
            "count",
            "total",
            "state",
            "status",
        }
        if value.lower() in technical_words:
            return False

        return True
