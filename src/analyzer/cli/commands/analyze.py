"""Analyze command implementation."""

import argparse

from ...commands import handle_analyze
from ..base import BaseAnalyzerCommand


class AnalyzeCommand(BaseAnalyzerCommand):
    """Command to analyze an existing QGIS plugin."""

    @property
    def name(self) -> str:
        """Command name."""
        return "analyze"

    @property
    def help(self) -> str:
        """Command help text."""
        return "Analyze an existing QGIS plugin"

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure analyze command arguments.

        Args:
            parser: The argument parser for this command.
        """
        parser.add_argument("project_path", help="Path to the QGIS project to analyze")
        self.add_common_args(parser)
        parser.add_argument(
            "-r",
            "--report",
            action="store_true",
            help="Generate detailed HTML/Markdown reports",
        )

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the analyze command.

        Args:
            args: Parsed command-line arguments.

        Returns:
            Exit code (0 for success).
        """
        # Note: logic moved to BaseAnalyzerCommand.get_analyzer
        handle_analyze(args)
        return 0
