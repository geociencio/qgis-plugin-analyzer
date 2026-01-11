# Release Notes - v0.7.0
## "The Code Excellence Release"

This release marks a significant milestone in the maturity of the QGIS Plugin Analyzer. We have performed an exhaustive refactoring of the core engine and reporting systems, achieving a milestone of **zero high-complexity functions** in the entire codebase.

### Key Highlights
- **100% Complexity Reduction**: All functions previously flagged for high cyclomatic complexity have been decomposed into smaller, more maintainable units.
- **Improved Scoring System**: We now provide two distinct scores:
  - **Module Stability**: Measures the overall complexity of a file.
  - **Maintainability Index**: Measures the average complexity per function, highlighting the success of our refactoring.
- **Modular Architecture**: The reporting system has been completely rewritten into an assembly pipeline, allowing for easier extension and theme support.

### Detailed Changes
See the [CHANGELOG.md](../CHANGELOG.md) for a full list of additions, improvements, and fixes.
