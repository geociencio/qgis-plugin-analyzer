"""Tests for the graph and serve CLI commands."""

import argparse
import contextlib
import io
import pathlib
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from analyzer.cli.commands.graph import GraphCommand
from analyzer.cli.commands.serve import ServeCommand
from analyzer.utils import IgnoreMatcher


class _BaseCliTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        self.out = self.root / "out"

    def tearDown(self):
        self._tmp.cleanup()


class TestGraphCommand(_BaseCliTest):
    def test_print_text_with_graph_and_cycles(self):
        command = GraphCommand()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            command._print_text({"a": ["b"]}, [["a", "b"]])

        self.assertIn("Circular Dependencies Detected", out.getvalue())

    def test_print_text_no_deps(self):
        command = GraphCommand()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            command._print_text({}, [])

        self.assertIn("No circular dependencies detected", out.getvalue())

    def test_print_mermaid(self):
        command = GraphCommand()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            command._print_mermaid({"a": ["b"]}, [["a", "b"]])

        self.assertIn("```mermaid", out.getvalue())
        self.assertIn("a --> b", out.getvalue())

    @patch.object(GraphCommand, "get_analyzer")
    def test_execute_text(self, mock_get_analyzer):
        analyzer = MagicMock()
        analyzer.project_path = self.root
        analyzer.matcher = IgnoreMatcher(self.root, [])
        analyzer.config.rules = {}
        analyzer._run_parallel_analysis.return_value = []
        analyzer._run_semantic_analysis.return_value = {"graph": {"a": ["b"]}, "cycles": []}
        mock_get_analyzer.return_value = analyzer

        args = argparse.Namespace(project_path=str(self.root), output=str(self.out), format="text")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(GraphCommand().execute(args), 0)

    @patch.object(GraphCommand, "get_analyzer")
    def test_execute_mermaid(self, mock_get_analyzer):
        analyzer = MagicMock()
        analyzer.project_path = self.root
        analyzer.matcher = IgnoreMatcher(self.root, [])
        analyzer.config.rules = {}
        analyzer._run_parallel_analysis.return_value = []
        analyzer._run_semantic_analysis.return_value = {"graph": {"a": ["b"]}, "cycles": []}
        mock_get_analyzer.return_value = analyzer

        args = argparse.Namespace(
            project_path=str(self.root), output=str(self.out), format="mermaid"
        )
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(GraphCommand().execute(args), 0)

    def test_get_analyzer_applies_strict(self):
        args = argparse.Namespace(
            project_path=str(self.root), output=str(self.out), profile="default", strict=True
        )

        analyzer = GraphCommand().get_analyzer(args)

        self.assertTrue(analyzer.config.strict)


class TestServeCommand(_BaseCliTest):
    def test_missing_report_returns_1(self):
        args = argparse.Namespace(output=str(self.out), port=0, no_browser=True)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(ServeCommand().execute(args), 1)

    @patch("socketserver.TCPServer")
    @patch("os.chdir")
    def test_serve_keyboard_interrupt_returns_0(self, _mock_chdir, mock_tcp):
        report = self.out / "PROJECT_SUMMARY.html"
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text("<html></html>", encoding="utf-8")

        httpd = mock_tcp.return_value.__enter__.return_value
        httpd.serve_forever.side_effect = KeyboardInterrupt

        args = argparse.Namespace(output=str(self.out), port=8000, no_browser=True)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(ServeCommand().execute(args), 0)


if __name__ == "__main__":
    unittest.main()
