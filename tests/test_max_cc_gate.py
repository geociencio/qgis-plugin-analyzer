"""Tests for the cyclomatic complexity gate (--max-cc)."""

import io
import json
import pathlib
import tempfile
import unittest
from argparse import Namespace
from unittest.mock import patch

from analyzer.commands import _enforce_max_cc, handle_analyze


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


class TestMaxCcGateCli(unittest.TestCase):
    """Integration tests for the --max-cc gate exit behavior and JSON shape."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.out = pathlib.Path(self.tmp) / "out"
        self.out.mkdir()

    def _write_context(self, functions):
        data = {
            "schema_version": 1,
            "analyzer_version": "1.13.2",
            "modules": [
                {
                    "path": "mod.py",
                    "functions": functions,
                    "ast_issues": [],
                    "security_issues": [],
                }
            ],
        }
        (self.out / "project_context.json").write_text(json.dumps(data), encoding="utf-8")

    def _args(self, max_cc, as_json=False):
        return Namespace(
            project_path=self.tmp,
            output=str(self.out),
            profile="default",
            scope="all",
            json=as_json,
            max_cc=max_cc,
            strict=False,
            report=False,
            include_content=False,
        )

    @patch("analyzer.commands.ProjectAnalyzer")
    @patch("analyzer.commands.report_summary")
    def test_gate_fail_exits_1(self, mock_summary, mock_analyzer_cls):
        analyzer = mock_analyzer_cls.return_value
        analyzer.run.return_value = True
        analyzer.output_dir = self.out
        self._write_context([{"name": "f", "line": 1, "complexity": 15}])

        with self.assertRaises(SystemExit) as cm:
            handle_analyze(self._args(10))
        self.assertEqual(cm.exception.code, 1)

    @patch("analyzer.commands.ProjectAnalyzer")
    @patch("analyzer.commands.report_summary")
    def test_gate_pass_returns_normally(self, mock_summary, mock_analyzer_cls):
        analyzer = mock_analyzer_cls.return_value
        analyzer.run.return_value = True
        analyzer.output_dir = self.out
        self._write_context([{"name": "f", "line": 1, "complexity": 5}])

        handle_analyze(self._args(10))  # should not raise

    @patch("analyzer.commands.ProjectAnalyzer")
    def test_json_shape_and_cc_gate(self, mock_analyzer_cls):
        analyzer = mock_analyzer_cls.return_value
        analyzer.run.return_value = True
        analyzer.output_dir = self.out
        self._write_context([{"name": "f", "line": 1, "complexity": 15}])

        buf = io.StringIO()
        with patch("sys.stdout", buf):
            handle_analyze(self._args(10, as_json=True))

        data = json.loads(buf.getvalue())
        self.assertEqual(data["schema_version"], 1)
        self.assertIn("modules", data)
        self.assertEqual(data["cc_gate"], "FAIL")
        self.assertEqual(data["cc_violations"][0]["name"], "f")


if __name__ == "__main__":
    unittest.main()
