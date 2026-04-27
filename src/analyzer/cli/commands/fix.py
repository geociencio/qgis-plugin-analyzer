"""Fix command implementation."""

import argparse

from ...commands import handle_fix
from ..base import BaseCommand


class FixCommand(BaseCommand):
    """Command to auto-fix common QGIS plugin issues."""

    @property
    def name(self) -> str:
        """Command name."""
        return "fix"

    @property
    def help(self) -> str:
        """Command help text."""
        return "Auto-fix common QGIS plugin issues"

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure fix command arguments.

        Args:
            parser: The argument parser for this command.
        """
        parser.add_argument("path", type=str, help="Path to the QGIS plugin directory")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=True,
            help="Show proposed changes without applying (default: True)",
        )
        parser.add_argument(
            "--apply", action="store_true", help="Apply fixes (disables dry-run)"
        )
        parser.add_argument(
            "--auto-approve",
            action="store_true",
            help="Apply all fixes without confirmation",
        )
        self.add_common_args(parser, include_output=False)
        parser.add_argument(
            "--rules",
            type=str,
            help="Comma-separated list of rule IDs to fix",
        )

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the fix command.

        Args:
            args: Parsed command-line arguments.

        Returns:
            Exit code (0 for success).
        """
        handle_fix(args)
        return 0
