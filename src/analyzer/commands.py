"""Command handlers for the QGIS Plugin Analyzer CLI.

This module contains the implementation of individual CLI commands to separate
interface definition (cli.py) from execution logic.
"""

import argparse
import dataclasses
import json
import logging
import pathlib
import sys
from typing import Any, cast

from .engine import ProjectAnalyzer
from .fixer import AutoFixer
from .reporters.summary_reporter import report_summary
from .rules import get_qgis_audit_rules
from .utils import DEFAULT_EXCLUDE
from .utils.performance_utils import set_progress_quiet
from .utils.stale_cache import detect_stale_cache


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
    scope = getattr(args, "scope", "all")
    as_json = getattr(args, "json", False)
    max_cc = getattr(args, "max_cc", None)

    if as_json:
        _route_logs_to_stderr()

    _warn_legacy_output_dir(pathlib.Path(project_path))

    analyzer = ProjectAnalyzer(
        str(project_path), output_dir, profile, workers=getattr(args, "workers", None)
    )
    _apply_config_overrides(analyzer, args)

    success = analyzer.run(scope=scope)

    context_path = analyzer.output_dir / "project_context.json"
    if context_path.exists():
        if as_json:
            _emit_json(context_path, max_cc)
        else:
            _report_and_gate(context_path, max_cc)

    if not success:
        sys.exit(1)


def _apply_config_overrides(analyzer: ProjectAnalyzer, args: argparse.Namespace) -> None:
    """Applies CLI overrides onto the analyzer's configuration.

    Args:
        analyzer: The analyzer whose config is overridden.
        args: Parsed command-line arguments.
    """
    if getattr(args, "strict", False):
        analyzer.config = dataclasses.replace(analyzer.config, strict=True)
    if getattr(args, "report", False):
        analyzer.config = dataclasses.replace(analyzer.config, generate_html=True)
    if getattr(args, "include_content", False):
        analyzer.config = dataclasses.replace(analyzer.config, include_content=True)
    if getattr(args, "no_cache", False):
        analyzer.config = dataclasses.replace(analyzer.config, cache=False)


def _load_context(context_path: pathlib.Path) -> dict[str, Any]:
    """Loads the persisted analysis context JSON.

    Args:
        context_path: Path to ``project_context.json``.

    Returns:
        The parsed analysis context.
    """
    with open(context_path, encoding="utf-8") as f:
        return cast(dict[str, Any], json.load(f))


def _emit_json(context_path: pathlib.Path, max_cc: int | None) -> None:
    """Writes the analysis context as JSON to stdout.

    Args:
        context_path: Path to ``project_context.json``.
        max_cc: Optional cyclomatic complexity gate; when set, the gate result
            is embedded in the emitted JSON.
    """
    data = _load_context(context_path)
    if max_cc is not None:
        cc_result = _enforce_max_cc(data.get("modules", []), max_cc)
        data["cc_gate"] = cc_result["gate"]
        data["cc_violations"] = cc_result["violations"]
    sys.stdout.write(json.dumps(data))


def _report_and_gate(context_path: pathlib.Path, max_cc: int | None) -> None:
    """Prints the human-readable summary and enforces the complexity gate.

    Args:
        context_path: Path to ``project_context.json``.
        max_cc: Optional cyclomatic complexity gate.

    Raises:
        SystemExit: When the complexity gate fails (exit code 1).
    """
    report_summary(context_path)
    if max_cc is None:
        return

    data = _load_context(context_path)
    cc_result = _enforce_max_cc(data.get("modules", []), max_cc)
    for violation in cc_result["violations"]:
        print(
            f"  - {violation['path']}:{violation['line']} -> "
            f"{violation['name']} (CC={violation['complexity']})"
        )
    if cc_result["gate"] == "FAIL":
        print(
            f"❌ Cyclomatic complexity gate failed: "
            f"{len(cc_result['violations'])} function(s) exceed --max-cc {max_cc}."
        )
        sys.exit(1)


def _enforce_max_cc(modules_data: list[dict[str, Any]], max_cc: int) -> dict[str, Any]:
    """Collects functions exceeding the maximum cyclomatic complexity.

    Args:
        modules_data: List of module analysis dicts (from project_context.json).
        max_cc: Maximum allowed cyclomatic complexity per function.

    Returns:
        Dict with ``gate`` ("PASS" or "FAIL") and ``violations`` list.
    """
    violations: list[dict[str, Any]] = []
    for mod in modules_data:
        path = mod.get("path", "")
        for func in mod.get("functions", []):
            cc = func.get("complexity", 0)
            if cc > max_cc:
                violations.append(
                    {
                        "path": path,
                        "name": func.get("name", ""),
                        "line": func.get("line", 0),
                        "complexity": cc,
                    }
                )
    violations.sort(key=lambda v: v["complexity"], reverse=True)
    return {"gate": "FAIL" if violations else "PASS", "violations": violations}


def _route_logs_to_stderr() -> None:
    """Redirects console log output to stderr so stdout stays machine-readable."""
    logger = logging.getLogger("qgis_analyzer")
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler) and handler.stream is sys.stdout:
            handler.setStream(sys.stderr)
    set_progress_quiet(True)


def _warn_legacy_output_dir(project_path: pathlib.Path) -> None:
    """Warns when a legacy output location (json/project_context.json) is detected."""
    legacy = project_path / "json" / "project_context.json"
    if legacy.exists():
        logging.getLogger("qgis_analyzer").warning(
            f"⚠️  Legacy output directory detected at {legacy}. "
            "Results are now written to the canonical --output directory."
        )


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

    if input_path.exists():
        warning = detect_stale_cache(input_path)
        if warning:
            print(f"\n\033[93m{warning}\033[0m\n")

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
    _apply_config_overrides(analyzer, args)

    if hasattr(args, "deep") and args.deep:
        print("🔍 Deep scan enabled (Entropy analysis and full secret detection)")

    success = analyzer.run()

    context_path = analyzer.output_dir / "project_context.json"
    if context_path.exists():
        # Use the specialized security reporter
        report_summary(context_path, by="security")

    if not success:
        sys.exit(1)
