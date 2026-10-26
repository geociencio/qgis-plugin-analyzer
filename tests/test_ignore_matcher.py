"""Tests for ignore-file precedence, defaults and --exclude/--scope."""

import argparse
import pathlib
import tempfile
import unittest
from unittest.mock import patch

from analyzer.cli.app import CLIApp
from analyzer.cli.commands.analyze import AnalyzeCommand
from analyzer.commands import _parse_exclude_patterns
from analyzer.engine import ProjectAnalyzer
from analyzer.security_audit import build_security_report
from analyzer.utils import IgnoreMatcher, discover_project_files


class TestIgnoreDefaults(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        for directory in ("src", "docs", "tests", ".venv", "build"):
            (self.root / directory).mkdir()
        for path in (
            "src/plugin.py",
            "docs/guide.py",
            "tests/test_plugin.py",
            ".venv/lib.py",
            "build/artifact.py",
        ):
            (self.root / path).write_text("", encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def test_default_excludes_docs_tests_venv_build(self):
        matcher = IgnoreMatcher(self.root, [])

        for path in (
            "docs/guide.py",
            "tests/test_plugin.py",
            ".venv/lib.py",
            "build/artifact.py",
        ):
            self.assertTrue(matcher.is_ignored(self.root / path), path)
        self.assertFalse(matcher.is_ignored(self.root / "src/plugin.py"))

    def test_discovery_uses_default_excludes(self):
        discovery = discover_project_files(self.root, IgnoreMatcher(self.root, []))

        self.assertEqual([path.name for path in discovery["python_files"]], ["plugin.py"])

    def test_ignore_files_merge_and_negation_wins(self):
        (self.root / "generated").mkdir()
        (self.root / "secret").mkdir()
        (self.root / ".gitignore").write_text("*.log\ngenerated/\n", encoding="utf-8")
        (self.root / ".qgisignore").write_text("secret/\n", encoding="utf-8")
        (self.root / ".analyzerignore").write_text(
            "!generated/keep.py\n!docs/guide.py\n", encoding="utf-8"
        )
        for path in ("generated/debug.log", "generated/keep.py", "secret/key.txt"):
            (self.root / path).write_text("", encoding="utf-8")

        analyzer = ProjectAnalyzer(str(self.root), str(self.root / "out"))

        self.assertTrue(analyzer.matcher.is_ignored(self.root / "generated/debug.log"))
        self.assertTrue(analyzer.matcher.is_ignored(self.root / "secret/key.txt"))
        self.assertFalse(analyzer.matcher.is_ignored(self.root / "generated/keep.py"))
        self.assertFalse(analyzer.matcher.is_ignored(self.root / "docs/guide.py"))

    def test_cli_excludes_can_negate_defaults(self):
        analyzer = ProjectAnalyzer(str(self.root), str(self.root / "out"))

        from analyzer.commands import _apply_config_overrides

        _apply_config_overrides(
            analyzer,
            argparse.Namespace(
                strict=False,
                report=False,
                include_content=False,
                no_cache=False,
                exclude=["!docs/"],
            ),
        )

        self.assertFalse(analyzer.matcher.is_ignored(self.root / "docs/guide.py"))

    def test_exclude_comma_normalization(self):
        self.assertEqual(
            _parse_exclude_patterns(["docs/,tests/", "!src/keep.py"]),
            ["docs/", "tests/", "!src/keep.py"],
        )

    def test_external_security_findings_respect_matcher(self):
        external = {
            "findings": [
                {
                    "file": "docs/leak.py",
                    "line": 1,
                    "type": "SECRET_AWS",
                    "rule_id": "AWS",
                    "severity": "critical",
                    "portal_severity": "critical",
                    "blocking": True,
                    "message": "secret",
                    "tool": "detect-secrets",
                }
            ],
            "tool_unavailable": False,
        }
        with patch("analyzer.security_audit.run_detect_secrets_audit", return_value=external):
            report = build_security_report(
                {"modules": []},
                project_path=self.root,
                tools=["native", "detect-secrets"],
                deep=False,
                matcher=IgnoreMatcher(self.root, []),
            )

        self.assertEqual(report["findings"], [])
        self.assertEqual(report["tool_status"]["detect-secrets"], "ok")


class TestScopeFlag(unittest.TestCase):
    def test_parser_accepts_scope_and_repeatable_exclude(self):
        parser = CLIApp()._build_parser()
        args = parser.parse_args(
            [
                "analyze",
                ".",
                "--scope",
                "i18n",
                "--exclude",
                "docs/",
                "--exclude",
                "!docs/keep.py",
            ]
        )

        self.assertEqual(args.scope, "i18n")
        self.assertEqual(args.exclude, ["docs/", "!docs/keep.py"])

    def test_scope_flag_sets_scope_and_path(self):
        args = argparse.Namespace(
            scope="i18n",
            scope_or_path="/tmp/plugin",
            remaining_path=None,
        )

        with patch("analyzer.cli.commands.analyze.handle_analyze") as handler:
            self.assertEqual(AnalyzeCommand().execute(args), 0)

        self.assertEqual(args.scope, "i18n")
        self.assertEqual(args.project_path, "/tmp/plugin")
        handler.assert_called_once_with(args)

    def test_positional_scope_still_works(self):
        args = argparse.Namespace(
            scope=None,
            scope_or_path="metadata",
            remaining_path="/tmp/plugin",
        )

        with patch("analyzer.cli.commands.analyze.handle_analyze"):
            AnalyzeCommand().execute(args)

        self.assertEqual(args.scope, "metadata")
        self.assertEqual(args.project_path, "/tmp/plugin")

    def test_duplicate_scope_is_rejected(self):
        args = argparse.Namespace(scope="i18n", scope_or_path="i18n", remaining_path=None)

        with self.assertRaises(ValueError):
            AnalyzeCommand().execute(args)


if __name__ == "__main__":
    unittest.main()
