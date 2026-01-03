---
description: Recommended Release Workflow (Copilot Adapted)
---

# Release Workflow for QGIS Plugin Manager

This document is the master guide for performing a project release, integrating Copilot best practices with our specific toolchain (`uv`, `unittest`).

## 1. Update Version
Bump the version in `pyproject.toml`.

**Option A: Manual**
- Edit `version = "X.Y.Z"` in `pyproject.toml`.

**Option B: Automated (sed)**
```bash
# Example: 1.1.0 -> 1.1.1
sed -i 's/^version = "1.1.0"/version = "1.1.1"/' pyproject.toml
```

**Commit the bump:**
```bash
git add pyproject.toml
git commit -m "chore(release): v1.1.1"
```

## 2. Create Tag & Push
Create an annotated tag and push changes to the remote.

```bash
VERSION=1.1.1
git tag -a "v$VERSION" -m "Release v$VERSION"

git push origin main
git push origin "v$VERSION"
```

## 3. Build Artifacts
Generate distribution files (source and wheel). Since we use `uv`, this is streamlined.

```bash
uv build
# Verify artifacts exist
ls -la dist/
```

## 4. Prepare Release Notes
Generate a temporary release notes file using our template.

```bash
VERSION=1.1.1
DATE=$(date +%F)
sed -e "s/{version}/$VERSION/g" -e "s/{date}/$DATE/g" .github/release_template.md > /tmp/release_notes.md
```
> **Review**: Open `/tmp/release_notes.md` and populate any missing PR links or details.

## 5. Create GitHub Release
Use the GitHub CLI (`gh`) to manage the release lifecycle.

**Option A: Draft Release (Recommended)**
Creates a draft and uploads assets. Allows final verification before publishing.
```bash
gh release create "v$VERSION" --title "v$VERSION" --notes-file /tmp/release_notes.md --draft
# Upload assets
gh release upload "v$VERSION" dist/* --clobber
```

**Option B: Direct Publish**
```bash
gh release create "v$VERSION" dist/* --title "v$VERSION" --notes-file /tmp/release_notes.md
```

## 6. Verification
Check the status of CI workflows triggered by the tag.

```bash
# List recent release runs
gh run list --workflow release.yml

# View specific run
gh run view <run-id> --web
```

## 7. Additional Tips
- **Generate Auto-Notes**: `gh release create "v$VERSION" --generate-notes`
- **View on Web**: `gh release view "v$VERSION" --web`
- **PyPI Publishing**:
  ```bash
  # If configured with token
  uv publish
  ```

---

## ✅ Pre-Flight Checklist
- [ ] Tests pass locally: `uv run python -m unittest discover tests`
- [ ] `CHANGELOG.md` updated.
- [ ] `pyproject.toml` version matches target.
- [ ] Tag created and pushed.
- [ ] Artifacts built and verified in `dist/`.
- [ ] GitHub Draft Release created with proper notes.
- [ ] Assets (wheels/sdist) uploaded.
