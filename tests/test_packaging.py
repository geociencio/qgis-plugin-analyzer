"""Static guards for the distribution boundary (wheel + sdist)."""

import pathlib
import tomllib
import unittest

_ROOT = pathlib.Path(__file__).resolve().parent.parent


class TestPackagingBoundary(unittest.TestCase):
    def test_setuptools_uses_the_src_layout(self):
        data = tomllib.loads((_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        tool = data["tool"]["setuptools"]

        self.assertEqual(tool["package-dir"][""], "src")
        self.assertFalse(tool["include-package-data"])
        self.assertEqual(tool["packages"]["find"]["where"], ["src"])
        self.assertEqual(tool["packages"]["find"]["include"], ["analyzer*"])

    def test_manifest_excludes_non_tool_content(self):
        manifest = (_ROOT / "MANIFEST.in").read_text(encoding="utf-8")

        for pattern in (
            "prune tests",
            "prune docs",
            "prune scripts",
            "prune .agent",
            "prune .agent-state",
            "prune src/qgis_plugin_analyzer.egg-info",
        ):
            self.assertIn(pattern, manifest)


if __name__ == "__main__":
    unittest.main()
