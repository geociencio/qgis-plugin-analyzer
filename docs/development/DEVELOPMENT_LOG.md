
# Development Log

## [2026-02-14] Release v1.9.0: Specialized Analysis Subcommands

### Achieved
- **Specialized Subcommands**: Implemented 5 targeted analysis scopes (`i18n`, `security`, `performance`, `architecture`, `metadata`) for the `analyze` command.
- **Backward Compatibility**: Maintained 100% compatibility with legacy `analyze [path]` syntax through manual argument dispatch.
- **Scope-Based Filtering**: Enhanced analysis pipeline to filter issues at multiple levels (visitor reporting, composite aggregation, engine results).
- **Release v1.9.0**: Successfully published release to GitHub with complete documentation and distribution packages.
- **Documentation Overhaul**: Updated README with modern badges (PyPI, downloads, Python versions), "What's New" section, and comprehensive subcommand examples.
- **PyPI Optimization**: Added 10 new trove classifiers for better discoverability (OS Independent, Testing, Utilities, Python 3.13, Console, Typed).
- **CLI Commands Roadmap**: Created comprehensive 3-phase implementation plan for future commands (`fix`, `docs`, `migrate`, `test`, `benchmark`, `init`).

### Technical Details
- Modified `AnalyzeCommand` with manual argument parsing to support both `analyze [scope] [path]` and `analyze [path]` syntax.
- Extended `ProjectAnalyzer.run()` to accept `scope` parameter and propagate it through worker context.
- Implemented `_filter_issues_by_scope()` method to filter results before saving to JSON context.
- Updated all visitors (`BaseVisitor`, `MetricsVisitor`, `StandardsVisitor`, `QGISRulesVisitor`, `SafetyVisitor`) to support scope-aware analysis.
- Enhanced `CompositeVisitor` to activate only relevant visitors based on scope.

### Quality Metrics
- Tests: 49/49 passing (0.39s)
- Module Stability: 45.1/100
- Maintainability: 90.0/100
- Security: 100.0/100
- Type Hints (Params): 97.1%
- Docstrings: 77.9%

### Commits
1. `feat(cli): add specialized subcommands to analyze command` (a45df81)
2. `chore(release): prepare v1.9.0` (5378ad2)
3. `docs(readme): add PyPI badges and improve trove classifiers` (f38c2b0)

### Distribution
- GitHub Release: https://github.com/geociencio/qgis-plugin-analyzer/releases/tag/v1.9.0
- Packages: tar.gz (95K) + wheel (100K)
- Roadmap: `docs/research/CLI_COMMANDS_ROADMAP.md`

## [2026-01-11] AI Context Core Extraction

### Achieved
- **Package Extraction**: Successfully extracted shared AI context logic into a standalone package `ai-context-core`.
- **Modularization**: Refactored `analyze_project_optfixed.py` into modular components (`analyzer.engine`, `analyzer.metrics`, `analyzer.ast_utils`, etc.).
- **New Tools**: Implemented `ai-ctx` CLI with `init` and `analyze` commands.
- **Documentation**: Created full documentation suite in `docs/` (`ARCHITECTURE`, `CONTRIBUTING`, `PROFILES_GUIDE`) and localized it to English.
- **Workflows**: Adapted and translated agent workflows (`start-session`, `end-session`, `create-commit`).

### Technical details
- Structure prepared in `migration/ai-context-core/`, ready for standalone git repository.
- Implemented robust configuration system with YAML profiles.
- Added comprehensive walkthrough and initial report in `docs/reports/initial_extraction.md`.

## [2026-02-01] Security Scanning Integration & CLI Enhancements

### Achieved
- **Security Scanning Logic**: Integrated `QGISSecurityVisitor` (AST) and `SecretScanner` (Regex/Entropy) into the analysis engine.
- **Dedicated Security Command**: Added `security` subcommand for focused scans with specialized terminal reporting.
- **Reporting Enhancements**: Integrated security scores and findings into both Markdown and JSON reports.
- **CLI Robustness**: Fixed bugs in single-file discovery and improved version reporting (`--version`, `version` command).
- **Future Planning**: Researched and documented a roadmap for future QGIS-specific audits.

### Technical details
- New modules: `security_checker.py`, `security_rules.py`, `secrets.py`.
- Refactored `engine.py` to support multi-faceted scoring (Stability, Maintainability, Compliance, Security).
- Modernized CLI dispatcher to support dedicated subcommands and improved argument handling.

## [2026-02-02] Architectural Refactoring & Complexity Reduction

### Achieved
- **Fixer Engine**: Replaced imperative `if-else` block with a **Registry Pattern** and `FixHandler`. Tests now run in-memory without I/O.
- **Visitor Modularization**: Split the monolithic `visitors.py` into a specialized package `visitors/` with separate components (`imports`, `metrics`, `standards`, `security`).
- **CLI Architecture**: Implemented **Command Pattern** in `cli/` to decouple argument parsing from execution. Added unified `BaseCommand`.
- **Reporter Optimization**: Refactored `summary_reporter.py` and `markdown_reporter.py` to significantly reduce cyclomatic complexity by extracting method builders.
- **Validators Fix**: Added missing `scan_for_binaries` and `calculate_package_size` to `validators.py` to fix test regressions.

### Technical details
- New packages: `src/analyzer/visitors/`, `src/analyzer/cli/`.
- Maintainability Score increased to **100/100**.
- Cyclomatic Complexity reduced across all core modules.
- All tests passing (including fixes for `tests/test_validators.py`).

## [2026-02-09] Engine Performance & Architecture Phase

### Achieved
- **Single-Pass AST Traversal**: Refactored `CompositeVisitor` and all specialized sub-visitors to use a hook-based architecture (`enter_node`/`exit_node`). Eliminated redundant tree traversals.
- **Worker Context Optimization**: Implemented `WorkerContext` with process-pool initializers to share rules and project paths, reducing serialization overhead in parallel analysis.
- **Strict QGIS Safety Audit**: Integrated advanced signal/slot leak detection and UI-blocking loop heuristics.
- **I18n Heuristic Precision**: Enhanced translatable string detection with better scope filtering for keys, functions, and non-user-facing patterns.
- **Hybrid Traversal Model**: Visitors now support both optimized single-pass orchestration and independent recursive visitation for testing.

### Technical details
- New modules: `src/analyzer/visitors/qgis_rules_visitor.py`, updated `composite_visitor.py`, `scanner.py`, `base.py`.
- Verified 100% test coverage for the new visitor architecture (43 tests passing).
- Optimized parallel processing via `concurrent.futures.ProcessPoolExecutor` with initializers.
- Local performance verified with `uv run qgis-analyzer analyze .`.
