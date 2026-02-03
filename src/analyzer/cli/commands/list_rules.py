"""List rules command implementation."""

import argparse

from ...commands import handle_list_rules
from ..base import BaseCommand


class ListRulesCommand(BaseCommand):
    """Command to list all available QGIS audit rules."""

    @property
    def name(self) -> str:
        """Command name."""
        return "list-rules"

    @property
    def help(self) -> str:
        """Command help text."""
        return "List all available QGIS audit rules"

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure list-rules command arguments.

        Args:
            parser: The argument parser for this command.
        """
        # No additional arguments needed
        pass

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the list-rules command.

        Args:
            args: Parsed command-line arguments.

        Returns:
            Exit code (0 for success).
        """
        handle_list_rules()
        return 0
