"""AST visitor for Qt6 migration rules (parity with flake8-qgis QGS4xx)."""

import ast
from typing import Any

from .base import BaseVisitor

# Name/class tokens removed or replaced in Qt6.
# Maps rule id -> (token, message).
QT6_REMOVED_NAMES: dict[str, tuple[str, str]] = {
    "QT6_QAPP_USAGE": (
        "qApp",
        "[QGS401] qApp was removed in Qt6. Use QApplication.instance().",
    ),
    "QT6_QREGEXP_USAGE": (
        "QRegExp",
        "[QGS406] QRegExp was removed in Qt6. Use QRegularExpression.",
    ),
    "QT6_QDESKTOPWIDGET": (
        "QDesktopWidget",
        "[QGS407] QDesktopWidget was removed in Qt6.",
    ),
}

# Enums removed/renamed in Qt6, referenced as ``Qt.<attr>``.
# Maps old attribute -> replacement.
QT6_REMOVED_ENUMS: dict[str, str] = {
    "MidButton": "Qt.MouseButton.MiddleButton",
    "WindowContextHelpButtonHint": "Qt.WindowType.WindowContextHelpButtonHint",
    "WA_NoBackground": "Qt.WidgetAttribute.WA_NoSystemBackground",
    "TextDate": "Qt.DateFormat.ISODate",
}

# Import suffixes that indicate compiled resources (removed in PyQt6).
_RESOURCE_SUFFIX = "_rc"


class QtTransitionVisitor(BaseVisitor):
    """Visitor for Qt6 migration / transition patterns.

    Detects APIs removed or renamed in Qt6, providing parity with the
    ``QGS4xx`` rules from flake8-qgis:

    - ``qApp``, ``QRegExp``, ``QDesktopWidget`` usage
    - Removed Qt enums (e.g. ``Qt.MidButton``)
    - ``QFontMetrics.width()``
    - ``QComboBox.activated[str]``
    - Compiled resource imports (``*_rc``)
    - ``addAction(...)`` with multiple arguments
    - ``QVariant()`` / ``QVariant(QVariant.Null)``
    - Legacy ``QDateTime(...)`` constructor signatures
    """

    def __init__(
        self,
        rel_path: str,
        rules_config: dict[str, Any] | None = None,
        scope: str = "all",
    ) -> None:
        """Initializes the Qt6 transition visitor.

        Args:
            rel_path: Relative path to the file being analyzed.
            rules_config: Optional configuration for audit rules and severities.
            scope: Analysis scope.
        """
        super().__init__(rel_path, rules_config, scope)
        self._qfontmetrics_seen = False

    def visit_Name(self, node: ast.Name) -> None:
        """Flags removed Qt6 names referenced as identifiers."""
        for rule_id, (token, message) in QT6_REMOVED_NAMES.items():
            if node.id == token:
                self._report_issue(rule_id, node.lineno, message, node.id)
        if node.id == "QFontMetrics":
            self._qfontmetrics_seen = True
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """Flags imports of removed Qt6 names and compiled resources."""
        for alias in node.names:
            self._check_removed_import(alias.name, node.lineno)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Flags from-imports of removed Qt6 names and compiled resources."""
        for alias in node.names:
            self._check_removed_import(alias.name, node.lineno)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Flags removed Qt6 enums referenced as attributes."""
        if node.attr in QT6_REMOVED_ENUMS and self._is_qt_base(node.value):
            replacement = QT6_REMOVED_ENUMS[node.attr]
            self._report_issue(
                "QT6_REMOVED_ENUM",
                node.lineno,
                f"[QGS403] Qt.{node.attr} was removed in Qt6. Use {replacement}.",
                ast.unparse(node),
            )
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        """Flags QComboBox.activated[str] usage."""
        if isinstance(node.value, ast.Attribute) and node.value.attr == "activated":
            self._report_issue(
                "QT6_QCOMBOBOX_ACTIVATED",
                node.lineno,
                "[QGS405] QComboBox.activated[str] was removed in Qt6. "
                "Use QComboBox.textActivated.",
                ast.unparse(node),
            )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Flags removed Qt6 constructor and method call signatures."""
        self._check_qfontmetrics_width(node)
        self._check_add_action_multiarg(node)
        self._check_qvariant_null(node)
        self._check_qdatetime_signatures(node)
        self.generic_visit(node)

    # --- Helpers ---

    def _check_removed_import(self, name: str, lineno: int) -> None:
        """Checks an imported name for removed Qt6 tokens or compiled resources."""
        if "QFontMetrics" in name:
            self._qfontmetrics_seen = True

        for rule_id, (token, message) in QT6_REMOVED_NAMES.items():
            if name == token or name.endswith(f".{token}"):
                self._report_issue(rule_id, lineno, message, f"import {name}")
                return

        if name.endswith(_RESOURCE_SUFFIX):
            self._report_issue(
                "QT6_COMPILED_RESOURCES",
                lineno,
                "[QGS408] Compiled resource imports were removed in PyQt6. "
                "Load resources by file path.",
                f"import {name}",
            )

    def _check_qfontmetrics_width(self, node: ast.Call) -> None:
        """Flags QFontMetrics.width() usage in files that use QFontMetrics."""
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "width"
            and self._qfontmetrics_seen
        ):
            self._report_issue(
                "QT6_QFONTMETRICS_WIDTH",
                node.lineno,
                "[QGS404] QFontMetrics.width() was removed in Qt6. "
                "Use QFontMetrics.horizontalAdvance().",
                ast.unparse(node),
            )

    def _check_add_action_multiarg(self, node: ast.Call) -> None:
        """Flags addAction() calls with multiple positional arguments."""
        if isinstance(node.func, ast.Attribute) and node.func.attr == "addAction":
            if len(node.args) >= 2:
                self._report_issue(
                    "QT6_ADDACTION_MULTIARG",
                    node.lineno,
                    "[QGS409] addAction() with multiple arguments was removed in Qt6. "
                    "Create a QAction and call addAction(action).",
                    ast.unparse(node),
                )

    def _check_qvariant_null(self, node: ast.Call) -> None:
        """Flags QVariant() / QVariant(QVariant.Null) usage."""
        if not (isinstance(node.func, ast.Name) and node.func.id == "QVariant"):
            return

        is_null = len(node.args) == 0
        if len(node.args) == 1 and isinstance(node.args[0], ast.Attribute):
            is_null = node.args[0].attr == "Null"

        if is_null:
            self._report_issue(
                "QT6_QVARIANT_NULL",
                node.lineno,
                "[QGS410] Use NULL instead of QVariant().",
                ast.unparse(node),
            )

    def _check_qdatetime_signatures(self, node: ast.Call) -> None:
        """Flags legacy QDateTime constructor signatures."""
        if not (isinstance(node.func, ast.Name) and node.func.id == "QDateTime"):
            return

        if len(node.args) == 8:
            self._report_issue(
                "QT6_QDATETIME_ARGS",
                node.lineno,
                "[QGS411] QDateTime(yyyy, mm, dd, hh, MM, ss, ms, ts) no longer "
                "works in Qt6. Use QDateTime(QDate(...), QTime(...)).",
                ast.unparse(node),
            )
        elif len(node.args) == 1 and isinstance(node.args[0], ast.Call):
            if isinstance(node.args[0].func, ast.Name) and node.args[0].func.id == "QDate":
                self._report_issue(
                    "QT6_QDATETIME_QDATE",
                    node.lineno,
                    "[QGS412] QDateTime(QDate(...)) no longer works in Qt6. "
                    "Use QDateTime(QDate(...), QTime(0, 0, 0)).",
                    ast.unparse(node),
                )

    @staticmethod
    def _is_qt_base(node: ast.AST) -> bool:
        """Returns True if the node is a Qt namespace reference (``Qt``/``Qt.*``)."""
        if isinstance(node, ast.Name):
            return node.id == "Qt" or node.id.startswith("Qt.")
        if isinstance(node, ast.Attribute):
            return node.attr.startswith("Qt")
        return False
