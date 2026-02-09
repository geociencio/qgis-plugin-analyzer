"""Base command class for CLI commands."""

import argparse
import pathlib
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..engine import ProjectAnalyzer


class BaseCommand(ABC):
    """Abstract base class for CLI commands.

    Each command encapsulates its own argument configuration and execution logic.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Command name as it appears in the CLI.

        Returns:
            The command name string.
        """

    @property
    @abstractmethod
    def help(self) -> str:
        """Help text for the command.

        Returns:
            A brief description of what the command does.
        """

    @abstractmethod
    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure command-specific arguments.

        Args:
            parser: The argument parser for this command.
        """

    @abstractmethod
    def execute(self, args: argparse.Namespace) -> int:
        """Execute the command.

        Args:
            args: Parsed command-line arguments.

        Returns:
            Exit code (0 for success, non-zero for failure).
        """

    def add_common_args(
        self,
        parser: argparse.ArgumentParser,
        include_output: bool = True,
        include_profile: bool = True,
        include_strict: bool = True,
    ) -> None:
        """Add common arguments shared across multiple commands.

        Args:
            parser: The argument parser to add arguments to.
            include_output: Whether to include the --output argument.
            include_profile: Whether to include the --profile argument.
            include_strict: Whether to include the --strict argument.
        """
        if include_output:
            parser.add_argument(
                "-o",
                "--output",
                help="Output directory for reports",
                default="./analysis_results",
            )
        if include_profile:
            parser.add_argument(
                "-p",
                "--profile",
                help="Configuration profile from pyproject.toml",
                default="default",
            )
        if include_strict:
            parser.add_argument(
                "--strict",
                action="store_true",
                help="Enable strict mode with gold-standard rules",
            )

    def setup_output_dir(self, args: argparse.Namespace) -> Optional[pathlib.Path]:
        """Setup and return the output directory if present in args.

        Args:
            args: Parsed command-line arguments.

        Returns:
            The resolved output directory path, or None if not applicable.
        """
        if hasattr(args, "output"):
            output_dir = pathlib.Path(args.output).resolve()
            output_dir.mkdir(parents=True, exist_ok=True)
            return output_dir
        return None


class BaseAnalyzerCommand(BaseCommand):
    """Base class for commands that use the ProjectAnalyzer engine."""

    def get_analyzer(self, args: argparse.Namespace) -> "ProjectAnalyzer":
        """Initializes and returns a ProjectAnalyzer instance.

        Args:
            args: Parsed command-line arguments.

        Returns:
            A configured ProjectAnalyzer instance.
        """
        import dataclasses

        from ..engine import ProjectAnalyzer

        project_path = getattr(args, "project_path", getattr(args, "path", "."))
        output_dir = getattr(args, "output", "./analysis_results")
        profile = getattr(args, "profile", "default")

        analyzer = ProjectAnalyzer(str(project_path), output_dir, profile)

        # Apply common flags
        updates = {}
        if hasattr(args, "strict") and args.strict:
            updates["strict"] = True
        if hasattr(args, "report") and args.report:
            updates["generate_html"] = True

        if updates:
            analyzer.config = dataclasses.replace(analyzer.config, **updates)

        return analyzer
