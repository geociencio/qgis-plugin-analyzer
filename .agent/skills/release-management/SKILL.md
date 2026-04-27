---
name: release-management
description: Standards for the release process of the qgis-plugin-analyzer Python package.
trigger: when preparing releases, updating versions, or using the /release-plugin workflow
---

# Release Management (Package Version)

Controls the version lifecycle of the `qgis-plugin-analyzer` package, ensuring quality and consistency in every delivery to PyPI/GitHub.

## When to use this skill
- At the end of a sprint or bug fix cycle.
- When updating `pyproject.toml` for a new version.
- When generating version notes or updating the changelog.
- When using the `/release-plugin` workflow.

## Freedom of Action
- **Strict**: Compliance with Semantic Versioning and quality checks is mandatory.

## Detailed Workflow

### Phase 1: Quality and Preparation
1. **Quality Analysis**:
   ```bash
   uv run qgis-analyzer analyze . -o analysis_results --profile release
   ```
   - Validate: Score > Acceptable (defined in badges), test coverage > 80%.
2. **Linting & Type Checking**:
   ```bash
   uv run ruff check .
   uv run mypy .
   ```

### Phase 2: Versioning
1. **Synchronization**: Update `version` in `pyproject.toml`.
2. **Changelog**: Add entry in `CHANGELOG.md` following the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.
3. **Semver Rules**:
   - MAJOR (X): Incompatible changes in CLI API/Library.
   - MINOR (Y): New analysis rules or features.
   - PATCH (Z): Bug fixes.

### Phase 3: Technical Verification
1. **Full Tests**:
   ```bash
   uv run pytest
   ```
   (Optional: integration tests with QGIS if applicable)

### Phase 4: Git and Tagging
1. Release commit: `chore(release): prepare vX.Y.Z`.
2. Tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`.
3. Push: `git push origin main --tags`.

### Phase 5: Packaging and Distribution
1. **Clean**: `rm -rf dist/ build/`
2. **Build**:
   ```bash
   uv run python -m build
   ```
3. **Validation**: Verify content of `.tar.gz` and `.whl` using `twine check`.
4. **Release**: Create GitHub release attaching the artifacts. (PyPI publication is typically handled via CI).

## Quality Checklist
- [ ] Does static analysis pass without critical errors?
- [ ] Is the version in `pyproject.toml` correct?
- [ ] Is `CHANGELOG.md` updated?
- [ ] Do tests pass locally?
