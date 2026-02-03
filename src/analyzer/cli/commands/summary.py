"""Summary command implementation."""

import argparse

from ...commands import handle_summary
from ..base import BaseCommand


class SummaryCommand(BaseCommand):
    """Command to show a quick terminal summary of analysis results."""

    @property
    def name(self) -> str:
        """Command name."""
        return "summary"

    @property
    def help(self) -> str:
        """Command help text."""
        return "Show a quick terminal summary of analysis results"

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure summary command arguments.

        Args:
            parser: The argument parser for this command.
        """
        parser.add_argument(
            "-i",
            "--input",
            help="Path to the research JSON file",
            default="analysis_results/project_context.json",
        )
        parser.add_argument(
            "-b",
            "--by",
            choices=["total", "modules", "functions", "classes"],
            default="total",
            help="Granularity of the summary (default: total)",
        )

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the summary command.

        Args:
            args: Parsed command-line arguments.

        Returns:
            Exit code (0 for success).
        """
        handle_summary(args)
        return 0
