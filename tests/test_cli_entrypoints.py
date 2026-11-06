"""Tests for the canonical CLI entry points."""

import subprocess
import sys
import tomllib
import unittest
from pathlib import Path

import analyzer
import analyzer.cli as cli
from analyzer.cli import CLIApp as ExportedCLIApp
from analyzer.cli.app import CLIApp as DirectCLIApp


class TestCLIEntryPoints(unittest.TestCase):
    def test_cli_package_reexports_cli_app(self):
        self.assertIs(ExportedCLIApp, DirectCLIApp)

    def test_cli_package_has_no_duplicate_main(self):
        self.assertFalse(hasattr(cli, "main"))

    def test_python_m_analyzer_version(self):
        result = subprocess.run(
            [sys.executable, "-m", "analyzer", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn(analyzer.__version__, result.stdout)

    def test_python_m_analyzer_help(self):
        result = subprocess.run(
            [sys.executable, "-m", "analyzer"],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("usage:", result.stdout.lower())

    def test_console_script_entrypoint_is_canonical(self):
        pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
        with pyproject.open("rb") as handle:
            data = tomllib.load(handle)

        self.assertEqual(data["project"]["scripts"]["qgis-analyzer"], "analyzer.main:main")


if __name__ == "__main__":
    unittest.main()
