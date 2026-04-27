"""CLI Application orchestrator."""

import argparse
import pathlib
import sys
from typing import Dict, List, Optional

from ..utils import logger, setup_logger
from .base import BaseCommand
from .commands import (
    AnalyzeCommand,
    FixCommand,
    GraphCommand,
    InitCommand,
    ListRulesCommand,
    SecurityCommand,
    ServeCommand,
    SummaryCommand,
    VersionCommand,
)


class CLIApp:
    """Main CLI application orchestrator.

    Manages command registration, argument parsing, and execution.
    """

    def __init__(self):
        """Initialize the CLI application with all available commands."""
        self.commands: Dict[str, BaseCommand] = self._discover_commands()

    def _discover_commands(self) -> Dict[str, BaseCommand]:
        """Auto-discover and instantiate all command classes.

        Returns:
            Dictionary mapping command names to command instances.
        """
        command_classes: List[type[BaseCommand]] = [
            AnalyzeCommand,
            SecurityCommand,
            FixCommand,
            GraphCommand,
            ServeCommand,
            ListRulesCommand,
            InitCommand,
            SummaryCommand,
            VersionCommand,
        ]
        return {cmd().name: cmd() for cmd in command_classes}

    def _build_parser(self) -> argparse.ArgumentParser:
        """Build the argument parser with all commands.

        Returns:
            Configured ArgumentParser instance.
        """
        from .. import __version__

        parser = argparse.ArgumentParser(
            description="QGIS Plugin Analyzer - A guardian for your PyQGIS code"
        )
        parser.add_argument(
            "-v", "--version", action="version", version=f"%(prog)s {__version__}"
        )
        subparsers = parser.add_subparsers(dest="command", help="Command to execute")

        # Register all commands
        for cmd in self.commands.values():
            cmd_parser = subparsers.add_parser(cmd.name, help=cmd.help)
            cmd.configure_parser(cmd_parser)

        return parser

    def _parse_args(
        self, parser: argparse.ArgumentParser, argv: Optional[List[str]] = None
    ) -> argparse.Namespace:
        """Parse command-line arguments with legacy support.

        Args:
            parser: The argument parser.
            argv: Optional argument list (defaults to sys.argv).

        Returns:
            Parsed arguments namespace.
        """
        if argv is None:
            argv = sys.argv[1:]

        # Legacy support: default to 'analyze' if first arg is a path
        if argv and argv[0] not in self.commands and not argv[0].startswith("-"):
            argv.insert(0, "analyze")

        return parser.parse_args(argv)

    def _setup_logging(self, args: argparse.Namespace) -> None:
        """Setup logging based on command arguments.

        Args:
            args: Parsed command-line arguments.
        """
        output_dir = pathlib.Path(
            getattr(args, "output", "./analysis_results")
        ).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        setup_logger(output_dir)

    def _execute_command(self, args: argparse.Namespace) -> int:
        """Execute the selected command.

        Args:
            args: Parsed command-line arguments.

        Returns:
            Exit code from command execution.
        """
        if not args.command or args.command not in self.commands:
            return 1

        command = self.commands[args.command]
        return command.execute(args)

    def run(self, argv: Optional[List[str]] = None) -> int:
        """Run the CLI application.

        Args:
            argv: Optional argument list (defaults to sys.argv).

        Returns:
            Exit code (0 for success, non-zero for failure).
        """
        parser = self._build_parser()

        try:
            args = self._parse_args(parser, argv)

            if not args.command:
                parser.print_help()
                return 0

            self._setup_logging(args)
            return self._execute_command(args)

        except KeyboardInterrupt:
            logger.info("\n⏹️ Analysis interrupted.")
            return 1
        except FileNotFoundError as e:
            logger.error(f"Error: File not found: {e}")
            return 1
        except ValueError as e:
            logger.error(f"Error: {e}")
            return 1
        except Exception as e:
            logger.critical(f"Critical Error: {e}", exc_info=True)
            return 1
