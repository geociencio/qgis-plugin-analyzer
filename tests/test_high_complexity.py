import pathlib
import shutil
import tempfile
import unittest

from analyzer.scanner import analyze_module_worker


class TestScannerHighComplexity(unittest.TestCase):
    """Unit tests for the high complexity rule detection."""

    def setUp(self) -> None:
        """Sets up a temporary directory for each test."""
        self.test_dir = pathlib.Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        """Cleans up temporary resources."""
        shutil.rmtree(self.test_dir)

    def test_high_complexity_rule(self):
        # Create a file with high complexity function
        # e.g., 16 conditional branches

        branches = "\n    ".join([f"if x == {i}: pass" for i in range(20)])
        code = f"""
def complex_f(x):
    {branches}
"""
        test_file = self.test_dir / "test_high_complexity.py"
        test_file.write_text(code, encoding="utf-8")

        # Analyze
        result = analyze_module_worker(test_file, self.test_dir)

        self.assertIsNotNone(result)
        issues = result["ast_issues"]

        # Check if HIGH_COMPLEXITY issue is present
        high_complexity_issues = [i for i in issues if i["type"] == "HIGH_COMPLEXITY"]
        self.assertEqual(len(high_complexity_issues), 1)
        self.assertIn("too complex", high_complexity_issues[0]["message"])
        self.assertIn(
            "CC=31", high_complexity_issues[0]["message"]
        )  # 1 (base) + 20 (ifs) + density penalty (1.5x)


if __name__ == "__main__":
    unittest.main()
