"""Tests for the cyclomatic complexity gate (--max-cc)."""

import unittest

from analyzer.commands import _enforce_max_cc


class TestMaxCcGate(unittest.TestCase):
    """Unit tests for the _enforce_max_cc gate helper."""

    def _modules(self, *complexities):
        return [
            {
                "path": f"mod_{i}.py",
                "functions": [{"name": f"func_{i}", "line": i + 1, "complexity": cc}],
            }
            for i, cc in enumerate(complexities)
        ]

    def test_pass_when_all_under_threshold(self):
        result = _enforce_max_cc(self._modules(5, 8, 10), 10)
        self.assertEqual(result["gate"], "PASS")
        self.assertEqual(result["violations"], [])

    def test_fail_when_function_exceeds_threshold(self):
        result = _enforce_max_cc(self._modules(5, 15, 8), 10)
        self.assertEqual(result["gate"], "FAIL")
        self.assertEqual(len(result["violations"]), 1)
        violation = result["violations"][0]
        self.assertEqual(violation["name"], "func_1")
        self.assertEqual(violation["complexity"], 15)
        self.assertEqual(violation["line"], 2)

    def test_violations_sorted_descending(self):
        result = _enforce_max_cc(self._modules(12, 20, 15), 10)
        complexities = [v["complexity"] for v in result["violations"]]
        self.assertEqual(complexities, [20, 15, 12])

    def test_empty_modules_pass(self):
        result = _enforce_max_cc([], 5)
        self.assertEqual(result["gate"], "PASS")
        self.assertEqual(result["violations"], [])


if __name__ == "__main__":
    unittest.main()
