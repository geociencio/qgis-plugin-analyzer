import pathlib
import shutil
import sys
import tempfile
import unittest

# Add src to path
sys.path.append(str(pathlib.Path(__file__).parent.parent / "src"))

from analyzer.reporters import generate_html_report
from analyzer.utils import load_profile_config


class TestAnalyzer(unittest.TestCase):
    """Unit tests for the core ProjectAnalyzer logic and TOML configuration."""

    def setUp(self) -> None:
        """Sets up a temporary directory for each test."""
        self.test_dir = pathlib.Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        """Cleans up temporary resources after each test."""
        shutil.rmtree(self.test_dir)

    def test_load_profile_config(self):
        pyproject = self.test_dir / "pyproject.toml"
        pyproject.write_text(
            """
[tool.qgis-analyzer.profiles.default]
strict = false
generate_html = true
fail_on_error = false

[tool.qgis-analyzer.profiles.default.rules.MISSING_I18N]
extra_ignore_calls = ["custom_call"]
extra_exact_ignores = ["Custom Ignored"]
""",
            encoding="utf-8",
        )
        config = load_profile_config(self.test_dir)

        self.assertFalse(config["strict"])
        self.assertTrue(config["generate_html"])
        rules = config["rules"]
        self.assertEqual(rules["MISSING_I18N"]["extra_ignore_calls"], ["custom_call"])
        self.assertEqual(rules["MISSING_I18N"]["extra_exact_ignores"], ["Custom Ignored"])

    def test_html_report(self):
        analyses = {
            "project_name": "TestProject",
            "metrics": {"quality_score": 85, "total_files": 10, "total_lines": 1000},
            "qgis_compliance": {
                "compliance_score": 90,
                "best_practices": {
                    "issues": [
                        {
                            "severity": "high",
                            "message": "Critical issue",
                            "file": "main.py",
                            "line": 10,
                            "code": "print('bad')",
                        }
                    ]
                },
            },
            "ruff_findings": [
                {
                    "code": "E501",
                    "message": "Line too long",
                    "filename": "main.py",
                    "location": {"row": 1},
                }
            ],
        }
        report_path = self.test_dir / "report.html"
        generate_html_report(analyses, report_path)

        content = report_path.read_text(encoding="utf-8")
        self.assertIn("<title>Analysis Report - TestProject</title>", content)
        self.assertIn("85/100", content)
        self.assertIn("90/100", content)
        self.assertIn("Critical issue", content)
        self.assertIn("Line too long", content)


if __name__ == "__main__":
    unittest.main()
