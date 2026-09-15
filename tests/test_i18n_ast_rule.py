"""Synthetic tests for the portable AST i18n rule (Fase 4).

These tests exercise the AST-based MISSING_I18N detection through the
CompositeVisitor, covering technical string patterns, multiline docstrings,
inline exclusions, and per-project configuration.
"""

import ast
import unittest

from analyzer.visitors.composite_visitor import CompositeVisitor


def _issues(code: str, rules_config=None) -> list:
    """Parse code and return the MISSING_I18N issues."""
    tree = ast.parse(code)
    visitor = CompositeVisitor(
        "test.py",
        rules_config=rules_config,
        scope="i18n",
        lines=code.splitlines(),
    )
    visitor.visit(tree)
    return [i for i in visitor.issues if i["type"] == "MISSING_I18N"]


class TestI18nAstRule(unittest.TestCase):
    """Synthetic coverage for the portable AST i18n rule."""

    def test_technical_strings_ignored(self):
        code = """
x = ".png"
y = "*.shp"
z = "#FF0000"
f = "field=name:string"
css = "QPushButton { color: red; }"
tag = "<br>"
fmt = "{:.2f}"
"""
        issues = _issues(code)
        self.assertEqual(issues, [], f"Technical strings should be ignored: {issues}")

    def test_format_string_chain_ignored(self):
        code = 'label = "Found {} items".format(count)'
        issues = _issues(code)
        self.assertEqual(issues, [], f"Format chain should be ignored: {issues}")

    def test_multiline_docstring_ignored(self):
        code = '''
def foo():
    """Line one of the docstring.
    Line two that looks user facing.
    """
    return "Real user string"
'''
        issues = _issues(code)
        self.assertEqual(len(issues), 1, f"Expected only the return string: {issues}")
        self.assertIn("Real user string", issues[0]["message"])

    def test_inline_no_i18n_ignored(self):
        code = 'x = "Skipped user string"  # no-i18n'
        issues = _issues(code)
        self.assertEqual(issues, [], f"# no-i18n should suppress: {issues}")

    def test_inline_noqa_ignored(self):
        code = 'x = "Skipped user string"  # noqa'
        issues = _issues(code)
        self.assertEqual(issues, [], f"# noqa should suppress: {issues}")

    def test_config_extra_exact_ignores(self):
        rules_config = {"MISSING_I18N": {"extra_exact_ignores": ["Custom Ignored"]}}
        code = 'x = "Custom Ignored"'
        issues = _issues(code, rules_config=rules_config)
        self.assertEqual(issues, [], f"extra_exact_ignores should suppress: {issues}")

    def test_config_extra_ignore_calls(self):
        rules_config = {"MISSING_I18N": {"extra_ignore_calls": ["customSetLabel"]}}
        code = 'customSetLabel("Some user text")'
        issues = _issues(code, rules_config=rules_config)
        self.assertEqual(issues, [], f"extra_ignore_calls should suppress: {issues}")

    def test_user_facing_string_flagged(self):
        code = 'label = "Please enter your name:"'
        issues = _issues(code)
        self.assertEqual(len(issues), 1, f"User-facing string should be flagged: {issues}")


if __name__ == "__main__":
    unittest.main()
