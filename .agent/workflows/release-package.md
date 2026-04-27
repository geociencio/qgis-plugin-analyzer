---
description: Unified process for releasing the Python package.
agent: QA & Release Engineer
skills: [release-management, qa-docker, commit-standards]
validation:
  - Tests passing (Green)
  - Correct version in pyproject.toml
  - Build generated without errors (twine check OK)
  - Version verified via CLI (`qgis-analyzer version`)
---

Release workflow for `qgis-plugin-analyzer`.

1. **Preparation**:
   🤖 **Agent Action**: Use **release-management** to validate previous state.
   // turbo
   ```bash
   uv run qgis-analyzer analyze . --profile release --strict
   ```

2. **Version & Docs Synchronization**:
    - Update `version` in `pyproject.toml`.
    - **Local Verification**: `uv sync` and then `uv run qgis-analyzer version` to ensure the engine detects the new version.
    - **Changelog**: Update `CHANGELOG.md` (you can use the `changelog-generator` skill to automate this).
    - **Generate Release Notes**: Create `docs/releases/notes/v[VERSION].md` with a descriptive and professional title.
    - **Documentation Update**: Ensure `README.md` and `RULES.md` reflect the latest changes.

3. **Technical Verification**:
    // turbo
    ```bash
    uv run pytest
    uv run ruff check .
    uv run mypy .
    ```

4. **Git Operations**:
    // turbo
    ```bash
    git checkout main && git pull origin main
    git add pyproject.toml CHANGELOG.md README.md docs/ uv.lock
    git commit -m "chore(release): prepare v[VERSION]"
    git tag -a "v[VERSION]" -m "Release v[VERSION] - [Major Milestone]"
    git push origin main --tags
    ```

5. **Build & Release**:
    // turbo
    ```bash
    rm -rf dist/
    uv run python -m build
    uv run twine check dist/*
    ```
    - **PyPI Upload** (if applicable): `uv run twine upload dist/*`.
    - Create Release on GitHub using `gh release create` linking the created notes.
