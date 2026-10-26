"""Security command implementation."""

import argparse

from ...commands import handle_security
from ..base import BaseAnalyzerCommand


class SecurityCommand(BaseAnalyzerCommand):
    """Command to execute focused security checks."""

    @property
    def name(self) -> str:
        """Command name."""
        return "security"

    @property
    def help(self) -> str:
        """Command help text."""
        return "Run focused security audit on the plugin"

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure security command arguments.

        Args:
            parser: The argument parser for this command.
        """
        parser.add_argument("project_path", help="Path to the QGIS project to analyze")
        self.add_common_args(parser)
        parser.add_argument(
            "-d",
            "--deep",
            action="store_true",
            default=None,
            help="Enable entropy and full secrets detection (default: profile)",
        )
        parser.add_argument(
            "--tools",
            default=None,
            metavar="LIST",
            help="Comma-separated tools: native,bandit,detect-secrets,flake8 (default: native)",
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Emit a machine-readable security report to stdout",
        )
        parser.add_argument(
            "--fail-on",
            choices=["critical", "warning", "info", "none"],
            default=None,
            help="Lowest severity that fails (default: profile security_fail_on, or critical)",
        )
        parser.add_argument(
            "--exclude",
            action="append",
            default=None,
            metavar="PATTERN",
            help="Additional ignore pattern (repeatable/comma-separated; ! re-includes)",
        )
        parser.add_argument(
            "--no-cache",
            action="store_true",
            help="Disable the incremental per-file analysis cache",
        )

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the security command.

        Args:
            args: Parsed command-line arguments.

        Returns:
            Exit code (0 for success).
        """
        handle_security(args)
        return 0
