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
            "--scope",
            choices=["all", "i18n", "security", "performance", "architecture", "metadata"],
            default=None,
            help="Analysis scope (alternative to the positional scope form)",
        )
        parser.add_argument(
            "--exclude",
            action="append",
            default=None,
            metavar="PATTERN",
            help="Additional ignore pattern (repeatable/comma-separated; ! re-includes)",
        )
        parser.add_argument(
            "-r",
            "--report",
            action="store_true",
            help="Generate detailed HTML/Markdown reports",
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Emit machine-readable JSON (project_context.json) to stdout",
        )
        parser.add_argument(
            "--include-content",
            action="store_true",
            help="Include module source content in the JSON output",
        )
        parser.add_argument(
            "--linters",
            default=None,
            metavar="LIST",
            help="Comma-separated lint tools to run (ruff,flake8; use 'none' to disable)",
        )
        parser.add_argument(
            "--flake8",
            action="store_true",
            help="Shorthand for --linters ruff,flake8",
        )
        parser.add_argument(
            "--max-cc",
            type=int,
            default=None,
            metavar="N",
            help="Fail analysis if any function exceeds this cyclomatic complexity",
        )
        parser.add_argument(
            "--workers",
            type=int,
            default=None,
            metavar="N",
            help="Parallel worker processes (clamped to 1..4 to bound memory)",
        )
        parser.add_argument(
            "--no-cache",
            action="store_true",
            help="Disable the incremental per-file analysis cache",
        )

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the analyze command.

        Args:
            args: Parsed command-line arguments.

        Returns:
            Exit code (0 for success).
        """
        scopes = ["all", "i18n", "security", "performance", "architecture", "metadata"]

        # ``--scope`` is the explicit form; keep ``analyze [scope] [path]``
        # working for backward compatibility.
        if args.scope is not None:
            if args.scope_or_path in scopes:
                raise ValueError("Specify the scope either positionally or with --scope, not both.")
            if args.remaining_path is not None:
                raise ValueError("Only one project path can be specified.")
            args.project_path = args.scope_or_path
        elif args.scope_or_path in scopes:
            args.scope = args.scope_or_path
            args.project_path = args.remaining_path or "."
        else:
            args.scope = "all"
            args.project_path = args.scope_or_path

        handle_analyze(args)
        return 0
