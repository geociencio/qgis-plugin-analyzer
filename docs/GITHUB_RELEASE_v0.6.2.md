# 🚀 Precise Complexity Tracking

This patch release improves how complexity is reported, giving you finer control over your code quality metrics.

## What's New

- **Per-Function Complexity**: `project_context.json` now includes detailed complexity scores for everyone function.
- **High Complexity Warning**: New `[HIGH_COMPLEXITY]` rule warns you when a single function exceeds a Cyclomatic Complexity of 15.

## Improvements

- Refactored `models.py` to use structured data for function analysis.
- Improved AST scanning precision for control flow structures.

**Full Changelog**: https://github.com/geociencio/qgis-plugin-analyzer/compare/v0.6.1...v0.6.2
