---
description: Standardized Release Workflow for AI Agents
---

# Release Workflow for QGIS Plugin Manager

This document serves as the master guide for AI agents to perform a project release. Follow these steps sequentially to ensure consistency, quality, and documentation accuracy.

## Phase 1: Quality Analysis
Before starting any release, you must verify the state of the project.

1. **Run QGIS Plugin Analyzer**: 
   // turbo
   `uv run qgis-analyzer . -o analysis_results`
   > [!NOTE]
   > For this CLI tool, some scores might be lower than 100% due to missing plugin-specific files (like `metadata.txt` at root). This is expected.

2. **Update Quality Badge**: 
   Extract the `Code Score` from `analysis_results/PROJECT_SUMMARY.md` and update the badge in `README.md`.

## Phase 2: Versioning & Documentation
1. **Determine Version**: 
   Check `pyproject.toml` for current version and decide on the next version (Semantic Versioning).
   - Major: Breaking changes.
   - Minor: New features or major refactors (e.g., v0.5.0 Modernization & UI).
   - Patch: Bug fixes.

2. **Update pyproject.toml**: 
   Update the `version` field.

3. **Update CHANGELOG.md**: 
   Follow the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format. Group changes by:
   - `Added`
   - `Improved` (UI/UX & Refactor)
   - `Fixed`

4. **Generate Release Notes**: 
   - Create `docs/RELEASE_NOTES_vX.Y.Z.md`.
   - Create `docs/GITHUB_RELEASE_vX.Y.Z.md`.
   - Include a descriptive title (e.g., "The Modernization Release").

## Phase 3: Verification
1. **Run Linting**: 
   // turbo
   `uv run ruff check .`
   Fix all errors, especially `E501 Line too long` which often blocks commits.

2. **Run Tests**: 
   // turbo
   `make test` (or `uv run python -m unittest discover tests`).
   Ensure 100% pass rate.

## Phase 4: Git Operations
1. **Staging & Commit**: 
   Stage all documents and use a descriptive commit message following Conventional Commits.
   Example: `docs: release v1.1.0 Security & Licensing Suite`

2. **Create Tag**: 
   Create an annotated tag with the version and title.
   `git tag -a vX.Y.Z -m "vX.Y.Z: [Title]"`

3. **Push to Origin**: 
   Push both the branch and the specifically created tag.
   `git push origin main && git push origin vX.Y.Z`

## Phase 5: Artifacts & GitHub Release
1. **Build Artifacts**:
   `uv build`
2. **Publish (Optional)**:
   `uv publish`
3. **Create GitHub Release**:
   Use the `gh` CLI with the template:
   `gh release create v{version} --title "v{version}" --notes-file .github/release_template.md dist/*`

---

## 🏁 Quick Release Checklist
- [ ] Tests pass (Local: `uv run python -m unittest discover tests`)
- [ ] `CHANGELOG.md` updated with latest changes.
- [ ] `pyproject.toml` version updated matching the tag.
- [ ] Quality Badges in `README.md` updated.
- [ ] Git Tag created and pushed to origin.
- [ ] Artifacts built (`uv build`) and verified.
- [ ] GitHub Release created using the template.
- [ ] Files `CONTRIBUTING.md` and `.github/release_template.md` are in `main`.
