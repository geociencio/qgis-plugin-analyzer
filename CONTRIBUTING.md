# Contributing to QGIS Plugin Analyzer

Thank you for your interest in contributing! This document explains how to report issues, propose new rules, and submit code changes for `qgis-plugin-analyzer`.

## Code of Conduct
We follow respectful behavior in discussions and contributions. Please be professional and respectful to other collaborators.

## Reporting an Issue
When opening an issue, please include:
- A clear and concise title.
- The analyzer version (e.g., `1.1.0`) and commit SHA.
- Your operating system and Python version.
- A description of the problem and the expected behavior.
- Steps to reproduce (e.g., command used: `qgis-analyzer analyze /path/to/plugin`).
- Relevant files (`metadata.txt`, `pyproject.toml`, code snippets).
- Relevant logs/output and, if applicable, a minimal reproducible example.

For security-related issues, please do not post them in a public issue. Use the GitHub Security Advisories feature.

## Proposing a New Rule / Improvement
Before implementing:
1. Open an issue with your proposal:
   - Suggested Rule ID (e.g., `UNSAFE_SUBPROCESS`).
   - Description of the rule and its motivation.
   - "Bad" and "Good" examples of code or metadata.
   - Proposed severity (`high`, `medium`, `low`).
   - If proposing an auto-fix, describe the desired transformation and potential risks.
2. If the proposal is accepted, create a branch to implement it.

## Code Workflow (Pull Request)

### 1. Prepare Environment
This project uses [uv](https://github.com/astral-sh/uv) for dependency management and virtual environments.

```bash
# Clone and enter the repo
git clone https://github.com/geociencio/qgis-plugin-analyzer
cd qgis-plugin-analyzer

# Sync the development environment
uv sync
```

### 2. Development
1. Create a branch with a clear name:
   - `feat/<short-description>`
   - `fix/<short-description>`
   - `rule/<ID>-<short-description>`
2. Implement logic in `src/analyzer/` (usually in `scanner.py`).
3. Add or update the rule definition in `src/analyzer/rules/qgis_rules.py`.
4. Update `RULES.md` with the rule documentation.

### 3. Quality & Formatting
- Follow **PEP 8** and **PEP 257** (Google-style docstrings).
- The project uses **Black** for formatting.
- Use **Conventional Commits** for commit messages:
  - `feat: Add X`
  - `fix: Correct Y`
  - `docs: Update documentation`
  - `chore: Maintenance tasks`

### 4. Running Tests & Linter
Before submitting your PR, ensure everything passes:

```bash
# Run the full test suite
uv run python -m unittest discover tests

# Run style audit (Ruff)
uv run ruff check .
```

### 5. Open a Pull Request
1. Push your branch to your fork.
2. Open a PR describing:
   - What was done and why.
   - How to test the change.
   - Impact (including breaking changes, if any).

---

## 📜 PR Checklist
- [ ] Tests added/updated and passing successfully.
- [ ] Documentation (`RULES.md`, `README`, `CHANGELOG`) updated.
- [ ] Commit messages follow **Conventional Commits**.
- [ ] No secrets, credentials, or temporary files were added.

## 🧪 Tests
- Write unit tests for every new rule in `tests/`.
- We maintain a suite based on the native `unittest` framework.

## 🛡️ Security
For reporting vulnerabilities, use GitHub Security Advisories or contact the maintainers confidentially. Avoid publishing exploits in public issues.

Thank you for helping improve the tools for the QGIS community!
