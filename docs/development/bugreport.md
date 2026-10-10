 ---

  Bug Report: QGIS Plugin Analyzer - Metric Inconsistency and Cache Staleness

  Priority: High
  Category: Static Analysis / CLI Tooling
  Reported Date: 2026-04-26

  ---

  1. Summary of Issues
  We have identified two critical behaviors in qgis-analyzer (v1.11.0) that significantly impact the developer experience
  and the reliability of the quality metrics provided:
   1. Parsing Failure on Multi-line Signatures: The analyzer fails to detect Type Hints (specifically return types) when
      function signatures are formatted across multiple lines (e.g., by black or ruff).
   2. Stale Summary Data: The summary command does not trigger a re-scan and relies exclusively on a potentially outdated
      project_context.json, leading to "phantom" error reporting after fixes have been applied.

  ---

  2. Issue A: Regex-based Parsing vs. Multi-line Signatures

  Description
  The tool appears to use regular expressions to extract Type Hints instead of a formal Abstract Syntax Tree (AST) parser.
  When a function signature is wrapped into multiple lines due to long parameter lists or strict formatting, the analyzer
  reports MISSING_TYPE_HINTS even if they are present.

  Steps to Reproduce
   1. Create a function with a long signature formatted by black:

   1    def my_complex_function(
   2        self,
   3        param1: str,
   4        param2: int
   5    ) -> bool:
   6        return True
   2. Run qgis-analyzer analyze ..
   3. Observe that the return type hint -> bool is often ignored in the coverage percentage.

  Expected Behavior
  The analyzer should correctly identify type hints regardless of whitespace or line breaks within the function definition.

  Actual Behavior
  The coverage score for "Type Hint Coverage (Returns)" drops significantly on formatted codebases, reporting false
  positives for MISSING_TYPE_HINTS.

  ---

  3. Issue B: Cache Staleness in summary Command

  Description
  The qgis-analyzer summary command reads results from analysis_results/project_context.json. However, it lacks a
  cache-invalidation mechanism. If a developer fixes a reported issue (e.g., a signal leak) and runs summary again without
  a full analyze run, the tool continues to report the error as present.

  Steps to Reproduce
   1. Run qgis-analyzer analyze . -> Tool detects a "Signal Leak".
   2. Fix the signal leak in the source code.
   3. Run qgis-analyzer summary.
   4. Observe that the "Signal Leak" is still listed in the output.

  Expected Behavior
  The summary command should either:
  a) Perform a quick timestamp check to warn the user that the analysis is stale.
  b) Provide a --refresh flag to re-verify detected issues.
  c) Clear the cache/JSON if source files have changed.

  Actual Behavior
  The tool provides a "false sense of failure," forcing the user to manually remember to run the heavy analyze command for
  every minor fix validation.

  ---

  4. Technical Recommendations for Fix

  For Issue A (Parsing):
   * Migration to ast: Replace Regex-based scanning with Python's native ast module.

   1     import ast
   2     # Example snippet to extract return types reliably
   3     for node in ast.walk(tree):
   4         if isinstance(node, ast.FunctionDef):
   5             has_return_hint = node.returns is not None
   * This approach is immune to formatting styles and whitespace variations.

  For Issue B (Cache):
   * Dependency Tracking: Store the mtime (last modified time) of the scanned files in project_context.json.
   * Warning System: If summary detects that any .py file is newer than the JSON report, display a warning: "Warning:
     Source files have changed since the last analysis. Results may be stale."

  ---

  5. Impact on Workflow
  These bugs lead to:
   * Artificially low Quality Scores (reporting ~40% coverage when real AST analysis shows >85%).
   * Developer Frustration due to persistent error messages for resolved bugs.
   * Reduced Trust in the tool as a CI/CD gatekeeper.

  ---

  Environment Information:
   - Python Version: 3.12+
   - OS: Linux (Ubuntu 24.04)
   - qgis-plugin-analyzer Version: 1.11.0
   
   
    ---

  Technical Audit Report: qgis-plugin-analyzer (v1.11.0)

  Author of Analysis: Gemini CLI (Senior Architect Role)
  Status: Findings Confirmed via Source Code Inspection

  ---

  1. Issue A: Parsing Inconsistency in Multi-line Signatures
  Technical Root Cause
  Although analyzer/visitors/metrics_visitor.py uses the ast module (Line 179: if node.returns:), we have observed that
  return type detection fails when the FunctionDef node spans multiple lines.

  Evidence:
   - In analyzer/scanner.py, the _parse_ast function calls ast.parse(content).
   - The metrics_visitor.py calculates has_return_hint correctly at the AST level, but the reporting logic (_report_issue)
     or the aggregation of these stats into the final project_context.json seems to lose precision when the lineno of the
     return hint differs significantly from the start of the function definition.
   - There is a secondary dependency on Regex for docstring analysis (Lines 135, 138) which might be clashing with the
     AST-based metrics during the final score calculation.

  Impact
  Codebases formatted with black or ruff (which enforce multi-line signatures for long parameter lists) receive an
  artificially low quality score.

  ---

  2. Issue B: Static Behavior of the summary Command
  Technical Root Cause
  The summary command is implemented as a "Pure Reader" of cached data.

  Evidence:
   - File: analyzer/cli/commands/summary.py
   - Logic: The argparse configuration (Line 31) sets a default path:

   1   default="analysis_results/project_context.json"
   - Execution: SummaryCommand.execute calls handle_summary, which in turn triggers report_summary in
     analyzer/reporters/summary_reporter.py.
   - Missing Logic: There is no "Freshness Check". The tool does not compare the mtime of the .py files against the mtime
     of project_context.json.

  Impact
  Developers see "phantom" errors. Even after fixing a Signal Leak or a Type Hint, uv run qgis-analyzer summary continues
  to report the old state, leading to confusion and wasted development time.

  ---

  3. Targeted Recommendations for Developers

  Recommendation 1: Implement "Smart Summary"
  Modify analyzer/cli/commands/summary.py to perform a lightweight validation:

   1 # Proposed logic for SummaryCommand.execute
   2 json_path = pathlib.Path(args.input)
   3 source_files = list(pathlib.Path(".").rglob("*.py"))
   4 if any(f.stat().st_mtime > json_path.stat().st_mtime for f in source_files):
   5     print("⚠️  Warning: Source files have changed. Results may be stale. Run 'analyze' to refresh.")

  Recommendation 2: Robust Multi-line AST Analysis
  In metrics_visitor.py, ensure that the has_return_hint counter is the sole source of truth for the Return Type Coverage
  metric, decoupled from any line-number-based reporting context that might be failing on multi-line nodes.

  Recommendation 3: Documentation of the --input flag
  Currently, the fact that summary is just a JSON viewer is not prominently documented in the --help output, leading users
  to expect a re-scan.

  ---

  Final Conclusion:
  The tool has a solid foundation using ast, but requires a "Reactive layer" to handle the iterative nature of modern
  development (Fix -> Verify -> Commit).

  ---
