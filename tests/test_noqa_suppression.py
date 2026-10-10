"""Tests for the transversal ``# noqa`` opt-out."""

import ast
import unittest

from analyzer.visitors.composite_visitor import CompositeVisitor
from analyzer.visitors.noqa import collect_noqa_directives


class TestCollectNoqaDirectives(unittest.TestCase):
    def test_bare_noqa_suppresses_all(self):
        directives = collect_noqa_directives(["x = 1  # noqa"])
        self.assertEqual(directives, {1: None})

    def test_explicit_codes(self):
        directives = collect_noqa_directives(["x = 1  # noqa: E501, F401"])
        self.assertEqual(directives, {1: {"E501", "F401"}})

    def test_noqa_in_string_is_ignored(self):
        directives = collect_noqa_directives(['x = "# noqa: F401"'])
        self.assertEqual(directives, {})

    def test_comment_only_line(self):
        directives = collect_noqa_directives(["# noqa: MISSING_DOCSTRING"])
        self.assertEqual(directives, {1: {"MISSING_DOCSTRING"}})


class TestCompositeNoqaSuppression(unittest.TestCase):
    def _issues(self, source: str) -> list[dict]:
        visitor = CompositeVisitor("m.py", scope="all", lines=source.splitlines())
        visitor.visit(ast.parse(source))
        return visitor.issues

    def test_noqa_code_suppresses_only_that_rule(self):
        source = "def public_func(x):  # noqa: MISSING_TYPE_HINTS\n    return x\n"

        types = {(issue["type"], issue["line"]) for issue in self._issues(source)}

        self.assertNotIn(("MISSING_TYPE_HINTS", 1), types)
        self.assertIn(("MISSING_DOCSTRING", 1), types)

    def test_bare_noqa_suppresses_all_on_line(self):
        source = "def public_func(x):  # noqa\n    return x\n"

        issues = self._issues(source)

        self.assertTrue(all(issue["line"] != 1 for issue in issues))

    def test_without_noqa_issue_is_reported(self):
        source = "def public_func(x):\n    return x\n"

        types = {issue["type"] for issue in self._issues(source)}

        self.assertIn("MISSING_TYPE_HINTS", types)


if __name__ == "__main__":
    unittest.main()
