# Release Notes - v0.8.0 "The Standardized Knight" 🛡️

## Overview
Release v0.8.0, codenamed "The Standardized Knight", marks a major milestone in the evolution of the QGIS Plugin Analyzer. This release focuses on objectivity, professional standards, and visual excellence. We have moved away from subjective scoring to a mathematically rigorous evaluation system based on industry standards.

## Key Changes

### 📉 Standardized Scoring System
We have introduced a completely objective scoring engine that eliminates "individual taste" from project ratings:
- **Maintainability Index (MI)**: Every file is now graded using the SEI Maintainability Index formula (logarithmic weight of Cylomatic Complexity vs. Source Lines of Code).
- **Ruff-Based Lint Score**: We now integrate Ruff findings using a Pylint-style weighted formula (Errors weigh 5x more than warnings/style issues).
- **Transparency**: A new document, `docs/SCORING_STANDARDS.md`, has been added to the project to explain exactly how your code is being graded.

### 🎨 Visual Legibility Improvements
Following user feedback, the HTML report has been visually overhauled:
- **High-Contrast Cards**: Score boxes now feature dark, high-contrast text to ensure legibility on light backgrounds.
- **Improved Scannability**: Added explicit labels and better spacing to the project summary dashboard.

## Technical Details
- **Maintainability Index Formula**: `MI = max(0, (171 - 0.23 * CC - 16.2 * ln(SLOC)) * 100 / 171)`
- **Lint Scoring Formula**: `100 - ((5*E + W + R + C) / (SLOC/10)) * 10`

---
*Standardizing excellence for the PyQGIS community.*
