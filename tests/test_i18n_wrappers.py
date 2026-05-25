"""Tests for i18n wrapper recognition: QCoreApplication.translate() and self.tr()."""

import ast
import unittest

from analyzer.visitors.composite_visitor import CompositeVisitor


def _get_i18n_issues(code: str) -> list:
    """Parse code with CompositeVisitor and return MISSING_I18N issues."""
    tree = ast.parse(code)
    visitor = CompositeVisitor("test_wrappers.py", scope="i18n")
    visitor.visit(tree)
    return [i for i in visitor.issues if i["type"] == "MISSING_I18N"]


def _get_i18n_strings(issues: list) -> list:
    """Extract the string values from MISSING_I18N issue messages."""
    result = []
    for issue in issues:
        msg = issue["message"]
        # Format: "Untranslated user-facing string: 'VALUE'. Use ..."
        start = msg.find("'") + 1
        end = msg.find("'", start)
        if start > 0 and end > start:
            result.append(msg[start:end])
    return result


class TestI18nWrappers(unittest.TestCase):
    """Verify i18n wrapper functions are recognized and skip false positives."""

    # --- self.tr() tests (should produce zero MISSING_I18N) ---

    def test_self_tr_alone(self):
        """self.tr('My Dialog') should NOT be flagged."""
        code = """
class MyDialog:
    def __init__(self):
        self.setWindowTitle(self.tr("My Dialog"))
"""
        issues = _get_i18n_issues(code)
        self.assertEqual(issues, [], f"self.tr() should not flag: {issues}")

    # --- QCoreApplication.translate() tests ---

    def test_translate_in_static_method(self):
        """QCoreApplication.translate() in @staticmethod should NOT be flagged."""
        code = """
class Reporter:
    @staticmethod
    def format():
        return QCoreApplication.translate("Reporter", "No data available")
"""
        issues = _get_i18n_issues(code)
        self.assertEqual(issues, [], f"translate() in static method should not flag: {issues}")

    def test_translate_in_super_init(self):
        """QCoreApplication.translate() in super().__init__() should NOT be flagged."""
        code = """
class MyPage(BasePage):
    def __init__(self, parent=None):
        super().__init__(
            QCoreApplication.translate("MyPage", "My Page Title"), parent)
"""
        issues = _get_i18n_issues(code)
        self.assertEqual(issues, [], f"translate() in super().__init__ should not flag: {issues}")

    def test_translate_in_non_qobject(self):
        """QCoreApplication.translate() in non-QObject class should NOT be flagged."""
        code = """
class LayerFactory:
    def create(self):
        layer.setName(QCoreApplication.translate("LayerFactory", "My Layer"))
"""
        issues = _get_i18n_issues(code)
        self.assertEqual(issues, [], f"translate() in non-QObject should not flag: {issues}")

    def test_translate_with_format_chain(self):
        """QCoreApplication.translate(...).format(...) should NOT be flagged."""
        code = """
label = QCoreApplication.translate("Ctx", "Found {} items").format(count)
"""
        issues = _get_i18n_issues(code)
        self.assertEqual(issues, [], f"translate().format() should not flag: {issues}")

    # --- Unwrapped strings should still be flagged ---

    def test_unwrapped_user_string_still_flagged(self):
        """User-facing string without i18n wrapper should still be caught."""
        code = """
class BadWidget:
    def __init__(self):
        self.label = "Please enter your name:"
"""
        issues = _get_i18n_issues(code)
        strings = _get_i18n_strings(issues)
        self.assertIn("Please enter your name:", strings)

    def test_unwrapped_in_normal_function_still_flagged(self):
        """String inside a non-i18n call should still be flagged."""
        code = """
label = setText("Hello World")
"""
        issues = _get_i18n_issues(code)
        strings = _get_i18n_strings(issues)
        self.assertIn("Hello World", strings)

    # --- Nested cases ---

    def test_translate_wrapper_inside_other_call(self):
        """translate() inside another call should NOT flag the wrapped string."""
        code = """
result = process(QCoreApplication.translate("Ctx", "User Message"))
"""
        issues = _get_i18n_issues(code)
        self.assertEqual(issues, [], f"Nested translate() should not flag: {issues}")

    def test_nested_helper_inside_translate(self):
        """Strings in helper calls inside translate() are part of the translation
        pipeline and should NOT be flagged."""
        code = """
label = QCoreApplication.translate("Ctx", format_value("Hello World"))
"""
        issues = _get_i18n_issues(code)
        self.assertEqual(
            issues, [],
            "Strings inside translate() helpers are still in the translation pipeline",
        )

    # --- Short strings and context names ---

    def test_short_context_name_not_flagged(self):
        """Short context names like 'Ctx' should not be flagged anyway (heuristic)."""
        code = """
label = QCoreApplication.translate("Ctx", "Save")
"""
        issues = _get_i18n_issues(code)
        # "Ctx" would fail is_translatable_string (no space, len 3, but no space/punct and
        # not all lowercase and not all uppercase... actually "Ctx" has uppercase C,
        # so is_translatable_string returns False). "Save" would fail
        # (len 4 < 5, no space/punct). Both should be skipped.
        self.assertEqual(issues, [], f"Short strings in translate() should not flag: {issues}")

    # --- Direct visitor edge case: _in_i18n_wrapper must reset between calls ---

    def test_wrapper_state_resets_between_calls(self):
        """After leaving a translate() call, unwrapped strings should be flagged again."""
        code = """
x = QCoreApplication.translate("X", "Hello World")
y = "Forgotten translation"
"""
        issues = _get_i18n_issues(code)
        strings = _get_i18n_strings(issues)
        self.assertIn("Forgotten translation", strings,
                       "String after translate() should still be flagged")
        self.assertNotIn("Hello World", strings,
                          "String inside translate() should NOT be flagged")


if __name__ == "__main__":
    unittest.main()
