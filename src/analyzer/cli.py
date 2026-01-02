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

from .engine import ProjectAnalyzer
from .utils import logger, setup_logger


def _setup_argument_parser() -> argparse.ArgumentParser:
    """Sets up and returns the argument parser with all subcommands.

    Returns:
        A configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        description="QGIS Plugin Analyzer - A guardian for your PyQGIS code"
    )
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
        "-p",
        "--profile",
        help="Configuration profile from pyproject.toml",
        default="default",
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

    # Init Command
    subparsers.add_parser("init", help="Initialize a new .analyzerignore with defaults")

    return parser


def _handle_fix_command(args: argparse.Namespace) -> bool:
    """Handles the execution of the 'fix' command.

    Args:
        args: Parsed command line arguments.

    Returns:
        True if the fix process completed successfully, False otherwise.
    """
    import json

    from .fixer import AutoFixer

    project_path = pathlib.Path(args.path).resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        return False

    # Run analysis first
    print("🔍 Analyzing project for fixable issues...")
    analyzer = ProjectAnalyzer(
        str(project_path),
        args.output if hasattr(args, "output") else "./analysis_results",
        args.profile if hasattr(args, "profile") else "default",
    )
    analyzer.run()

    # Load issues
    context_file = analyzer.output_dir / "project_context.json"
    with open(context_file) as f:
        context = json.load(f)

    all_issues = []
    for module in context.get("modules", []):
        all_issues.extend(module.get("ast_issues", []))

    if args.rules:
        rule_ids = [r.strip() for r in args.rules.split(",")]
        all_issues = [i for i in all_issues if i.get("type") in rule_ids]

    fixer = AutoFixer(project_path, dry_run=not args.apply)
    fixable = fixer.get_fixable_issues(all_issues)

    if not fixable:
        print("✅ No fixable issues found!")
        return True

    print(f"\n📋 Found {len(fixable)} fixable issue(s)")
    if not args.apply:
        print("\n⚠️  DRY RUN MODE (use --apply to execute changes)\n")

    stats = fixer.apply_fixes(fixable, interactive=not args.auto_approve)
    print(
        f"\n📊 Summary: Applied: {stats['applied']}, Skipped: {stats['skipped']}, Failed: {stats['failed']}"
    )
    return True


def _handle_analyze_command(args: argparse.Namespace) -> None:
    """Handles the execution of the 'analyze' command.

    Args:
        args: Parsed command line arguments.
    """
    analyzer = ProjectAnalyzer(args.project_path, args.output, args.profile)
    analyzer.run()


def _handle_list_rules_command() -> None:
    """Handles the 'list-rules' command by displaying available audit rules."""
    from .rules import get_qgis_audit_rules

    rules = get_qgis_audit_rules()
    print("\n📋 QGIS Audit Rules Catalog:")
    print("=" * 30)
    for r in rules:
        print(f"- [{r['severity'].upper()}] {r['id']}: {r['message']}")
    print(f"\nTotal: {len(rules)} rules.\n")


def _handle_init_command() -> None:
    """Handles the 'init' command by creating a default .analyzerignore file."""
    from .utils import DEFAULT_EXCLUDE

    ignore_file = pathlib.Path(".analyzerignore")
    if ignore_file.exists():
        print("⚠️  .analyzerignore already exists. Skipping.")
    else:
        with open(ignore_file, "w") as f:
            f.write("# QGIS Plugin Analyzer Ignore File\n")
            for p in DEFAULT_EXCLUDE:
                f.write(f"{p}\n")
        print("✅ Created .analyzerignore with default excludes.")


def main() -> None:
    """Main entry point for the QGIS Plugin Analyzer CLI.

    Orchestrates the command execution based on parsed arguments and
    sets up the global logging environment.
    """
    parser = _setup_argument_parser()

    # Legacy support / default to analyze if no command provided
    if len(sys.argv) > 1 and sys.argv[1] not in [
        "analyze",
        "fix",
        "list-rules",
        "init",
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

    try:
        if args.command == "fix":
            _handle_fix_command(args)
        elif args.command == "analyze":
            _handle_analyze_command(args)
        elif args.command == "list-rules":
            _handle_list_rules_command()
        elif args.command == "init":
            _handle_init_command()
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
