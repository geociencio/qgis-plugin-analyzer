import io
import pathlib
import shutil
import sys
import tempfile
import unittest

# Add src to path
sys.path.append(str(pathlib.Path(__file__).parent.parent / "src"))

from analyzer.reporters import generate_html_report
from analyzer.utils import _minimal_toml_load


class TestAnalyzer(unittest.TestCase):
    def setUp(self):
        self.test_dir = pathlib.Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_minimal_toml(self):
        toml_content = b"""
[tool.qgis-analyzer.profiles.default]
strict = false
generate_html = true
fail_on_error = false

[tool.qgis-analyzer.profiles.release]
strict = true
generate_html = true
fail_on_error = true
version = "0.3.1"
count = 42
"""
        f = io.BytesIO(toml_content)
        data = _minimal_toml_load(f)

        profiles = data["tool"]["qgis-analyzer"]["profiles"]
        self.assertFalse(profiles["default"]["strict"])
        self.assertTrue(profiles["default"]["generate_html"])
        self.assertTrue(profiles["release"]["strict"])
        self.assertEqual(profiles["release"]["version"], "0.3.1")
        self.assertEqual(profiles["release"]["count"], 42)

    def test_html_report(self):
        analyses = {
            "project_name": "TestProject",
            "metrics": {
                "quality_score": 85,
                "total_files": 10,
                "total_lines": 1000
            },
            "qgis_compliance": {
                "compliance_score": 90,
                "best_practices": {
                    "issues": [
                        {"severity": "high", "message": "Critical issue", "file": "main.py", "line": 10, "code": "print('bad')"}
                    ]
                }
            },
            "ruff_findings": [
                {"code": "E501", "message": "Line too long", "filename": "main.py", "location": {"row": 1}}
            ]
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
