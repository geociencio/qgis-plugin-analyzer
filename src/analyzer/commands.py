"""Command handlers for the QGIS Plugin Analyzer CLI.

This module contains the implementation of individual CLI commands to separate
interface definition (cli.py) from execution logic.
"""

import argparse
import dataclasses
import json
import pathlib
import sys

from .engine import ProjectAnalyzer
from .fixer import AutoFixer
from .reporters.summary_reporter import report_summary
from .rules import get_qgis_audit_rules
from .utils import DEFAULT_EXCLUDE


def handle_fix(args: argparse.Namespace) -> bool:
    """Handles the execution of the 'fix' command.

    Args:
        args: Parsed command line arguments.

    Returns:
        True if the fix process completed successfully, False otherwise.
    """
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
    if hasattr(args, "strict") and args.strict:
        analyzer.config = dataclasses.replace(analyzer.config, strict=True)

    analyzer.run()

    # Load issues
    context_file = analyzer.output_dir / "project_context.json"
    if not context_file.exists():
        print("❌ Analysis failed to generate context file.")
        return False

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


def handle_analyze(args: argparse.Namespace) -> None:
    """Handles the execution of the 'analyze' command.

    Args:
        args: Parsed command line arguments.
    """
    # Use standard initialization if not already provided
    project_path = getattr(args, "project_path", ".")
    output_dir = getattr(args, "output", "./analysis_results")
    profile = getattr(args, "profile", "default")

    analyzer = ProjectAnalyzer(str(project_path), output_dir, profile)

    # Apply overrides (moving towards centralized config in BaseAnalyzerCommand)
    if hasattr(args, "strict") and args.strict:
        analyzer.config = dataclasses.replace(analyzer.config, strict=True)
    if hasattr(args, "report") and args.report:
        analyzer.config = dataclasses.replace(analyzer.config, generate_html=True)

    success = analyzer.run()

    context_path = analyzer.output_dir / "project_context.json"
    if context_path.exists():
        report_summary(context_path)

    if not success:
        sys.exit(1)


def handle_list_rules() -> None:
    """Handles the 'list-rules' command by displaying available audit rules."""
    rules = get_qgis_audit_rules()
    print("\n📋 QGIS Audit Rules Catalog:")
    print("=" * 30)
    for r in rules:
        print(f"- [{r['severity'].upper()}] {r['id']}: {r['message']}")
    print(f"\nTotal: {len(rules)} rules.\n")


def handle_init() -> None:
    """Handles the 'init' command by creating a default .analyzerignore file."""
    ignore_file = pathlib.Path(".analyzerignore")
    if ignore_file.exists():
        print("⚠️  .analyzerignore already exists. Skipping.")
    else:
        with open(ignore_file, "w") as f:
            f.write("# QGIS Plugin Analyzer Ignore File\n")
            for p in DEFAULT_EXCLUDE:
                f.write(f"{p}\n")
        print("✅ Created .analyzerignore with default excludes.")


def handle_summary(args: argparse.Namespace) -> None:
    """Handles the 'summary' command by displaying a terminal report.

    Args:
        args: Parsed command line arguments.
    """
    input_path = pathlib.Path(args.input).resolve()
    report_summary(input_path, by=args.by)


def handle_security(args: argparse.Namespace) -> None:
    """Handles the execution of the 'security' command.

    Args:
        args: Parsed command line arguments.
    """
    project_path = pathlib.Path(getattr(args, "project_path", ".")).resolve()
    if not project_path.exists():
        print(f"❌ Path not found: {project_path}")
        sys.exit(1)

    print(f"🛡️  Starting focused security scan for: {project_path.name}...")

    output_dir = getattr(args, "output", "./analysis_results")
    profile = getattr(args, "profile", "default")
    analyzer = ProjectAnalyzer(str(project_path), output_dir, profile)

    if hasattr(args, "deep") and args.deep:
        print("🔍 Deep scan enabled (Entropy analysis and full secret detection)")

    success = analyzer.run()

    context_path = analyzer.output_dir / "project_context.json"
    if context_path.exists():
        # Use the specialized security reporter
        report_summary(context_path, by="security")

    if not success:
        sys.exit(1)
