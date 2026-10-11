# Release Process — GitHub & PyPI

Canonical release guide for **qgis-plugin-analyzer**. It describes how a version is
prepared, tagged, published on GitHub and uploaded to PyPI, driven by
`.github/workflows/release.yml`.

> Toolchain: `uv` (build + lock), `pytest` (coverage floor 80 %), `ruff`, `mypy`,
> `gh` (GitHub CLI). The runtime version is derived from `pyproject.toml`
> (`analyzer._get_version`), so the version bump below is the single source of truth.

---

## 0. How the pipeline works (two stages)

```
git push vX.Y.Z (tag)
        │
        ▼
[release.yml · draft-release]  ──▶  GitHub Release (DRAFT, empty body)
        │  (you publish it)
        ▼
[release.yml · publish-pypi]   ──▶  uv build ++ uv publish --▶ PyPI
```

- **Stage 1 — tag push**: creates a **draft** GitHub Release (`draft-release` job).
- **Stage 2 — release published**: when you publish the draft, the `publish-pypi`
  job builds the distribution and uploads it to PyPI using the repo secret
  `PYPI_TOKEN`.

Required secret: **`PYPI_TOKEN`** (Settings → Secrets → Actions).
Verify with `gh secret list`.

### Obtaining the `PYPI_TOKEN`

The token is a PyPI API token, stored as a GitHub repository secret.

1. **Create it on PyPI** — sign in at https://pypi.org and open
   **Account settings → API tokens** (https://pypi.org/manage/account/token/):

   - **Add API token** → name it (e.g. `qgis-plugin-analyzer CI`).
   - **Scope**: pick **Project: `qgis-plugin-analyzer`** (least privilege). A brand-new
     project needs an **Entire account** token first; narrow it afterwards.
   - Copy the token — it is shown **once** and starts with `pypi-`.

2. **Store it as a repo secret** — GitHub → repo → **Settings → Secrets and variables →
   Actions → New repository secret**:

   - Name: **`PYPI_TOKEN`** · Secret: the `pypi-…` value.
   - Verify: `gh secret list`.

   The workflow consumes it as `UV_PUBLISH_TOKEN` (see §0). The token is a credential —
   never commit it; if leaked, revoke it on the same page and issue a new one.

3. **Local / manual publish** uses your own token:

   ```bash
   UV_PUBLISH_TOKEN=pypi-******** uv publish
   # or:  uvx twine upload dist/* -u __token__ -p pypi-********
   ```

   (or configure `~/.pypirc` / keyring).

### Alternative: Trusted Publishing (no token)

PyPI **Trusted Publishing** uses GitHub OIDC instead of a long-lived secret:

- PyPI → your project → **Publishing → Add a new pending publisher**
  (GitHub: owner `geociencio`, repo `qgis-plugin-analyzer`, workflow `release.yml`).
- Add `permissions: id-token: write` to the publish job and replace the token step
  with `pypa/gh-action-pypi-publish` (GitHub's official action) instead of
  `uv publish` + `UV_PUBLISH_TOKEN`.

This removes the secret and its rotation; it requires editing `.github/workflows/release.yml`.

> GitHub (`gh`) and PyPI are separate accounts: the `gho_…` GitHub token does **not**
> work for PyPI.

---

## 1. Pre-flight gates (must be green)

```bash
uv run ruff check . && uv run ruff format --check .
uv run mypy src/
uv run pytest --cov=analyzer --cov-report=term -q      # coverage floor 80%
uv run qgis-analyzer analyze . --max-cc 15              # self-analysis gate
```

All must pass before touching the version.

---

## 2. Version & documentation

1. **Version bump** — `pyproject.toml`:

   ```toml
   [project]
   version = "X.Y.Z"
   ```

2. **Lockfile** (updates the root package version in `uv.lock`):

   ```bash
   uv lock
   uv run qgis-analyzer version      # must print X.Y.Z
   ```

3. **Changelog** — add a `## [X.Y.Z] - YYYY-MM-DD` section to `CHANGELOG.md`
   ([Keep a Changelog](https://keepachangelog.com/) + SemVer categories:
   `Added` / `Changed` / `Fixed` / `Docs` / `Removed`).

4. **Release notes** — create `docs/releases/notes/vX.Y.Z.md` (this is the body
   used when publishing the GitHub release).

5. **README** — update the `## 🆕 What's New in vX.Y.Z` section and any metric badges.

6. **Development log** — add a dated entry to `docs/DEVELOPMENT_LOG.md`.

### Commit layout (build a clean history)

Keep the **code fix** and the **release prep** as separate commits:

```bash
# 1) the actual change (if any), e.g.
git commit -m "fix(security): avoid B102/B307 false positives on attribute calls"

# 2) the release prep
git add pyproject.toml uv.lock CHANGELOG.md README.md \
        docs/DEVELOPMENT_LOG.md docs/releases/notes/vX.Y.Z.md
git commit -m "chore(release): prepare vX.Y.Z"
```

---

## 3. Build & verify locally (safety net)

```bash
rm -rf dist/
uv build
uvx twine check dist/*         # both sdist and wheel must say PASSED
```

This mirrors what `publish-pypi` runs in CI, so a local failure is caught early.

---

## 4. Tag & push

```bash
git push origin main
git tag -a "vX.Y.Z" -m "Release vX.Y.Z"
git push origin "vX.Y.Z"
```

Pushing the tag triggers **Stage 1** and creates a draft release.

---

## 5. Publish the GitHub release (triggers PyPI)

Wait for the draft, then publish it with the release notes. Publishing fires the
`release: published` event → **Stage 2** → PyPI.

```bash
# Wait for CI to create the draft (a few seconds)
gh release view vX.Y.Z | grep -E "draft:|tag:"

# Publish with the notes file
gh release edit vX.Y.Z --draft=false --title "vX.Y.Z" \
  --notes-file docs/releases/notes/vX.Y.Z.md
```

Verify:

```bash
gh run list --event release --limit 3         # the run must be "success"
gh run view <run-id>                          # publish-pypi job ✓ (draft-release skipped)
```

---

## 6. Verify PyPI

```bash
python - <<'EOF'
import urllib.request, json
d = json.load(urllib.request.urlopen("https://pypi.org/pypi/qgis-plugin-analyzer/json"))
print("latest:", d["info"]["version"])
print("files:", [f["filename"] for f in d["releases"].get("X.Y.Z", [])])
EOF
```

Also confirm the CLI still reports the right version from a clean install:

```bash
uvx qgis-plugin-analyzer@X.Y.Z --version
```

---

## 7. Manual fallback (CI unavailable)

If the workflow cannot run, publish from the local build. `PYPI_TOKEN` is a repo
secret and is **not** readable locally; use your own token.

```bash
rm -rf dist/ && uv build && uvx twine check dist/*
UV_PUBLISH_TOKEN=pypi-********  uv publish
# or:  uvx twine upload dist/* -u __token__ -p pypi-********
```

---

## 8. Troubleshooting / gotchas

- **PyPI job skipped after publishing.** `publish-pypi` must **not** declare a
  `needs:` on a job that is skipped by its own `if`. (Historically `publish-pypi`
  needed `draft-release`, which only runs on tag push, so on a `release` event it
  was skipped and PyPI never uploaded — v1.15.0/1.15.1 were uploaded manually.)
  The job now runs on its own `release`-published condition.

- **Release events use the tag's commit workflow.** A `release` event evaluates
  the workflow file from the **tagged commit**, not the default branch. Editing
  `main` does not change an already-published release. If you must change
  release-event behaviour, fix the workflow in the commit the tag points to
  (move the tag if the release has not been published to PyPI yet).

- **A freshly published version looks "unsatisfiable".** A consumer's
  `uv lock --upgrade-package qgis-plugin-analyzer` may still see the previous
  version through a stale simple-index cache. Retry with
  `uv lock --upgrade-package qgis-plugin-analyzer --no-cache --refresh`.

- **`gh` auth.** `gh auth status` must show `repo` (+ `workflow`) scopes; the SSH
  remote is used for `git push`.

- **Node.js 20 deprecation warning.** Informational only; do not act while
  `actions/checkout@v4` / `astral-sh/setup-uv@v3` still work.

---

## 9. Checklist

- [ ] `ruff`, `ruff format --check`, `mypy src/`, `pytest` (≥80 % cov), self-analysis `--max-cc 15` green.
- [ ] `pyproject.toml` version bumped; `uv.lock` regenerated; `qgis-analyzer version` confirms.
- [ ] `CHANGELOG.md`, `docs/releases/notes/vX.Y.Z.md`, README "What's New", `docs/DEVELOPMENT_LOG.md` updated.
- [ ] Fix commit + `chore(release)` commit; `uv build` + `twine check` PASSED.
- [ ] Tag `vX.Y.Z` pushed; draft GitHub release created and **published** with notes.
- [ ] `gh run view` → `publish-pypi` succeeded.
- [ ] Version live on PyPI (JSON check) and `uvx qgis-plugin-analyzer@X.Y.Z --version` correct.
