---
name: project-context
description: Summary of the purpose, architecture, and structure of the qgis-plugin-analyzer project.
trigger: when starting a new session or needing high-level architectural context
---

# Project Context: QGIS Plugin Analyzer

## Purpose
`qgis-plugin-analyzer` is a static analysis tool designed for QGIS plugin developers. It audits Python code to ensure compliance with QGIS standards, security best practices, and maintainability metrics.

## Key Features
- **AST-based Analysis**: Custom visitors to detect QGIS-specific hazards (blocking loops, signal leaks).
- **Quality Scoring**: Combined metrics for Stability and Maintainability.
- **Automated Reporting**: Generates summaries in Terminal, JSON, Markdown, and HTML.
- **Legacy Support**: Detects obsolete APIs and GDAL/PyQt import patterns.

## Architecture
- `src/analyzer/cli/`: Typer-based command line interface.
- `src/analyzer/visitors/`: Core analysis logic using Python's `ast` module.
- `src/analyzer/reporters/`: Transformation of raw data into user-facing reports.
- `src/analyzer/engine.py`: Orchestrator of the analysis pipeline.
- `src/analyzer/scoring.py`: Logic for quality index calculation.

## Tech Stack
- **Language**: Python 3.9+
- **Tooling**: `uv` (Package management), `ruff` (Linting), `pytest` (Testing).
- **Core Libs**: `ast` (Standard library), `jinja2` (HTML reports), `typer` (CLI).

## Design Philosophy
- **Stateless & Static**: No execution of the plugin code; only source analysis.
- **Fast & Parallel**: Uses process pooling for multi-file analysis.
- **Extensible**: New rules can be added by implementing a new `BaseVisitor`.
