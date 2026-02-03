"""Security command implementation."""

import argparse

from ...commands import handle_security
from ..base import BaseCommand


class SecurityCommand(BaseCommand):
    """Command to run a focused security scan."""

    @property
    def name(self) -> str:
        """Command name."""
        return "security"

    @property
    def help(self) -> str:
        """Command help text."""
        return "Run a focused security scan"

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure security command arguments.

        Args:
            parser: The argument parser for this command.
        """
        parser.add_argument("project_path", help="Path to the QGIS project to scan")
        self.add_common_args(parser)
        parser.add_argument(
            "--deep",
            action="store_true",
            help="Run more intensive (but slower) security checks",
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
