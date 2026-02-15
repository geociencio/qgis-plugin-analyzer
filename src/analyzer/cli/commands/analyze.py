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
        # We manually handle subcommands (scopes) to maintain 100% backward
        # compatibility with 'analyze [path]'.
        parser.add_argument(
            "scope_or_path",
            nargs="?",
            default=".",
            help="Analysis scope (i18n, performance, architecture, metadata) or project path",
        )
        parser.add_argument(
            "remaining_path",
            nargs="?",
            help="Project path if a scope was specified in the first argument",
        )
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
        scopes = ["all", "i18n", "security", "performance", "architecture", "metadata"]

        # Logic to distinguish between 'analyze [scope] [path]' and 'analyze [path]'
        if args.scope_or_path in scopes:
            args.scope = args.scope_or_path
            args.project_path = args.remaining_path or "."
        else:
            args.scope = "all"
            args.project_path = args.scope_or_path

        handle_analyze(args)
        return 0
