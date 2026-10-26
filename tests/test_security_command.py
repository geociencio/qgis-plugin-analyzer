"""Tests for the security command's config overrides and JSON contract."""

import argparse
import contextlib
import io
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch

from analyzer.commands import handle_security
from analyzer.engine import ProjectConfig


class TestSecurityCommandOverrides(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        self.out = self.root / "out"
        self.out.mkdir(parents=True)
        (self.out / "project_context.json").write_text(
            json.dumps({"modules": [], "analyzed_at": "2026-10-25T00:00:00+00:00"}),
            encoding="utf-8",
        )

    def tearDown(self):
        self._tmp.cleanup()

    def _args(self, **overrides) -> argparse.Namespace:
        base = {
            "project_path": str(self.root),
            "output": str(self.out),
            "profile": "default",
            "strict": False,
            "no_cache": False,
            "deep": False,
            "tools": None,
            "fail_on": "critical",
            "json": True,
        }
        base.update(overrides)
        return argparse.Namespace(**base)

    def _run(self, args) -> tuple["object", str]:
        stdout = io.StringIO()
        with patch("analyzer.commands.ProjectAnalyzer") as mock_cls:
            analyzer = mock_cls.return_value
            analyzer.config = ProjectConfig()
            analyzer.run.return_value = True
            analyzer.output_dir = self.out
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    handle_security(args)
        return analyzer, stdout.getvalue()

    def test_no_cache_disables_config_cache(self):
        analyzer, _ = self._run(self._args(no_cache=True))

        self.assertFalse(analyzer.config.cache)

    def test_cache_enabled_by_default(self):
        analyzer, _ = self._run(self._args())

        self.assertTrue(analyzer.config.cache)

    def test_strict_is_applied(self):
        # handle_security previously ignored --strict (it never called the
        # override helper); guard the fix alongside --no-cache.
        analyzer, _ = self._run(self._args(strict=True))

        self.assertTrue(analyzer.config.strict)

    def test_run_uses_security_scope(self):
        analyzer, _ = self._run(self._args())

        analyzer.run.assert_called_once_with(scope="security")

    def test_deep_sets_deep_security(self):
        analyzer, _ = self._run(self._args(deep=True))

        self.assertTrue(analyzer.config.deep_security)

    def test_non_deep_is_focused(self):
        analyzer, _ = self._run(self._args(deep=False))

        self.assertFalse(analyzer.config.deep_security)

    def test_json_report_shape(self):
        _, stdout = self._run(self._args())

        report = json.loads(stdout)
        self.assertEqual(report["command"], "security")
        self.assertEqual(report["scope"], "security")
        self.assertEqual(report["tools"], ["native"])
        self.assertEqual(report["summary"]["total"], 0)


if __name__ == "__main__":
    unittest.main()
