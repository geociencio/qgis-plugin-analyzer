"""Init command implementation."""

import argparse

from ...commands import handle_init
from ..base import BaseCommand


class InitCommand(BaseCommand):
    """Command to initialize a new .analyzerignore with defaults."""

    @property
    def name(self) -> str:
        """Command name."""
        return "init"

    @property
    def help(self) -> str:
        """Command help text."""
        return "Initialize a new .analyzerignore with defaults"

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure init command arguments.

        Args:
            parser: The argument parser for this command.
        """
        # No additional arguments needed
        pass

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the init command.

        Args:
            args: Parsed command-line arguments.

        Returns:
            Exit code (0 for success).
        """
        handle_init()
        return 0
