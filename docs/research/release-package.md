---
description: "Automates the release process: quality validation, versioning, git tagging, and build."
agent: QA Engineer
skills:
  - project-context
  - tech-stack
  - commit-standards
---

# Workflow: Version Release (Release)

This workflow ensures that every public version of `qgis-plugin-analyzer` is stable, documented, and traceable.

## 1. Quality Audit (Gateway)

Before any version change, the system must be professionally audited.

// turbo
```bash
# 1. QGIS standards audit (Release Profile)
uv run qgis-analyzer analyze . --profile release

# 2. Static analysis and styling
uv run ruff check .

# 3. Strict type checking
uv run mypy . 

# 4. Unit tests
uv run pytest
```

> **STOP**: Do not proceed if there are MyPy errors, test failures, or if quality scores are insufficient.

## 2. Release Preparation

1.  **Versioning**: Update `version` in `pyproject.toml`.
2.  **Changelog**: Record changes for the new version in `CHANGELOG.md` following the "Keep a Changelog" format.
3.  **Release Notes**: Create a document in `docs/releases/notes/v[VERSION].md` with a **descriptive and professional title** (e.g., `# v1.6.0: Official Repository Validation...`).
4.  **Docs Synchronization**: Ensure `README.md` and other manuals are up to date.
5.  **Environment**: Ensure `uv.lock` is updated (`uv sync`).

## 3. Git Operations

Standardize messages and tags following Conventional Commits.

```bash
git add pyproject.toml CHANGELOG.md README.md docs/ uv.lock
git commit -m "chore(release): prepare v[VERSION]"
git tag -a "v[VERSION]" -m "Release v[VERSION] - [Descriptive Title]"
git push origin main --tags
```

## 4. Build and Publication

Generate artifacts and prepare the release on GitHub.

// turbo
```bash
# Clean previous builds
rm -rf dist/

# Build sdist and wheel
uv run python -m build

# Create GitHub Release (optional if using 'gh' cli)
gh release create "v[VERSION]" --title "v[VERSION] - [Title]" --notes-file docs/releases/notes/v[VERSION].md
gh release upload "v[VERSION]" dist/*
```

## Expected Outcome
- Version updated in `pyproject.toml`.
- Git tag created and pushed to remote.
- Release notes with descriptive titles.
- Distribution artifacts correctly generated in `dist/`.
