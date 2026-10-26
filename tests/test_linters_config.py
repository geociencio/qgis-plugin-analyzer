"""Tests for the --linters/--flake8 overrides and Flake8 scoring penalties."""

import argparse
import unittest

from analyzer.commands import _apply_config_overrides
from analyzer.engine import ProjectConfig
from analyzer.scoring import ScoringEngine


class _FakeAnalyzer:
    def __init__(self):
        self.config = ProjectConfig()


class TestLinterOverrides(unittest.TestCase):
    def _args(self, **overrides) -> argparse.Namespace:
        base = {"strict": False, "report": False, "include_content": False, "no_cache": False}
        base.update(overrides)
        return argparse.Namespace(**base)

    def test_flake8_shorthand_enables_both(self):
        analyzer = _FakeAnalyzer()

        _apply_config_overrides(analyzer, self._args(flake8=True))

        self.assertEqual(analyzer.config.linters, ["ruff", "flake8"])

    def test_explicit_linters(self):
        analyzer = _FakeAnalyzer()

        _apply_config_overrides(analyzer, self._args(linters="flake8"))

        self.assertEqual(analyzer.config.linters, ["flake8"])

    def test_none_disables_linters(self):
        analyzer = _FakeAnalyzer()

        _apply_config_overrides(analyzer, self._args(linters="none"))

        self.assertEqual(analyzer.config.linters, [])

    def test_unknown_linter_is_rejected(self):
        analyzer = _FakeAnalyzer()

        with self.assertRaises(ValueError):
            _apply_config_overrides(analyzer, self._args(linters="snyk"))


class TestFlake8Scoring(unittest.TestCase):
    def test_flake8_findings_reduce_maintainability(self):
        engine = ScoringEngine("generic")
        modules = [
            {
                "path": "a.py",
                "lines": 100,
                "functions": [{"complexity": 2}],
                "ast_issues": [],
            }
        ]
        base = engine._get_maint_score(modules, [])
        penalized = engine._get_maint_score(modules, [], [{"code": "F401", "type": "FLAKE8_F401"}])

        self.assertLess(penalized, base)


if __name__ == "__main__":
    unittest.main()
