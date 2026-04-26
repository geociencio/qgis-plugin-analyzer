# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.12.0] - 2026-04-26

### Added
- **Framework Upgrade**: Modernized agentic system to Gen 5 architecture. Integrated English-based workflows, specialized skills (`agentic-memory`, `domain-logic`), and global MCP scripts.
- **Scaffold System**: Added `scaffold` blueprints for QGIS and mining specific plugin generation.

### Changed
- Refactored `.agent` directory, unifying conventions and deleting legacy Spanish workflows.
- Adjusted source codebase via `ruff` checks and code formatting.

### Fixed
- **Cache Staleness**: Fixed an issue where the `summary` command read cached JSON data without warning if the underlying source code was modified.
- **Metrics Accuracy**: Refactored `metrics_visitor.py` to robustly detect return type hints on multi-line function signatures, eliminating false positive `MISSING_TYPE_HINTS` violations.

## [1.11.0] - 2026-04-05

### Added
- **Dynamic Versioning**: Implemented a dynamic version retrieval system in `__init__.py` that automatically reads from `pyproject.toml` in development environments, eliminating hardcoded version strings.

### Fixed
- **Project Type Detection**: Fixed a critical bug where QGIS plugins were incorrectly detected as `GENERIC` projects if `metadata.txt` was ignored in `.analyzerignore`. Detección de metadatos ahora tiene prioridad sobre las reglas de ignorado.
- **Engine Logs**: Reduced redundant "Project type" logging messages during analysis.

## [1.10.1] - 2026-03-20

### Fixed
- **Metrics Accuracy**: Added support for `ast.AsyncFunctionDef` parsing in `MetricsVisitor`, rectifying a statistical skew where heavily asynchronous plugins incorrectly showed artificially lowered return type hint coverage.

## [1.10.0] - 2026-02-18

### Fixed
- **Architectural Analysis**: Eliminated false positives in circular dependency detection (`DependencyGraph`) by:
    - Excluding `TYPE_CHECKING` imports from the graph.
    - Implementing canonical deduplication for reported cycles.
    - Validating file existence during import resolution.
- **Module Stability Score**: Fixed a critical bug where the score dropped to 0/100 in large projects due to phantom cycles.

## [1.9.0] - 2026-02-15

### Added
- **Specialized Analysis Subcommands**: Implemented targeted analysis scopes for more efficient auditing:
    - `analyze i18n [path]`: Internationalization and translation audit
    - `analyze security [path]`: Security vulnerability scanning
    - `analyze performance [path]`: Performance and UI blocking detection
    - `analyze architecture [path]`: Dependency and coupling analysis
    - `analyze metadata [path]`: QGIS metadata validation
    - Full backward compatibility maintained with legacy `analyze [path]` syntax
- **CLI Commands Roadmap**: Comprehensive 3-phase implementation plan for future CLI enhancements documented in `docs/research/CLI_COMMANDS_ROADMAP.md`

### Changed
- **Scope-Based Filtering**: Enhanced analysis engine to filter issues based on selected scope throughout the entire pipeline
- **Visitor Architecture**: Extended all visitors to support scope-aware analysis with minimal overhead

### Technical Details
- Manual argument dispatch in `AnalyzeCommand` for subcommand detection
- Scope parameter propagation through worker context to all visitors
- Issue filtering at multiple levels: visitor reporting, composite aggregation, and final result building
- Zero breaking changes - all existing scripts and workflows remain compatible

### Verification
- `analyze i18n .` → 1,150 issues (MISSING_I18N only)
- `analyze .` → 1,266 issues (all types, legacy compatible)

## [1.8.0-beta.1] - 2026-02-14

### Added
- **I18n Differentiation**:
    - **Docstring Detection**: Standalone string constants (docstrings and standalone expression strings) are now explicitly excluded from `MISSING_I18N` analysis.
    - **Improved UI String Heuristics**: Enhanced detection to include single-word UI labels with punctuation (e.g., `"Name:"`, `"Error!"`), improving accuracy for translation candidates.

### Fixed
- **I18n False Positives**: Resolved issue where developer documentation (docstrings) was incorrectly flagged as missing translation.


### Added
- **Engine Performance Upgrades**:
    - **Single-Pass AST Traversal**: Refactored `CompositeVisitor` to a hook-based model (`enter_node`/`exit_node`), visiting each AST node exactly once.
    - **Worker Context Sharing**: Implemented process-pool initializers to share heavyweight configuration and project context across workers, reducing per-file serialization overhead.
- **Deep QGIS Safety Audits**:
    - **Signal/Slot Leak Detection**: Automatically identifies signals connected in `initGui` that lack a corresponding disconnect in `unload`.
    - **UI-Blocking Heuristics**: Detects intensive loops and long-running operations that should be wrapped in `QgsTask` to prevent freezing the QGIS interface.
- **New CLI Visualization & Utilities**:
    - **`graph` Command**: Generates Mermaid dependency graphs and identifies circular imports visually.
    - **`serve` Command**: Built-in local web server to instantly view generated HTML analysis reports.
- **Enhanced I18n Heuristics**: Improved precision in translatable string detection, reducing false positives for non-user-facing strings.

### Changed
- **Modular Visitor Architecture**: Fully decoupled visitors into specialized components supporting both standalone and single-pass execution.
- **Improved Complexity Scoring**: Introduced density-based penalties for code with high decision-point concentrations.

### Fixed
- **Undefined Name Regressions**: Resolved several `F821` linting issues in CLI and engine layers.
- **Test Compatibility**: Implemented a hybrid traversal model to maintain 100% compatibility with the existing unit test suite.

## [1.6.0] - 2026-02-03

### Added
- **Official QGIS Repository Validation**: Implemented strict local checks to mirror the official repository bot:
    - **Package Size Enforcement**: Warning when the plugin ZIP exceeds the 20MB limit.
    - **Binary File Detection**: Proactive scanning and banning of `.exe`, `.dll`, `.so`, and other binaries.
    - **Folder structure validation**: Ensures the root folder matches the expected QGIS plugin format.
    - **Enhanced Metadata Validation**: Verification of mandatory fields and URL protocols in `metadata.txt`.
- **Focused Security Command**: New `security --deep` flag for intensive, multi-pass vulnerability audits.
- **Rules Documentation**: Added `list-rules` command to display the full catalog of implemented audit rules.

### Changed
- **CLI Architecture Refactor**: Re-implemented the command-line interface using the **Command Pattern** for better modularity and testability.
- **Visitor Modularization**: Split the monolithic `visitors.py` into a specialized package (`src/analyzer/visitors/`) with separate audit contexts.
- **Engine Optimization**: Significant performance improvements in file discovery and AST traversal logic.
- **Refined Auto-Fixing**: Improved `FixRegistry` and handler-based auto-reparations for QGIS legacy issues.

### Fixed
- **CLI Flag Consistency**: Standardized flags across all subcommands (`--report`, `--profile`, `--input`).
- **Path Handling**: Robust relative path resolution in terminal reports and JSON exports.

## [1.5.0] - 2026-02-01

### Added
- **Security Scanning Infrastructure**: Integrated AST-based auditing (`QGISSecurityVisitor`) and Regex/Entropy scanning (`SecretScanner`) to detect vulnerabilities:
    - `B102/B307`: Detects high-risk `exec()` and `eval()` calls.
    - `B602/B608`: Detects unsafe subprocess shell execution and potential SQL injection.
    - `HARDCODED_SECRET`: Advanced entropy-based detection of API keys, passwords, and tokens.
- **Dedicated Security CLI**: New `security` subcommand for focused, high-impact plugin audits with specialized terminal reporting.
- **Enhanced Version Reporting**: Added `--version` flag and a dedicated `version` subcommand.
- **Bilingual Command Guides**: Comprehensive GIS guides in both Spanish (`GUIA_COMANDOS.md`) and English (`COMMANDS_GUIDE.md`).
- **Antigravity Framework Standardization**: Modularized the agent system into `.agent/scripts/` for maximum portability.

### Changed
- **Documentation Reorganization**: Restructured the `docs/` directory into a professional hierarchy (`user_guide/`, `releases/`, `research/`, `development/`, `reports/`).
- **Project Structure**: Refactored `ProjectAnalyzer` to support multi-faceted scoring (Stability, Maintainability, Compliance, Security).

### Fixed
- **Single-File Discovery**: Fixed a bug where analyzing individual files (not directories) resulted in zero results.
- **Reporter Pathing**: Improved file path reporting in terminal summaries for single-file analysis.

## [1.4.0] - 2026-01-03

### Added
- **Type Checking**: Full integration with `mypy` and `qgis-stubs` for static type analysis and improved code reliability.
- **CLI Output Control**:
    - Default behavior is now **Screen-Only** (linter style), significantly cleaner for CI/CD.
    - Added `--report` (or `-r`) flag to explicitly generate HTML/Markdown reports.

## [1.2.0] - 2026-01-02

### Added
- **GitHub Action**: Native Composite Action (`action.yml`) for easy CI/CD integration.
- **Pre-commit Hook**: Native configuration (`.pre-commit-hooks.yaml`) for automated local checks.
- **PyPI Standards**: Improved project metadata (URLs, Classifiers) in `pyproject.toml`.

## [1.1.0] - 2026-01-02

### Added
- **Security & Safety Audit Suite**: Implemented advanced rules for detecting vulnerabilities and performance bottlenecks:
    - `UNSAFE_SUBPROCESS`: Detects dangerous command execution with `shell=True` or variable interpolation.
    - `BLOCKING_NETWORK_CALL`: Flags synchronous network requests in UI code to prevent freezing the QGIS interface.
- **GPL v3 Licensing**: Officially adopted the GNU General Public License v3 for the project.

### Fixed
- **Rule Message Accuracy**: Improved clarity and precision of audit rule messages.
- **Vulnerability Testing**: Added specialized unit tests for security-related rules.

## [1.0.0] - 2026-01-02

### Added
- **Professional `summary` CLI**: Integrated a high-performance terminal reporter (`qgis-analyzer summary`) with ANSI color support and granular filtering (`--by {total,modules,functions,classes}`).
- **Granular Complexity Heatmaps**: Terminal-based visibility into file and function complexity, identifying technical debt instantly.

### Improved
- **Core Excellence Standard**: Finalized the project-wide standardization of docstrings and type safety, achieving a professional baseline for all future development.
- **Reporting Architecture**: Refactored reporting layers to be fully modular, allowing for easy extension of terminal and file-based outputs.

## [0.9.0] - 2026-01-02

### Added
- **Standardized Project Style**: Applied Google-style docstrings and strict type hinting (>90% coverage) project-wide for enhanced maintainability and safety.
- **`summary` Command**: Integrated an enhanced terminal-based reporting tool to provide quick, colored insights into project quality.

### Improved
- **Structural Decomposition**: Decomposed the monolithic `utils.py` into specialized modules (`logging_utils`, `config_utils`, `path_utils`, `performance_utils`, `ast_utils`) and unified package facades.
- **Modernized Test Suite**: Standardized the entire `tests/` directory with consistent imports and Google-style documentation.

## [0.8.0] - 2026-01-02

### Added
- **Standardized Scoring System**: Implemented objective, industry-standard metrics for project evaluation.
    - **Maintainability Index (MI)**: Integrated the standard SEI formula for code health assessment.
    - **Pylint-Style Weighted Scoring**: Integrated Ruff findings with severity-based weighting (Errors: 5x, Others: 1x).
- **Official Scoring Documentation**: Added `docs/SCORING_STANDARDS.md` to formally define project rating criteria.

### Improved
- **High-Contrast UI**: Fixed "lost letters" issue in HTML report score cards by ensuring high contrast between text and background.
- **Reporting Labels**: Added explicit labels to score cards in the HTML summary for better scannability.
- **Structural Decomposition**: Decomposed the monolithic `utils.py` into specialized modules (`logging_utils`, `config_utils`, `path_utils`, `performance_utils`, `ast_utils`) and unified package facades.
- **Modernized Test Suite**: Standardized the entire `tests/` directory with consistent imports and Google-style documentation.

### Fixed
- **Contrast Legibility**: Resolved low-contrast text rendering in the project summary dashboard.

### Added
- **Dual Scoring System**: Introduced "Module Stability Score" (file-level) and "Code Maintainability Score" (function-level) for a more nuanced view of project health.
- **Maintainability Metrics**: Function-level complexity is now explicitly tracked and weighted in the overall quality report.

### Improved
- **Extreme Refactoring**: Successfully refactored all 8 high-complexity functions identified in the core engine, CLI, and reporting layers, reducing their individual cyclomatic complexity by up to 80%.
- **Zero High Complexity**: Achieved a 100% reduction in `HIGH_COMPLEXITY` violations (>15 CC) across the entire codebase.
- **Modular Reporting**: Refactored `reporters.py` into a modular assembly pipeline, making HTML and Markdown generation significantly more maintainable.
- **English Documentation**: Updated project metadata and descriptions to English to align with international standards.

### Fixed
- **Score Reporting**: Fixed "Score: N/A" issue in `parse_report.py` by correctly extracting metrics from nested JSON objects.

## [0.6.2] - 2026-01-02

### Added
- **Per-Function Complexity Metrics**: `project_context.json` now includes detailed complexity scores for each function object, enabling precise monitoring of refactoring efforts.
- **Automatic Complexity Warning**: New `HIGH_COMPLEXITY` rule in scanner that flags functions with Cyclomatic Complexity > 15.

### Improved
- **Structured Data Models**: Refactored `ModuleAnalysis` to store functions as rich objects instead of simple ID strings.

## [0.6.1] - 2025-12-31

### Added
- **Default Scrutiny Exclusions**: Added a robust set of default ignored patterns (`.venv`, `venv`, `__pycache__`, `.git`, `.github`, `build`, `dist`, etc.) that are now automatically excluded from all scanning phases (AST, binaries, package size).
- **Project Type Detection**: The engine now distinguishes between a `QGIS Plugin` and a `Generic Python Project`, tailoring scoring and validation logic accordingly.

### Improved
- **Multi-processing Engine**: Replaced sequential scanning with `ProcessPoolExecutor`, significantly reducing analysis time for large projects.
- **Real-time UX**: Added a CLI `ProgressTracker` with ETA and file counts.
- **Reporting Architecture**: Refactored `reporters.py` to handle different project types and improved the HTML report layout.

### Fixed
- **Ignore Logic Engine**:
  - Improved `.analyzerignore` pattern matching to support non-anchored directory patterns (e.g., `dist/` now matches at any depth).
  - Added support for anchored patterns (starting with `/`) for precise exclusion.
  - Resolved a regression where `scan_for_binaries` and `ResourceValidator` bypassed ignore rules, causing false positives in quality scores.

## [0.6.0] - 2025-12-31

### Added
- **Security Hardening**: Implemented SSRF protection for metadata URLs, XXE mitigation for XML parsing, and Path Traversal prevention for file operations.
- **SPATIAL_INDEX Rule**: New AST-based rule to detect missing spatial indexes in QGIS layers.

### Improved
- **Caching & Performance**: Integrated `LRUCache` for repeated file lookups and optimized AST traversals.
- **Professional Logging**: Replaced print statements with a structured logging system (`analyzer.log`).
- **Resilient Parsing**: Added a minimal TOML parser fallback for systems without `tomllib`.

### Fixed
- Syntax error in `scanner.py`.
  - Implemented security-focused unit tests covering SSRF and traversal scenarios.
- **Improved Scans**:
  - Refactored `SPATIAL_INDEX` as an AST-based rule for high-precision detection of unoptimized loops.

### Changed
- **Performance Optimization**:
  - Analysis pipeline now caches file content, reducing disk I/O significantly during multi-phase scanning.
  - Refined exception handling in CLI to provide specific feedback for file and validation errors.

## [0.5.1] - 2025-12-31

### Fixed
- **Consistency & Stability**:
  - Unified Rule IDs across AST and Regex engines (e.g., `UNPRECISE_LAYER`, `MANUAL_RESOURCE_PATH`).
  - Fixed undefined attribute `self.ignore_matcher` (renamed to `self.matcher`) in `ProjectAnalyzer`.
  - Corrected method call `ignore_matcher.is_ignored()` in package size calculator.
  - Fixed missing imports (`tempfile`, `shutil`, `ET`) in `fixer.py` and `semantic.py`.
  - Corrected `validate_metadata` path handling in `engine.py`.
- **CLI Improvements**:
  - Added `-p/--profile` support to `fix` command, allowing fixes to respect custom rule configurations.
- **Performance**:
  - Pre-compiled regex patterns in `scanner.py` for faster auditing.

### Changed
- **Refactoring**:
  - Consolidated plugin structure and metadata validation logic into `validators.py`.
  - Improved robustness of the minimal TOML parser for better numeric and string handling.
  - `analyze_module_worker` now consistently accepts and passes `rules_config` to workers.

## [0.5.0] - 2025-12-30

### Added
- **Deep Semantic Analysis** (Roadmap Point 1)
  - Dependency graph with circular import detection
  - Resource validation (Qt `.qrc` files)
  - Signal/Slot safety checks for missing slot methods
  - Module coupling metrics (fan-in/fan-out)
- **Interactive Auto-Fix Mode** (Roadmap Point 2)
  - `fix` command with dry-run mode by default
  - AST-based transformers for code corrections:
    - `GDALImportFixer`: `import gdal` → `from osgeo import gdal`
    - `LegacyImportFixer`: `PyQt4/PyQt5` → `qgis.PyQt`
    - `PrintToLogFixer`: `print()` → `QgsMessageLog.logMessage()`
    - `I18nFixer`: Wrap hardcoded strings in `self.tr()`
  - Safety features: git status check, interactive diff preview, confirmation prompts
  - Rule filtering with `--rules` flag
- **Repository Compliance Suite** (Roadmap Point 3)
  - Binary scanner: Detect prohibited `.exe`, `.dll`, `.so` files
  - Package size calculator with 20MB limit warning
  - URL validator for `metadata.txt` links (homepage, tracker, repository)
  - Integration into scoring system with penalties
- **Enhanced Configuration Profiles** (Roadmap Point 4)
  - Rule-level configuration in `pyproject.toml`
  - Custom severity levels: `error`, `warning`, `info`, `ignore`
  - Nested TOML section support: `[tool.qgis-analyzer.profiles.NAME.rules]`
  - Backward compatible (works without rules config)

### Changed
- Updated `load_profile_config()` to parse `rules` section
- Enhanced minimal TOML parser for nested sections
- `QGISASTVisitor` now accepts `rules_config` parameter
- Scoring system penalizes binaries (-50 pts) and size violations (-10 pts)

### Documentation
- Created `COMPETITIVE_ANALYSIS.md` comparing with flake8-qgis and pylint-plugin-utils
- Updated walkthrough artifacts for each feature

## [0.4.0] - 2025-12-29
### Changed
- **Zero Runtime Dependencies**: Removed all external runtime dependencies (`tomli`, `dominate`). The analyzer now uses a built-in minimal TOML generator and manual HTML reporting.
- **Migration to Unittest**: Refactored the entire test suite from `pytest` to the native `unittest` framework, removing `pytest` from the development stack.
- **Optimized Deployment**: Reduced project footprint by eliminating non-essential packages.

### Removed
- **Project Generator (`init`)**: Project generation capabilities were removed from the analyzer to focus strictly on static analysis. The code has been exported to `generator_export`.

## [0.3.1] - 2025-12-29
### Added
- **Professional Logging System**: Persistent logging to `analysis_results/analyzer.log` with detailed tracebacks for troubleshooting.
- **Resource Management**: Optimized concurrency (limited to 4 workers) and file size safety (skips files >500KB) to prevent system crashes on large projects.
- **Cache Optimization**: Added results cache to `IgnoreMatcher` for faster file scanning.

### Fixed
- **CLI Stability**: Resolved `NameError: pathlib` and improved top-level exception handling.
- **Audit Rule IDs**: Renamed `UNPRECISE_LAYER` to `UNPRECISE_LAYER_LOOKUP` and `MANUAL_PATH` to `MANUAL_RESOURCE_PATH` for clarity and test consistency.

## [0.3.0] - 2025-12-29
### Added
- **Ruff Integration**: Native execution of Ruff for Python standard linting.
- **AST Audit Engine**: Migration of critical rules to Abstract Syntax Tree (AST) for higher precision.
- **New QGIS Rules**: 
  - `QGIS_PROTECTED_MEMBER`: Detection of unstable protected imports (`qgis._core`, etc.).
  - `IFACE_AS_ARGUMENT`: Detection of `QgisInterface` passed as argument (standards QGS105).
  - `GDAL_DIRECT_IMPORT`: Warning for direct `gdal` imports instead of `osgeo.gdal`.
  - `MANDATORY_CLEANUP`: Validation of `unload()` presence when `initGui()` is used.
- **Advanced Profiles**: Configurable profiles (`default`, `release`) in `pyproject.toml` with strict modes.
- **HTML Reports**: Professional and visual report generation using `dominate`.
- **Boilerplate System (`init`)**: Project generation for Processing, GUI, and Map Tool plugins.
- **Template Safety**: Use of `.tmpl` extension for boilerplate files to avoid IDE syntax errors.

### Fixed
- **Stability**: Resolved `KeyError: complexity` crashes during syntax errors.
- **Reliability**: Restored missing system imports in utility modules.

## [0.2.0] - 2025-12-28
### Added
- Support for `.analyzerignore` files to exclude specific files and directories from analysis.
- Robust pattern matching using the native `fnmatch` module (no external dependencies).


### Added
- Initial project structure for QGIS Plugin Analyzer.
- Professional static analysis engine using Python AST and Regex.
- Compliance rules for QGIS standards (i18n, obsolete APIs, threading, etc.).
- Official repository standards validation (`metadata.txt`, `__init__.py`, `LICENSE`).
- Multi-process support for high-performance analysis.
- Markdown and JSON reporting system.
- Unit test suite for scanner and validation logic using `pytest`.
- Development dependency management with `uv`.

### Fixed
- Corrected scoring reporting bug where `qgis_score` appeared as 0 in `PROJECT_SUMMARY.md`.
- Refined `MANUAL_RESOURCE_PATH` regex for better detection of manual icon/UI paths.
- Fixed regex typo and lookahead logic in `scanner.py`.

## [0.0.1] - 2025-12-25
- Conceptual prototype, research, and comparative analysis.
