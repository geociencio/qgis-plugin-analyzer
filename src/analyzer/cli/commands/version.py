"""Version command implementation."""

import argparse

from ... import __version__
from ..base import BaseCommand


class VersionCommand(BaseCommand):
    """Command to show the current version of the analyzer."""

    @property
    def name(self) -> str:
        """Command name."""
        return "version"

    @property
    def help(self) -> str:
        """Command help text."""
        return "Show the current version of the analyzer"

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure version command arguments.

        Args:
            parser: The argument parser for this command.
        """
        # No additional arguments needed
        pass

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the version command.

        Args:
            args: Parsed command-line arguments.

        Returns:
            Exit code (0 for success).
        """
        print(f"qgis-analyzer {__version__}")
        return 0
