import pathlib
import unittest

from analyzer.reporters.html_reporter import generate_html_report
from analyzer.reporters.markdown_reporter import generate_markdown_summary


class TestReporters(unittest.TestCase):
    def setUp(self):
        self.test_dir = pathlib.Path("test_reports")
        self.test_dir.mkdir(exist_ok=True)
        self.mock_data = {
            "project_name": "TestProject",
            "project_type": "qgis",
            "metrics": {
                "quality_score": 85.0,
                "maintainability_score": 75.0,
                "total_lines": 1000,
            },
            "qgis_compliance": {
                "compliance_score": 90.0,
                "best_practices": {
                    "issues": [
                        {
                            "file": "main.py",
                            "line": 10,
                            "severity": "medium",
                            "message": "Test issue",
                            "code": "print('hello')",
                        }
                    ]
                },
            },
            "research_summary": {
                "type_hint_coverage": 80,
                "docstring_coverage": 70,
                "return_hint_coverage": 60,
                "detected_docstring_styles": ["Google"],
            },
            "semantic": {
                "circular_dependencies": [["a", "b", "a"]],
                "missing_resources": ["icon.png"],
                "coupling_metrics": {"module_a": {"fan_in": 5, "fan_out": 2}},
            },
            "repository_compliance": {
                "is_compliant": False,
                "binaries": ["test.exe"],
                "package_size_mb": 25.0,
                "url_validation": {"http://test.com": "failed"},
            },
            "ruff_findings": [
                {
                    "code": "E402",
                    "message": "Module level import not at top of file",
                    "filename": "test.py",
                    "location": {"row": 5},
                }
            ],
        }

    def tearDown(self):
        # Cleanup test reports
        if self.test_dir.exists():
            for f in self.test_dir.glob("*"):
                f.unlink()
            self.test_dir.rmdir()

    def test_html_report_generation(self):
        output_path = self.test_dir / "report.html"
        generate_html_report(self.mock_data, output_path)

        self.assertTrue(output_path.exists())
        content = output_path.read_text(encoding="utf-8")
        self.assertIn("TestProject", content)
        self.assertIn("85.0/100", content)
        self.assertIn("Test issue", content)
        self.assertIn("Circular Dependencies Detected", content)
        self.assertIn("test.exe", content)

    def test_markdown_report_generation(self):
        output_path = self.test_dir / "report.md"
        generate_markdown_summary(self.mock_data, output_path)

        self.assertTrue(output_path.exists())
        content = output_path.read_text(encoding="utf-8")
        self.assertIn("# 📋 Project Analysis Report: TestProject", content)
        self.assertIn("Module Stability Score", content)
        self.assertIn("85.0/100", content)
        self.assertIn("Test issue", content)
        self.assertIn("Circular Import Cycles", content)
        self.assertIn("icon.png", content)


if __name__ == "__main__":
    unittest.main()
