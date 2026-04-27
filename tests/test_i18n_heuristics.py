import ast
import unittest

from src.analyzer.visitors.standards_visitor import StandardsVisitor


class TestI18nHeuristics(unittest.TestCase):
    def setUp(self):
        self.visitor = StandardsVisitor("test.py")

    def analyze_code(self, code):
        tree = ast.parse(code)
        # StandardsVisitor uses a custom orchestration in the engine,
        # but here we can simulate visit_Constant directly or use generic_visit
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                if isinstance(child, ast.Constant):
                    self.visitor.visit_Constant(child, parent=node)
        return [
            issue for issue in self.visitor.issues if issue["type"] == "MISSING_I18N"
        ]

    def test_should_ignore_short_technical_strings(self):
        code = "self.id = 'id'\nself.data = 'data'"
        issues = self.analyze_code(code)
        self.assertEqual(
            len(issues), 0, f"Should ignore short technical strings, found: {issues}"
        )

    def test_should_ignore_dict_keys_and_values(self):
        code = "d = {'key': 'value', 'type': 'internal'}"
        issues = self.analyze_code(code)
        self.assertEqual(
            len(issues), 0, f"Should ignore dict technical strings, found: {issues}"
        )

    def test_should_report_user_facing_strings(self):
        code = "self.label.setText('Please enter your name:')"
        issues = self.analyze_code(code)
        self.assertGreater(
            len(issues),
            0,
            "Should report strings with spaces/punctuation as user-facing",
        )

    def test_should_ignore_snake_case_and_technical_patterns(self):
        code = "self.config = 'my_internal_config_v1'\nself.path = 'C:/Users/Test'"
        issues = self.analyze_code(code)
        self.assertEqual(len(issues), 0, "Should ignore snake_case and paths")


if __name__ == "__main__":
    unittest.main()
