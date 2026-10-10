import sys
import unittest
from unittest.mock import MagicMock, patch

from analyzer.engine import ProjectAnalyzer


class TestRuffAudit(unittest.TestCase):
    def _analyzer(self) -> ProjectAnalyzer:
        analyzer = ProjectAnalyzer("/tmp")
        analyzer.config = MagicMock(strict=False)
        return analyzer

    @patch("subprocess.run")
    def test_invokes_ruff_via_interpreter(self, mock_run):
        mock_run.return_value = MagicMock(stdout="[]", stderr="", returncode=0)

        result = self._analyzer().run_ruff_audit()

        cmd = mock_run.call_args.args[0]
        self.assertEqual(cmd[0], sys.executable)
        self.assertIn("ruff", cmd)
        self.assertFalse(result["tool_unavailable"])

    @patch("subprocess.run")
    def test_tool_unavailable_when_module_missing(self, mock_run):
        mock_run.return_value = MagicMock(stdout="", stderr="No module named ruff", returncode=1)

        result = self._analyzer().run_ruff_audit()

        self.assertTrue(result["tool_unavailable"])
        self.assertEqual(result["findings"], [])

    @patch("subprocess.run")
    def test_tool_unavailable_on_exception(self, mock_run):
        mock_run.side_effect = FileNotFoundError("no interpreter")

        result = self._analyzer().run_ruff_audit()

        self.assertTrue(result["tool_unavailable"])

    @patch("subprocess.run")
    def test_findings_parsed(self, mock_run):
        mock_run.return_value = MagicMock(stdout='[{"code": "F401"}]', stderr="", returncode=1)

        result = self._analyzer().run_ruff_audit()

        self.assertEqual(result["findings"], [{"code": "F401"}])
        self.assertFalse(result["tool_unavailable"])


if __name__ == "__main__":
    unittest.main()
