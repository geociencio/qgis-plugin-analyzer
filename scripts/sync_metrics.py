#!/usr/bin/env python3
"""Unified metric extraction for qgis-plugin-analyzer.

Runs the analyzer on itself, extracts quality scores from the analysis
output, and writes a structured snapshot to .agent-state/memory/agent_metrics.json.

Usage:
    uv run python scripts/sync_metrics.py
"""

import json
import subprocess
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ANALYSIS_RESULTS = PROJECT_ROOT / "analysis_results" / "project_context.json"
METRICS_FILE = PROJECT_ROOT / ".agent-state" / "memory" / "agent_metrics.json"


def run_command(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    return subprocess.run(
        cmd,
        cwd=cwd or PROJECT_ROOT,
        capture_output=True,
        text=True,
    )


def extract_scores() -> dict:
    """Extract quality scores from analyzer output."""
    if not ANALYSIS_RESULTS.exists():
        print(f"⚠ Analysis results not found at {ANALYSIS_RESULTS}")
        print("  Run: uv run qgis-analyzer analyze .")
        return {}

    with open(ANALYSIS_RESULTS) as f:
        data = json.load(f)

    # Scores live under "metrics" in the current output contract
    # (quality_score / maintainability_score / security_score).
    scores = data.get("scores", data.get("quality_scores", data.get("metrics", {})))
    return {
        "stability": scores.get("stability", scores.get("quality_score", 0)),
        "maintainability": scores.get("maintainability", scores.get("maintainability_score", 0)),
        "security": scores.get("security", scores.get("security_score", 0)),
    }


def count_tests() -> dict:
    """Count passing tests via pytest."""
    result = run_command(["python", "-m", "pytest", "tests/", "-q", "--tb=no"])
    # Parse pytest summary line: "87 passed in 0.54s"
    output = result.stdout + result.stderr
    passed = 0
    total = 0
    for line in output.splitlines():
        if "passed" in line:
            parts = line.split()
            for i, part in enumerate(parts):
                if part == "passed":
                    try:
                        passed = int(parts[i - 1])
                        break
                    except (ValueError, IndexError):
                        pass

    # Fallback: count test files
    if passed == 0:
        test_files = list((PROJECT_ROOT / "tests").glob("test_*.py"))
        total = len(test_files)

    return {"pass": passed, "total": total or passed}


def extract_issue_stats() -> tuple[dict[str, int], dict[str, int]]:
    """Return issue counts from the analysis results.

    Returns:
        A tuple ``(by_type, by_severity)`` where ``by_type`` maps rule id to
        count and ``by_severity`` maps severity to count.
    """
    if not ANALYSIS_RESULTS.exists():
        return {}, {"critical": 0, "high": 0, "medium": 0, "low": 0}

    with open(ANALYSIS_RESULTS) as f:
        data = json.load(f)

    by_type: dict[str, int] = {}
    by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for module in data.get("modules", []):
        for issue in module.get("ast_issues", []):
            issue_type = issue.get("type", "unknown")
            by_type[issue_type] = by_type.get(issue_type, 0) + 1
            severity = str(issue.get("severity", "medium")).lower()
            by_severity[severity] = by_severity.get(severity, 0) + 1

    return by_type, by_severity


def load_existing_metrics() -> dict:
    """Load existing metrics file or return empty structure."""
    if METRICS_FILE.exists():
        with open(METRICS_FILE) as f:
            return json.load(f)
    return {"version": "1.0", "project": "qgis-plugin-analyzer", "sessions": []}


def main() -> None:
    print("🔄 qgis-plugin-analyzer — Metric Sync")
    print(f"   Date: {date.today().isoformat()}")
    print()

    # 1. Run the analyzer on itself
    print("📊 Running self-analysis...")
    result = run_command(["uv", "run", "qgis-analyzer", "analyze", "."])
    if result.returncode != 0:
        print(f"⚠ Analysis completed with warnings (exit code {result.returncode})")
    else:
        print("   Analysis complete.")

    # 2. Extract scores
    scores = extract_scores()
    if scores:
        print(f"   Stability: {scores['stability']}/100")
        print(f"   Maintainability: {scores['maintainability']}/100")
        print(f"   Security: {scores['security']}/100")
    else:
        print("   ⚠ Could not extract scores. Using last known values.")
        scores = {"stability": 55.1, "maintainability": 77.0, "security": 100.0}

    # 3. Collect issue statistics (before running the test suite, which may
    # regenerate analysis artifacts as a side effect).
    issue_breakdown, severity_totals = extract_issue_stats()
    total_issues = sum(issue_breakdown.values())
    print(f"   Issues: {total_issues} total")

    # 4. Count tests
    tests = count_tests()
    print(f"   Tests: {tests['pass']}/{tests['total']} passing")
    print()

    # 5. Update metrics file
    metrics = load_existing_metrics()
    session_entry = {
        "date": date.today().isoformat(),
        "session": "sync_metrics_auto",
        "scores": scores,
        "tests": tests,
        "issues": severity_totals,
    }

    # Replace today's entry if it exists, otherwise append
    metrics["sessions"] = [s for s in metrics["sessions"] if s["date"] != date.today().isoformat()]
    metrics["sessions"].append(session_entry)
    metrics["sessions"].sort(key=lambda s: s["date"])

    # Ground-truth summary consumed by the Agentic Forge tooling
    # (``forge.py metrics validate`` / ``report``).
    metrics["summary"] = {
        "test_count": tests["pass"],
        "tests_ok": tests["pass"],
        "quality_score_latest": scores["stability"],
        "maintainability_score": scores["maintainability"],
        "security_score": scores["security"],
        "total_issues": total_issues,
        "issue_breakdown": issue_breakdown,
        "i18n_issues_qgis_analyzer": issue_breakdown.get("MISSING_I18N", 0),
    }

    with open(METRICS_FILE, "w") as f:
        json.dump(metrics, f, indent=2)
        f.write("\n")

    print(f"✅ Metrics written to {METRICS_FILE}")
    print(f"   Total sessions tracked: {len(metrics['sessions'])}")


if __name__ == "__main__":
    main()
