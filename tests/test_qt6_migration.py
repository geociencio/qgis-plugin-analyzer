"""Tests for the Qt6 migration rules (QGS4xx parity)."""

import ast
import unittest

from analyzer.visitors.composite_visitor import CompositeVisitor


def _qt6_issues(code: str) -> list:
    """Parse code and return the Qt6 migration issues (QT6_* types)."""
    tree = ast.parse(code)
    visitor = CompositeVisitor("test_qt6.py", scope="architecture")
    visitor.visit(tree)
    return [i for i in visitor.issues if i["type"].startswith("QT6_")]


class TestQt6Migration(unittest.TestCase):
    """Coverage for the Qt6 migration / transition rules."""

    def test_qapp_flagged(self):
        code = "qApp.processEvents()"
        issues = _qt6_issues(code)
        self.assertEqual([i["type"] for i in issues], ["QT6_QAPP_USAGE"])

    def test_qregexp_flagged(self):
        issues = _qt6_issues("re = QRegExp('foo')")
        self.assertEqual([i["type"] for i in issues], ["QT6_QREGEXP_USAGE"])

    def test_qregexp_import_flagged(self):
        issues = _qt6_issues("from qgis.PyQt.QtCore import QRegExp")
        self.assertIn("QT6_QREGEXP_USAGE", [i["type"] for i in issues])

    def test_qregularexpression_ok(self):
        issues = _qt6_issues("re = QRegularExpression('foo')")
        self.assertEqual([i for i in issues if i["type"] == "QT6_QREGEXP_USAGE"], [])

    def test_qdesktopwidget_flagged(self):
        issues = _qt6_issues("w = QDesktopWidget()")
        self.assertEqual([i["type"] for i in issues], ["QT6_QDESKTOPWIDGET"])

    def test_removed_enum_flagged(self):
        issues = _qt6_issues("x = Qt.MidButton")
        self.assertEqual([i["type"] for i in issues], ["QT6_REMOVED_ENUM"])

    def test_modern_enum_ok(self):
        issues = _qt6_issues("x = Qt.MouseButton.MiddleButton")
        self.assertEqual([i for i in issues if i["type"] == "QT6_REMOVED_ENUM"], [])

    def test_qfontmetrics_width_flagged(self):
        code = "from qgis.PyQt.QtGui import QFontMetrics\nw = fm.width('x')"
        issues = _qt6_issues(code)
        self.assertIn("QT6_QFONTMETRICS_WIDTH", [i["type"] for i in issues])

    def test_qcombobox_activated_flagged(self):
        issues = _qt6_issues("combo.activated[str].connect(self.handler)")
        self.assertIn("QT6_QCOMBOBOX_ACTIVATED", [i["type"] for i in issues])

    def test_compiled_resources_flagged(self):
        issues = _qt6_issues("import resources_rc")
        self.assertIn("QT6_COMPILED_RESOURCES", [i["type"] for i in issues])

    def test_add_action_multiarg_flagged(self):
        issues = _qt6_issues("menu.addAction('foo', self.cb, 'Ctrl+F')")
        self.assertIn("QT6_ADDACTION_MULTIARG", [i["type"] for i in issues])

    def test_add_action_single_ok(self):
        issues = _qt6_issues("menu.addAction(action)")
        self.assertEqual([i for i in issues if i["type"] == "QT6_ADDACTION_MULTIARG"], [])

    def test_qvariant_null_flagged(self):
        issues = _qt6_issues("x = QVariant()")
        self.assertIn("QT6_QVARIANT_NULL", [i["type"] for i in issues])

    def test_qvariant_null_explicit_flagged(self):
        issues = _qt6_issues("x = QVariant(QVariant.Null)")
        self.assertIn("QT6_QVARIANT_NULL", [i["type"] for i in issues])

    def test_qdatetime_8args_flagged(self):
        code = "dt = QDateTime(2026, 1, 26, 0, 0, 0, 0, 0)"
        issues = _qt6_issues(code)
        self.assertIn("QT6_QDATETIME_ARGS", [i["type"] for i in issues])

    def test_qdatetime_qdate_flagged(self):
        code = "dt = QDateTime(QDate(2026, 1, 26))"
        issues = _qt6_issues(code)
        self.assertIn("QT6_QDATETIME_QDATE", [i["type"] for i in issues])

    def test_string_literals_not_flagged(self):
        code = 'msg = "qApp QRegExp QDesktopWidget"'
        issues = _qt6_issues(code)
        self.assertEqual(issues, [], f"String literals must not be flagged: {issues}")


if __name__ == "__main__":
    unittest.main()
