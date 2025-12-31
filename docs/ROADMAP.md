# Roadmap: QGIS Plugin Analyzer 🚀

This document outlines the strategic improvements and technical advancements required to evolve `qgis-plugin-analyzer` from a static validator into a comprehensive quality assurance ecosystem.

## 1. ✅ Deep Semantic Analysis (Completed in v0.5.0)

Currently, the analyzer relies on AST/Regex for single-file analysis. It lacks understanding of cross-file relationships.

- **Dependency Graphing**:
    - Visualize module usage using Mermaid diagrams in HTML reports.
    - Detect circular imports.
- **Resource Validation**:
    - Verify that resource paths (e.g., `:/plugins/my_plugin/icon.png`) actually exist in the compiled `.qrc`/`.py` resource file.
- **Signal/Slot Safety**:
    - Analyze `connect()` calls to ensure target slots exist and match signatures (where possible statically).

## 2. ✅ Interactive "Auto-Fix" Mode (Completed in v0.5.0)

Move from "reporting" to "fixing". Add a `fix` command.

- **Automated Fixers**:
    - **i18n**: Interactive mode to wrap string literals in `self.tr()`.
    - **Logging**: Replace `print()` with `QgsMessageLog.logMessage()`.
    - **Imports**: Auto-refactor direct `gdal` imports to `osgeo.gdal`.

## 3. ✅ Official Repository Compliance Suite (Completed in v0.5.0)

Local pre-check to ensure plugin passes metadata and security policies of `plugins.qgis.org`.

- **Binary Scanner**: Fail if `.dll`, `.exe`, `.so` binaries are found.
- **Link Validator**: Check availability of URLs in `metadata.txt` (homepage, tracker).
- **Size Check**: Warn if package size exceeds 20MB.

## 4. ✅ Enhanced Configuration Profiles (Completed in v0.5.0)

The current profile system only affects failure conditions. It should control the analysis depth.

- **Ruff Parameter Injection**:
    - Allow profiles to inject specific Ruff rules/configs.
- **Custom Rule Sets**:
    - Allow users to define custom rule sets and severity levels in `pyproject.toml`.

## 5. Security & Safety (Priority: Low)

- **Subprocess Auditing**:
    - Flag usage of `subprocess` with unsanitized inputs.
- **Network Calls**:
    - Detect purely sychronous network calls (e.g., `requests.get`) inside the main thread (GUI blocking).

## 6. Integration Improvements

- **GitHub Actions**:
    - Create a dedicated GitHub Action in the marketplace that uses this tool.
- **Pre-commit Hook**:
    - official support for `.pre-commit-config.yaml`.

## 7. Type Checking (Future)

- Integrate `mypy` execution into the report pipeline to catch type-related errors before runtime.
