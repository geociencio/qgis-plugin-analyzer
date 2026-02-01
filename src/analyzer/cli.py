# /***************************************************************************
#  QGIS Plugin Analyzer
#                                  A QGIS tool
#  Static code analysis and standards audit for QGIS plugins.
#                               -------------------
#         begin                : 2025-12-28
#         git sha              : $Format:%H$
#         copyright            : (C) 2025 by Juan M Bernales
#         email                : juanbernales@gmail.com
#  ***************************************************************************/
#
# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/


import argparse
import pathlib
import sys

from . import __version__
from .commands import (
    handle_analyze,
    handle_fix,
    handle_init,
    handle_list_rules,
    handle_security,
    handle_summary,
)
from .utils import logger, setup_logger


def _setup_argument_parser() -> argparse.ArgumentParser:
    """Sets up and returns the argument parser with all subcommands.

    Returns:
        A configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        description="QGIS Plugin Analyzer - A guardian for your PyQGIS code"
    )
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Analyze Command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze an existing QGIS plugin")
    analyze_parser.add_argument("project_path", help="Path to the QGIS project to analyze")
    analyze_parser.add_argument(
        "-o",
        "--output",
        help="Output directory for reports",
        default="./analysis_results",
    )
    analyze_parser.add_argument(
        "-r",
        "--report",
        action="store_true",
        help="Generate detailed HTML/Markdown reports",
    )
    analyze_parser.add_argument(
        "-p",
        "--profile",
        help="Configuration profile from pyproject.toml",
        default="default",
    )

    # Security Command
    security_parser = subparsers.add_parser("security", help="Run a focused security scan")
    security_parser.add_argument("project_path", help="Path to the QGIS project to scan")
    security_parser.add_argument(
        "-o",
        "--output",
        help="Output directory for reports",
        default="./analysis_results",
    )
    security_parser.add_argument(
        "-p",
        "--profile",
        help="Configuration profile from pyproject.toml",
        default="default",
    )
    security_parser.add_argument(
        "--deep",
        action="store_true",
        help="Run more intensive (but slower) security checks",
    )

    # Fix Command
    fix_parser = subparsers.add_parser("fix", help="Auto-fix common QGIS plugin issues")
    fix_parser.add_argument("path", type=str, help="Path to the QGIS plugin directory")
    fix_parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Show proposed changes without applying (default: True)",
    )
    fix_parser.add_argument("--apply", action="store_true", help="Apply fixes (disables dry-run)")
    fix_parser.add_argument(
        "--auto-approve",
        action="store_true",
        help="Apply all fixes without confirmation",
    )
    fix_parser.add_argument(
        "-p",
        "--profile",
        help="Configuration profile from pyproject.toml",
        default="default",
    )
    fix_parser.add_argument(
        "--rules",
        type=str,
        help="Comma-separated list of rule IDs to fix",
    )

    # List Rules Command
    subparsers.add_parser("list-rules", help="List all available QGIS audit rules")

    # Version Command
    subparsers.add_parser("version", help="Show the current version of the analyzer")

    # Init Command
    subparsers.add_parser("init", help="Initialize a new .analyzerignore with defaults")

    # Summary Command
    summary_parser = subparsers.add_parser(
        "summary", help="Show a quick terminal summary of analysis results"
    )
    summary_parser.add_argument(
        "-i",
        "--input",
        help="Path to the research JSON file",
        default="analysis_results/project_context.json",
    )
    summary_parser.add_argument(
        "-b",
        "--by",
        choices=["total", "modules", "functions", "classes"],
        default="total",
        help="Granularity of the summary (default: total)",
    )

    return parser


def main() -> None:
    """Main entry point for the QGIS Plugin Analyzer CLI.

    Orchestrates the command execution based on parsed arguments and
    sets up the global logging environment.
    """
    parser = _setup_argument_parser()

    # Legacy support / default to analyze if no command provided
    if len(sys.argv) > 1 and sys.argv[1] not in [
        "analyze",
        "security",
        "version",
        "fix",
        "list-rules",
        "init",
        "summary",
        "-h",
        "--help",
    ]:
        # If the first argument is a path (doesn't start with -), assume 'analyze'
        if not sys.argv[1].startswith("-"):
            sys.argv.insert(1, "analyze")

    args = parser.parse_args()

    # Initialize logger (default to analysis_results if not specified)
    output_dir = pathlib.Path(getattr(args, "output", "./analysis_results")).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    setup_logger(output_dir)

    # Command Dispatcher
    dispatch = {
        "fix": lambda: handle_fix(args),
        "analyze": lambda: handle_analyze(args),
        "list-rules": lambda: handle_list_rules(),
        "init": lambda: handle_init(),
        "summary": lambda: handle_summary(args),
        "security": lambda: handle_security(args),
        "version": lambda: print(f"qgis-analyzer {__version__}"),
    }

    try:
        if args.command in dispatch:
            dispatch[args.command]()
        else:
            parser.print_help()

    except KeyboardInterrupt:
        logger.info("\n⏹️ Analysis interrupted.")
        sys.exit(1)
    except FileNotFoundError as e:
        logger.error(f"Error: File not found: {e}")
        sys.exit(1)
    except ValueError as e:
        # This handles path traversal or other validation errors
        logger.error(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Critical Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
