
---
description: Creates commit ensuring quality (Ruff), metrics, and changelog.
---

# Workflow: Create Commit (Enhanced)

This workflow is the gold standard for saving changes. It not only commits but cleans the code, updates project memory, and ensures documentation.

## Workflow Steps

1.  **Code Hygiene (Automatic)**:
    First and foremost, ensures code is clean and formatted to avoid CI rejections.
    // turbo
    ```bash
    uv run ruff check --fix .
    uv run ruff format .
    ```

2.  **Impact Sync (AI)**:
    Updates metrics to understand how these changes affect project complexity.
    // turbo
    ```bash
    ai-ctx analyze
    ```

3.  **Update CHANGELOG.md**:
    *   Checks `git status`.
    *   Inserts a concise line in the `[Unreleased]` section of `CHANGELOG.md` describing the value added.

4.  **Generate Commit Message**:
    Drafts a message following the guidelines in `docs/development/COMMIT_GUIDELINES.md`.
    *   **Format**: `<type>: <description in English>`
    *   **Types**: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`.

5.  **Execution**:
    Consolidates the changes.
    // turbo
    ```bash
    git add .
    git commit -m "<generated_message>"
    ```

## Important Notes
- If `ruff` modified files in step 1, those changes will be included automatically in the commit.
- If the generated message doesn't convince you, edit it before approving the final command.
