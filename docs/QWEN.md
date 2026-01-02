# QGIS Plugin Analyzer - Project Context

## Project Overview

The QGIS Plugin Analyzer is a static analysis tool designed specifically for QGIS (PyQGIS) plugin developers. Its goal is to elevate plugin quality by ensuring they follow community best practices and are optimized for AI-assisted development.

### Key Features
- **Deep Semantic Analysis**: Cross-file dependency graphing, circular import detection, and module coupling metrics
- **Interactive Auto-Fix Mode**: Automatically fix common QGIS issues (GDAL imports, PyQt bridge, logging, i18n) with safety checks
- **Official Repository Compliance**: Proactive validation of binaries, package size, and metadata URLs
- **Enhanced Configuration Profiles**: Rule-level severity control (`error`, `warning`, `info`, `ignore`) via `pyproject.toml`
- **Integrated Ruff Analysis**: Combines custom QGIS rules with the fastest linter in the Python ecosystem
- **Qt Resource Validation**: Detect missing or broken resource paths (`:/plugins/...`) in your code
- **Signal/Slot Safety**: Detection of potentially missing slots or inherited slot warnings
- **AI-Ready**: Generates structured summaries and optimized contexts for LLMs
- **Zero Runtime Dependencies**: Works using only the Python standard library (Ruff as an external tool)

## Architecture

### Core Components
- `cli.py`: Command-line interface with `analyze` and `fix` subcommands
- `engine.py`: Main analysis pipeline that orchestrates the entire process
- `scanner.py`: AST-based and regex-based QGIS-specific rule checking
- `fixer.py`: Auto-fix engine with various fix strategies
- `transformers.py`: AST-based code transformers for applying fixes
- `semantic.py`: Dependency graph analysis and resource validation
- `validators.py`: Repository compliance checks (binaries, size, URLs)
- `reporters.py`: HTML, Markdown, and JSON report generation
- `utils.py`: Helper functions, configuration loading, and utility classes

### Analysis Pipeline
1. **File Discovery**: Scans Python files respecting `.analyzerignore` patterns
2. **Parallel Analysis**: Uses ProcessPoolExecutor to analyze modules concurrently
3. **AST Analysis**: Custom AST visitor detects QGIS-specific issues
4. **Ruff Integration**: Runs Ruff linter for general Python code quality
5. **Semantic Analysis**: Builds dependency graphs and validates Qt resources
6. **Repository Compliance**: Checks for binaries, package size, and metadata
7. **Report Generation**: Creates HTML, Markdown, and JSON reports

## Building and Running

### Installation
```bash
# Using uv (recommended)
uv tool install git+https://github.com/geociencio/qgis-plugin-analyzer.git

# Or local development
git clone https://github.com/geociencio/qgis-plugin-analyzer
cd qgis-plugin-analyzer
uv sync

# Using pip
pip install .
```

### Main Commands
```bash
# Analyze a plugin
qgis-analyzer analyze /path/to/your/plugin -o ./quality_report

# Auto-fix issues (dry run by default)
qgis-analyzer fix /path/to/your/plugin

# Apply fixes
qgis-analyzer fix /path/to/your/plugin --apply

# Use specific profile from pyproject.toml
qgis-analyzer analyze /path/to/your/plugin -p release
```

### Configuration Profiles
The analyzer supports configuration profiles defined in `pyproject.toml`:
```toml
[tool.qgis-analyzer.profiles.default]
strict = false
generate_html = true
fail_on_error = false

[tool.qgis-analyzer.profiles.release]
strict = true
generate_html = true
fail_on_error = true
```

## Development Conventions

### Code Structure
- All source code is in `src/analyzer/`
- Analysis rules are implemented in `scanner.py`
- Fix strategies are in `fixer.py` with corresponding transformers in `transformers.py`
- Reports are generated in `reporters.py`

### Analysis Rules
The analyzer implements various QGIS-specific rules categorized as:
- Internationalization (i18n)
- Obsolete API and Precision
- Threading Security
- Resource Management
- Performance
- Architecture
- QGIS Specific Standards (flake8-qgis inspired)
- General Python Best Practices

### Auto-Fix Capabilities
The tool can automatically fix:
- GDAL direct imports to `from osgeo import gdal`
- Legacy PyQt4/PyQt5 imports to `qgis.PyQt`
- Print statements to QgsMessageLog
- Hardcoded UI strings to `self.tr()` for i18n

### Configuration
- Uses `.analyzerignore` for file exclusion patterns (similar to `.gitignore`)
- Supports configuration profiles in `pyproject.toml`
- Rule severity can be customized per profile

## Testing and Quality Assurance

The tool includes:
- Parallel processing for faster analysis
- Safety checks before applying fixes
- Git status verification before auto-fixing
- Interactive diff previews for changes
- Comprehensive HTML and Markdown reports
- JSON output for integration with other tools

## Key Files and Directories
- `pyproject.toml`: Project configuration and dependencies
- `README.md`: Main documentation
- `RULES.md`: Complete list of audit rules
- `src/analyzer/`: Main source code
- `analysis_results/`: Default output directory for reports
- `.analyzerignore`: File patterns to ignore during analysis