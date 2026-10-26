"""Tests for Bandit/detect-secrets adapters and the security report merge."""

import pathlib
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from analyzer.bandit_audit import run_bandit_audit
from analyzer.detect_secrets_audit import run_detect_secrets_audit
from analyzer.secrets import SecretScanner
from analyzer.security_audit import (
    build_security_report,
    format_security_report,
    parse_tools,
)


class TestBanditAudit(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _completed(self, stdout: str, stderr: str = "", code: int = 1):
        return subprocess.CompletedProcess(
            args=["python", "-m", "bandit"], returncode=code, stdout=stdout, stderr=stderr
        )

    def test_high_severity_is_critical_and_blocking(self):
        payload = (
            '{"results": [{"filename": "%s", "line_number": 4, "col_offset": 2, '
            '"issue_severity": "HIGH", "issue_confidence": "HIGH", "test_id": "B602", '
            '"issue_text": "subprocess call with shell=True", "issue_cwe": {"id": 78}}]}'
            % (self.root / "plugin.py")
        )
        with patch("analyzer.bandit_audit.subprocess.run", return_value=self._completed(payload)):
            result = run_bandit_audit(self.root)

        self.assertFalse(result["tool_unavailable"])
        finding = result["findings"][0]
        self.assertEqual(finding["type"], "BANDIT_B602")
        self.assertEqual(finding["portal_severity"], "critical")
        self.assertTrue(finding["blocking"])
        self.assertEqual(finding["file"], "plugin.py")

    def test_unavailable_tool_is_explicit(self):
        with patch(
            "analyzer.bandit_audit.subprocess.run",
            return_value=self._completed("", "No module named bandit"),
        ):
            result = run_bandit_audit(self.root)

        self.assertTrue(result["tool_unavailable"])
        self.assertEqual(result["findings"], [])


class TestDetectSecretsAudit(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _completed(self, stdout: str, stderr: str = "", code: int = 1):
        return subprocess.CompletedProcess(
            args=["python", "-m", "detect_secrets"], returncode=code, stdout=stdout, stderr=stderr
        )

    def test_secret_is_critical_and_blocking(self):
        payload = (
            '{"version": "1.5.0", "results": {"%s": [{"type": "AWSKeyDetector", '
            '"line_number": 2, "hashed_secret": "abc", "is_verified": false}]}}'
            % (self.root / "plugin.py")
        )
        with patch(
            "analyzer.detect_secrets_audit.subprocess.run",
            return_value=self._completed(payload),
        ):
            result = run_detect_secrets_audit(self.root)

        self.assertFalse(result["tool_unavailable"])
        finding = result["findings"][0]
        self.assertEqual(finding["type"], "SECRET_AWSKEYDETECTOR")
        self.assertEqual(finding["portal_severity"], "critical")
        self.assertTrue(finding["blocking"])

    def test_unavailable_tool_is_explicit(self):
        with patch(
            "analyzer.detect_secrets_audit.subprocess.run",
            return_value=self._completed("", "No module named detect_secrets"),
        ):
            result = run_detect_secrets_audit(self.root)

        self.assertTrue(result["tool_unavailable"])
        self.assertEqual(result["findings"], [])


class TestSecurityReport(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _context(self, severity: str = "high"):
        return {
            "analyzed_at": "2026-10-25T00:00:00+00:00",
            "modules": [
                {
                    "path": "plugin.py",
                    "security_issues": [
                        {
                            "file": "plugin.py",
                            "line": 2,
                            "type": "B307",
                            "severity": severity,
                            "message": "eval detected",
                        }
                    ],
                    "ast_issues": [
                        {
                            "file": "plugin.py",
                            "line": 3,
                            "type": "UNSAFE_SUBPROCESS",
                            "severity": "high",
                            "message": "shell=True",
                        }
                    ],
                }
            ],
        }

    def test_parse_tools(self):
        self.assertEqual(parse_tools(None), ["native"])
        self.assertEqual(parse_tools("native,bandit"), ["native", "bandit"])
        self.assertEqual(
            parse_tools("bandit,detect-secrets,flake8"), ["bandit", "detect-secrets", "flake8"]
        )
        with self.assertRaises(ValueError):
            parse_tools("snyk")

    def test_native_summary_and_exit_code(self):
        report = build_security_report(
            self._context(), project_path=self.root, tools=["native"], deep=False
        )

        self.assertEqual(report["exit_code"], 1)
        self.assertEqual(report["summary"]["critical"], 2)
        self.assertEqual(report["summary"]["blocking"], 2)
        self.assertEqual(report["tool_status"], {"native": "ok"})

    def test_merge_prefers_external_tool(self):
        external = {
            "findings": [
                {
                    "file": "plugin.py",
                    "line": 2,
                    "type": "BANDIT_B307",
                    "rule_id": "B307",
                    "severity": "critical",
                    "portal_severity": "critical",
                    "blocking": True,
                    "message": "eval",
                    "tool": "bandit",
                }
            ],
            "tool_unavailable": False,
        }
        with patch("analyzer.security_audit.run_bandit_audit", return_value=external):
            report = build_security_report(
                self._context(), project_path=self.root, tools=["native", "bandit"], deep=False
            )

        b307 = [item for item in report["findings"] if item["rule_id"] == "B307"]
        self.assertEqual(len(b307), 1)
        self.assertEqual(b307[0]["tool"], "bandit")
        self.assertEqual(report["tool_status"]["bandit"], "ok")

    def test_flake8_tool_is_merged_as_info(self):
        external = {
            "findings": [
                {
                    "file": "plugin.py",
                    "line": 4,
                    "type": "FLAKE8_F401",
                    "rule_id": "F401",
                    "severity": "info",
                    "message": "'os' imported but unused",
                    "tool": "flake8",
                }
            ],
            "tool_unavailable": False,
        }
        with patch("analyzer.security_audit.run_flake8_audit", return_value=external):
            report = build_security_report(
                self._context(), project_path=self.root, tools=["native", "flake8"], deep=False
            )

        flake8 = [item for item in report["findings"] if item["tool"] == "flake8"]
        self.assertEqual(len(flake8), 1)
        self.assertEqual(flake8[0]["portal_severity"], "info")
        self.assertFalse(flake8[0]["blocking"])
        self.assertEqual(report["tool_status"]["flake8"], "ok")

    def test_tool_unavailable_exits_two(self):
        unavailable = {"findings": [], "tool_unavailable": True}
        with patch("analyzer.security_audit.run_bandit_audit", return_value=unavailable):
            report = build_security_report(
                self._context(), project_path=self.root, tools=["native", "bandit"], deep=False
            )

        self.assertEqual(report["exit_code"], 2)
        self.assertTrue(report["tool_unavailable"])

    def test_fail_on_warning_and_none(self):
        warning_context = self._context(severity="medium")
        self.assertEqual(
            build_security_report(
                warning_context,
                project_path=self.root,
                tools=["native"],
                deep=False,
                fail_on="warning",
            )["exit_code"],
            1,
        )
        self.assertEqual(
            build_security_report(
                warning_context,
                project_path=self.root,
                tools=["native"],
                deep=False,
                fail_on="none",
            )["exit_code"],
            0,
        )

    def test_format_report(self):
        report = build_security_report(
            self._context(), project_path=self.root, tools=["native"], deep=False
        )

        lines = format_security_report(report)
        self.assertIn("Security findings: 2", lines[0])
        self.assertTrue(any("B307" in line for line in lines))


class TestSecretScannerEntropy(unittest.TestCase):
    TOKEN = 'VALUE = "Xk9Qm2Lp8Rt4Vz7Nb3Wc6Yd1"'

    def test_entropy_is_opt_in(self):
        focused = SecretScanner(include_entropy=False).scan_text(self.TOKEN)
        deep = SecretScanner(include_entropy=True).scan_text(self.TOKEN)

        self.assertFalse(any(item.type == "HIGH_ENTROPY" for item in focused))
        self.assertTrue(any(item.type == "HIGH_ENTROPY" for item in deep))


if __name__ == "__main__":
    unittest.main()
