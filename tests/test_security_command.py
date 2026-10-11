"""Tests for the security command's config overrides (e.g. --no-cache)."""

import argparse
import contextlib
import io
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
        }
        base.update(overrides)
        return argparse.Namespace(**base)

    def _run(self, args) -> "object":
        with patch("analyzer.commands.ProjectAnalyzer") as mock_cls:
            analyzer = mock_cls.return_value
            analyzer.config = ProjectConfig()
            analyzer.run.return_value = True
            analyzer.output_dir = self.out
            with contextlib.redirect_stdout(io.StringIO()):
                handle_security(args)
        return analyzer

    def test_no_cache_disables_config_cache(self):
        analyzer = self._run(self._args(no_cache=True))

        self.assertFalse(analyzer.config.cache)

    def test_cache_enabled_by_default(self):
        analyzer = self._run(self._args())

        self.assertTrue(analyzer.config.cache)

    def test_strict_is_applied(self):
        # handle_security previously ignored --strict (it never called the
        # override helper); guard the fix alongside --no-cache.
        analyzer = self._run(self._args(strict=True))

        self.assertTrue(analyzer.config.strict)


if __name__ == "__main__":
    unittest.main()
