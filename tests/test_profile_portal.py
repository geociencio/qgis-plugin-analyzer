"""Tests for the portal profile and CLI > profile > default precedence."""

import argparse
import pathlib
import tempfile
import unittest

from analyzer.commands import _apply_config_overrides, _security_options
from analyzer.engine import ProjectAnalyzer
from analyzer.engine_config import ProjectConfig

_PORTAL_TOML = """\
[tool.qgis-analyzer.profiles.portal]
linters = ["ruff", "flake8"]
security_tools = ["native", "bandit", "detect-secrets", "flake8"]
security_fail_on = "warning"
metadata_rules = true
fail_on = "critical"
deep_security = true
"""


class TestPortalProfile(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        (self.root / "pyproject.toml").write_text(_PORTAL_TOML, encoding="utf-8")
        (self.root / "metadata.txt").write_text("[general]\nname=Demo\n", encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def _analyzer(self) -> ProjectAnalyzer:
        return ProjectAnalyzer(str(self.root), str(self.root / "out"), profile="portal")

    def test_profile_values_are_loaded(self):
        config = self._analyzer().config

        self.assertEqual(config.linters, ["ruff", "flake8"])
        self.assertEqual(config.security_tools, ["native", "bandit", "detect-secrets", "flake8"])
        self.assertEqual(config.security_fail_on, "warning")
        self.assertTrue(config.metadata_rules)
        self.assertEqual(config.fail_on, "critical")
        self.assertTrue(config.deep_security)
        self.assertTrue(config.deep_security_configured)

    def test_security_options_use_profile_defaults(self):
        config = self._analyzer().config
        args = argparse.Namespace(tools=None, fail_on=None, json=True, deep=None)

        tools, fail_on, as_json, deep = _security_options(args, config)

        self.assertEqual(tools, ["native", "bandit", "detect-secrets", "flake8"])
        self.assertEqual(fail_on, "warning")
        self.assertTrue(as_json)
        self.assertTrue(deep)

    def test_cli_overrides_profile(self):
        analyzer = self._analyzer()
        args = argparse.Namespace(
            tools="native",
            fail_on="none",
            json=False,
            deep=False,
            strict=False,
            report=False,
            include_content=False,
            no_cache=False,
        )
        _apply_config_overrides(analyzer, args)

        tools, fail_on, _as_json, deep = _security_options(args, analyzer.config)

        self.assertEqual(tools, ["native"])
        self.assertEqual(fail_on, "none")
        self.assertFalse(deep)

    def test_deep_is_not_overridden_when_flag_is_absent(self):
        analyzer = self._analyzer()

        _apply_config_overrides(
            analyzer,
            argparse.Namespace(strict=False, report=False, include_content=False, no_cache=False),
        )

        self.assertTrue(analyzer.config.deep_security)

    def test_explicit_deep_false_overrides_profile(self):
        analyzer = self._analyzer()

        _apply_config_overrides(
            analyzer,
            argparse.Namespace(
                strict=False,
                report=False,
                include_content=False,
                no_cache=False,
                deep=False,
            ),
        )

        self.assertFalse(analyzer.config.deep_security)
        self.assertTrue(analyzer.config.deep_security_configured)

    def test_fail_on_gate(self):
        analyzer = ProjectAnalyzer.__new__(ProjectAnalyzer)
        analyzer.config = ProjectConfig(fail_on="critical")
        analyses = {
            "modules": [
                {
                    "security_issues": [
                        {
                            "file": "a.py",
                            "line": 1,
                            "type": "B307",
                            "severity": "high",
                            "message": "eval",
                        }
                    ]
                }
            ]
        }

        self.assertTrue(analyzer._fail_on_gate(analyses))
        analyzer.config = ProjectConfig(fail_on="none")
        self.assertFalse(analyzer._fail_on_gate(analyses))


if __name__ == "__main__":
    unittest.main()
