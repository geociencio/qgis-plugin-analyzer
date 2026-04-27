import ast
import unittest
from analyzer.visitors.composite_visitor import CompositeVisitor


class TestI18nStandards(unittest.TestCase):
    def test_i18n_excludes_docstrings(self):
        """Verify that docstrings are not flagged as missing translations."""
        code = """
def my_function():
    \"\"\"This is a docstring that shouldn't be translated.\"\"\"
    print("This is a user message that should be translated.")
"""
        tree = ast.parse(code)
        visitor = CompositeVisitor("test_file.py")
        visitor.visit(tree)

        # MISSING_DOCSTRING (from MetricsVisitor) and HIGH_COMPLEXITY etc might be present
        # but we care about MISSING_I18N
        i18n_issues = [i for i in visitor.issues if i["type"] == "MISSING_I18N"]

        # Should only find the user message
        messages = [i["message"] for i in i18n_issues]
        self.assertTrue(any("user message" in m for m in messages))
        self.assertFalse(any("docstring" in m for m in messages))
        self.assertEqual(len(i18n_issues), 1)

    def test_i18n_includes_user_facing_strings(self):
        """Verify that actual user-facing strings are still flagged."""
        code = """
class MyWidget:
    def __init__(self):
        self.label = "Name:"
"""
        tree = ast.parse(code)
        visitor = CompositeVisitor("test_file.py")
        visitor.visit(tree)

        i18n_issues = [i for i in visitor.issues if i["type"] == "MISSING_I18N"]
        self.assertEqual(len(i18n_issues), 1)
        self.assertIn("Name:", i18n_issues[0]["message"])


if __name__ == "__main__":
    unittest.main()
