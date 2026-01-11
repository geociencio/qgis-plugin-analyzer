# PyPI Packaging Standards & Best Practices (2025)

## 1. Metadata: `pyproject.toml` as the Source of Truth
The `pyproject.toml` file is the central configuration for modern Python projects (PEP 518, PEP 621).

### Mandatory Fields (PEP 621)
These must be under the `[project]` table:
- **`name`**: Valid package name (normalized).
- **`version`**: Compliant with PEP 440 (e.g., `1.2.0`, `1.2.0.dev1`).
- **`description`**: Short summary.
- **`readme`**: Path to README file (Markdown is standard).
- **`requires-python`**: E.g., `>=3.8`.
- **`authors` / `maintainers`**: List of name/email maps.
- **`license`**: Updated in late 2024 to support `license-files` key.
- **`classifiers`**: PyPI Trove classifiers (Development Status, Audience, License, Python Version).

### URLs (Important)
Add a `[project.urls]` table to link your repository, documentation, and tracker. This greatly improves the PyPI page score.
```toml
[project.urls]
"Homepage" = "https://github.com/user/repo"
"Bug Tracker" = "https://github.com/user/repo/issues"
"Documentation" = "https://user.github.io/repo"
```

## 2. Trusted Publishers (Security)
The gold standard for publication in 2025 is **Trusted Publishers** (OIDC), eliminating long-lived API tokens.

### How it works
1. **No Secrets**: You don't store a `PYPI_TOKEN` in GitHub Secrets.
2. **OIDC Handshake**: GitHub Actions requests a short-lived token from PyPI during the workflow using OpenID Connect.
3. **PyPI Verification**: PyPI verifies the token was issued for the specific repo/workflow/environment and authorizes the upload.

### Configuration
- **PyPI Side**: Add a "Trusted Publisher" for your GitHub repository and workflow filename (`release.yml`).
- **GitHub Workflow**: Add `permissions: id-token: write`.
- **Tooling**: `uv publish` and `gh-action-pypi-publish` support this natively.

## 3. Build & Distribution
### Tooling: `uv`
`uv` is recognized as a modern, high-performance frontend that adheres to standards.
- **Build Backend**: Most projects use `setuptools`, `hatchling`, or `flit-core`. Our project uses `setuptools` (defined in `[build-system]`).
- **Artifacts**: Always publish **both**:
  - `sdist` (`.tar.gz`): Source distribution.
  - `wheel` (`.whl`): Built distribution (universal).

## 4. Security & Quality Checklist
- **2FA**: Mandatory for all PyPI accounts.
- **API Tokens**: If not using Trusted Publishers, use "Project-Scoped" tokens, never "Account-Scoped".
- **Dynamic Versioning**: Consider tools like `setuptools_scm` if you want versions derived from Git tags automatically (optional).

## 5. Our Project Compliance Status

| Requirement | Status | Action Item |
| :--- | :---: | :--- |
| `pyproject.toml` core metadata | ✅ | Good coverage. |
| Project URLs | ⚠️ | **Missing**. Should be added. |
| Classifiers | ⚠️ | **Missing/Incomplete**. Should be added. |
| README format | ✅ | Markdown used. |
| Build System | ✅ | `setuptools` verified. |
| Security | ⚠️ | Using `PYPI_TOKEN` (Secret) instead of Trusted Publishers (OIDC). |
| Tooling | ✅ | `uv` is fully compliant. |

## Recommendations
1. **Update `pyproject.toml`**: Add `[project.urls]` and `classifiers`.
2. **Upgrade to Trusted Publishers**: Migrate from Token-based auth to OIDC for better security.

## References
1. **[Python Packaging User Guide](https://packaging.python.org/en/latest/guides/modernize-setup-py-project/)**: "Modernize your project" (2024).
2. **[PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/)**: Official documentation on OIDC publishing.
3. **[PEP 621](https://peps.python.org/pep-0621/)**: Storing project metadata in `pyproject.toml`.
4. **[PEP 518](https://peps.python.org/pep-0518/)**: Specifying Minimum Build System Requirements.
5. **[The state of Python packaging in 2025](https://packaging.python.org/)** (Community surveys and roadmap).
