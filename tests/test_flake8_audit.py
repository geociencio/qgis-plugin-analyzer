"""Tests for the Flake8 adapter (JSON, fallback parser and availability)."""

import json
import pathlib
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from analyzer.flake8_audit import run_flake8_audit


class TestFlake8Audit(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _completed(self, stdout: str, stderr: str = "", code: int = 1):
        return subprocess.CompletedProcess(
            args=["python", "-m", "flake8"], returncode=code, stdout=stdout, stderr=stderr
        )

    def test_json_output_is_normalized(self):
        filename = str(self.root / "a.py")
        payload = json.dumps(
            {
                filename: [
                    {
                        "code": "F401",
                        "filename": filename,
                        "line_number": 2,
                        "column_number": 1,
                        "text": "'os' imported but unused",
                    }
                ]
            }
        )
        with patch("analyzer.flake8_audit.importlib.util.find_spec", return_value=object()):
            with patch(
                "analyzer.flake8_audit.subprocess.run", return_value=self._completed(payload)
            ):
                result = run_flake8_audit(self.root)

        self.assertFalse(result["tool_unavailable"])
        self.assertEqual(result["formatter"], "json")
        self.assertEqual(len(result["findings"]), 1)
        finding = result["findings"][0]
        self.assertEqual(finding["file"], "a.py")
        self.assertEqual(finding["line"], 2)
        self.assertEqual(finding["code"], "F401")
        self.assertEqual(finding["type"], "FLAKE8_F401")
        self.assertEqual(finding["severity"], "info")

    def test_default_output_fallback(self):
        payload = f"{self.root / 'a.py'}:3:5: E501 line too long\n"
        with patch("analyzer.flake8_audit.importlib.util.find_spec", return_value=None):
            with patch(
                "analyzer.flake8_audit.subprocess.run", return_value=self._completed(payload)
            ):
                result = run_flake8_audit(self.root)

        self.assertEqual(result["formatter"], "default")
        self.assertEqual(result["findings"][0]["code"], "E501")
        self.assertEqual(result["findings"][0]["col"], 5)

    def test_clean_run_has_no_findings(self):
        with patch("analyzer.flake8_audit.importlib.util.find_spec", return_value=None):
            with patch(
                "analyzer.flake8_audit.subprocess.run",
                return_value=self._completed("", code=0),
            ):
                result = run_flake8_audit(self.root)

        self.assertEqual(result["findings"], [])
        self.assertFalse(result["tool_unavailable"])

    def test_json_reporter_module_is_detected(self):
        def fake_spec(name: str):
            return object() if name == "flake8_json_reporter" else None

        with patch("analyzer.flake8_audit.importlib.util.find_spec", side_effect=fake_spec):
            with patch(
                "analyzer.flake8_audit.subprocess.run",
                return_value=self._completed("{}", code=0),
            ):
                result = run_flake8_audit(self.root)

        self.assertEqual(result["formatter"], "json")
        self.assertFalse(result["tool_unavailable"])

    def test_unavailable_tool_is_explicit(self):
        with patch("analyzer.flake8_audit.importlib.util.find_spec", return_value=None):
            with patch(
                "analyzer.flake8_audit.subprocess.run",
                return_value=self._completed("", "No module named flake8", code=1),
            ):
                result = run_flake8_audit(self.root)

        self.assertTrue(result["tool_unavailable"])
        self.assertEqual(result["findings"], [])

    def test_config_argument(self):
        config = self.root / ".flake8"
        with patch("analyzer.flake8_audit.importlib.util.find_spec", return_value=None):
            with patch(
                "analyzer.flake8_audit.subprocess.run",
                return_value=self._completed("", code=0),
            ) as run:
                run_flake8_audit(self.root, config=config)

        command = run.call_args.args[0]
        self.assertIn("--config", command)
        self.assertIn(str(config), command)


if __name__ == "__main__":
    unittest.main()
