"""Tests for the terminal summary reporter."""

import contextlib
import io
import json
import pathlib
import tempfile
import unittest

from analyzer.reporters.summary_reporter import _group_findings_by_severity, report_summary

_DATA = {
    "metrics": {
        "quality_score": 80.0,
        "maintainability_score": 75.0,
        "security_score": 100.0,
    },
    "research_summary": {
        "type_hint_coverage": 90.0,
        "return_hint_coverage": 80.0,
        "docstring_coverage": 70.0,
        "detected_docstring_styles": ["Google"],
        "qgis_context_summary": {
            "gdal_styles": {"Modern": 1},
            "pyqt_usage": {"PyQt5": 0, "PyQt6": 0},
            "total_legacy_signals": 0,
            "uses_processing": False,
            "signal_leaks": ["self.sig.connect(x)"],
        },
    },
    "modules": [
        {
            "path": "a.py",
            "lines": 10,
            "complexity": 20,
            "ast_issues": [
                {
                    "file": "a.py",
                    "line": 1,
                    "type": "MAGIC_NUMBER",
                    "severity": "warning",
                    "message": "m",
                }
            ],
            "security_issues": [],
            "functions": [{"name": "f", "complexity": 20, "line": 1}],
            "classes": ["Widget"],
        }
    ],
    "security": {
        "score": 50.0,
        "findings": [
            {
                "file": "a.py",
                "line": 2,
                "type": "B307",
                "severity": "high",
                "message": "eval",
                "code": "eval(x)",
            }
        ],
    },
}


class TestSummaryReporter(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = pathlib.Path(self._tmp.name)
        self.path = self.tmp / "project_context.json"
        self.path.write_text(json.dumps(_DATA), encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def _run(self, by: str) -> bool:
        with contextlib.redirect_stdout(io.StringIO()):
            return report_summary(self.path, by=by)

    def test_missing_file_returns_false(self):
        self.assertFalse(report_summary(self.tmp / "missing.json"))

    def test_total(self):
        self.assertTrue(self._run("total"))

    def test_by_modules(self):
        self.assertTrue(self._run("modules"))

    def test_by_functions(self):
        self.assertTrue(self._run("functions"))

    def test_by_classes(self):
        self.assertTrue(self._run("classes"))

    def test_by_security(self):
        self.assertTrue(self._run("security"))

    def test_unknown_mode_returns_false(self):
        self.assertFalse(self._run("bogus"))

    def test_group_findings_by_severity(self):
        groups = _group_findings_by_severity(
            [{"severity": "HIGH"}, {"severity": "weird"}, {"severity": "low"}]
        )

        self.assertEqual(len(groups["high"]), 1)
        self.assertEqual(len(groups["low"]), 1)
        self.assertEqual(len(groups["other"]), 1)


if __name__ == "__main__":
    unittest.main()
