# AI Context Core

The central nervous system for your AI-assisted coding workflow.

## Features
- **Project Analysis**: Deep AST analysis for Python projects.
- **Context Management**: Keeps `.ai-context` files updated.
- **Profiles**: 
    - `python-generic`: Standard Python support.
    - `qgis-plugin`: Specialized rules for QGIS plugin development.
- **Workflow Automation**: Standardized scripts for session management.

## Installation

```bash
uv tool install .
```

## Usage

```bash
# Initialize in a new project
ai-ctx init --profile qgis-plugin

# Update context manually
ai-ctx analyze
```
