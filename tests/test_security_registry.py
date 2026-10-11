"""Regression tests for the Bandit-inspired security registry.

Guards against the built-in checks silently not being registered (the
``security_rules`` module is only imported for its registration side effect).
"""

import ast
import unittest

from analyzer.security_checker import SecurityRegistry
from analyzer.visitors.security_visitor import SecurityVisitor


def _findings(code: str) -> set[str]:
    visitor = SecurityVisitor("m.py")
    visitor.visit(ast.parse(code))
    return {finding["type"] for finding in visitor.findings}


class TestSecurityRegistry(unittest.TestCase):
    def test_checks_are_registered(self):
        total = sum(len(checks) for checks in SecurityRegistry._checks.values())
        self.assertGreater(total, 0)

    def test_eval_is_detected(self):
        self.assertIn("B307", _findings("eval(user_input)\n"))

    def test_exec_is_detected(self):
        self.assertIn("B102", _findings("exec(user_input)\n"))

    def test_attribute_exec_is_ignored(self):
        # QDialog.exec() is a method call, not the builtin exec()
        self.assertNotIn("B102", _findings("dlg.exec()\n"))

    def test_attribute_eval_is_ignored(self):
        # e.g. table.eval() is a method call, not the builtin eval()
        self.assertNotIn("B307", _findings("table.eval()\n"))

    def test_pickle_load_is_detected(self):
        self.assertIn("B301", _findings("import pickle\npickle.load(handle)\n"))

    def test_subprocess_shell_is_detected(self):
        self.assertIn(
            "B602",
            _findings("import subprocess\nsubprocess.run(cmd, shell=True)\n"),
        )

    def test_sql_injection_is_detected(self):
        code = 'cursor.execute(f"SELECT * FROM t WHERE id = {uid}")\n'
        self.assertIn("B608", _findings(code))

    def test_hardcoded_secret_is_detected(self):
        self.assertIn("HARDCODED_SECRET", _findings('api_key = "abcd1234efgh5678"\n'))

    def test_clean_code_has_no_findings(self):
        self.assertEqual(_findings("value = 1 + 2\n"), set())


if __name__ == "__main__":
    unittest.main()
