# v0.8.0: The Standardized Knight 🛡️

## Summary
The "Standardized Knight" release establishes objective, industry-standard metrics for PyQGIS code quality, ensuring that project ratings are fair, transparent, and mathematically sound.

## 🚀 Key Features
- **Objective Scoring Engine**: Mathematically calculated Maintainability Index (MI) and Pylint-style weighted metrics.
- **Scoring Standards Doc**: Full transparency into the grading logic via `docs/SCORING_STANDARDS.md`.
- **UI Legibility Fix**: High-contrast rendering for HTML report score cards.

## 🛠️ Internal Improvements
- Replaced subjective "Module Stability" and "Maintainability" formulas with standardized formulas.
- Refined `engine.py` to correctly integrate `Ruff` findings into the final score.
- Fixed CSS contrast issues in `reporters.py`.

## 📦 What's New
- `docs/SCORING_STANDARDS.md`: The official "Source of Truth" for our scoring logic.
- `docs/RELEASE_NOTES_v0.8.0.md`: Detailed release information.

---
**Full Changelog**: [v0.7.0...v0.8.0](https://github.com/geociencio/qgis-plugin-analyzer/compare/v0.7.0...v0.8.0)
