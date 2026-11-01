"""Integration tests for signal connections in project_context.json."""

import contextlib
import io
import json
import pathlib
import tempfile
import unittest

from analyzer.engine import ProjectAnalyzer
from analyzer.reporters.summary_reporter import report_summary

_PLUGIN = """\
class Plugin:
    def initGui(self):
        self.btn.clicked.connect(self.on_click)
        self.other.clicked.connect(self.on_other)
    def unload(self):
        self.btn.clicked.disconnect(self.on_click)
"""


class TestSignalIntegration(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        (self.root / "metadata.txt").write_text(
            "[general]\nname=Demo\nversion=1.0\n", encoding="utf-8"
        )
        (self.root / "plugin.py").write_text(_PLUGIN, encoding="utf-8")
        self.out = self.root / "out"

    def tearDown(self):
        self._tmp.cleanup()

    def _run(self, profile: str = "default") -> dict:
        analyzer = ProjectAnalyzer(str(self.root), str(self.out), profile=profile)
        self.assertTrue(analyzer.run(scope="all"))
        with open(self.out / "project_context.json", encoding="utf-8") as handle:
            return json.load(handle)

    def test_project_json_contains_signal_connections(self):
        data = self._run()
        summary = data["research_summary"]["qgis_context_summary"]

        self.assertEqual(summary["signal_connections"]["summary"]["unmatched"], 1)
        self.assertEqual(summary["signal_connections"]["summary"]["matched"], 1)
        self.assertEqual(summary["signal_leaks"], ["self.other.clicked"])
        module_context = data["modules"][0]["research_metrics"]["qgis_context"]
        self.assertIn("signal_connections", module_context)
        self.assertNotIn("signal_events", module_context)

    def test_emit_config_adds_signal_issue(self):
        (self.root / "pyproject.toml").write_text(
            "[tool.qgis-analyzer.profiles.default.rules.SIGNAL_LEAK]\n"
            'emit = true\nscope = "class"\nconfidence = "low"\n',
            encoding="utf-8",
        )
        data = self._run()

        issue_types = {issue["type"] for issue in data["modules"][0]["ast_issues"]}
        self.assertIn("SIGNAL_LEAK", issue_types)

    def test_summary_signal_details_are_opt_in(self):
        self._run()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            report_summary(self.out / "project_context.json", show_signals=True)

        text = output.getvalue()
        self.assertIn("Unmatched signal paths: 1", text)
        self.assertIn("self.other.clicked", text)


if __name__ == "__main__":
    unittest.main()
