# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.7.0] - 2026-01-02

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
