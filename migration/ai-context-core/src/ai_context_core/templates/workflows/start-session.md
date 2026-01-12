
---
description: Initializes the session: updates metrics, loads critical context, and verifies environment.
---

This workflow prepares the environment for a productive development session.

1.  **Context Tuning**:
    Executes project analysis and **reads** the resulting memory files to understand the current state.
    // turbo
    ```bash
    ai-ctx analyze
    ```
    
    Reads the following files to load the context into memory:
    *   `.ai-context/project_brain.md`
    *   `AI_CONTEXT.md`
    *   `docs/DEVELOPMENT_LOG.md`
    *   `task.md`

2.  **Environment Sync**:
    Ensures dependencies are synchronized.
    // turbo
    ```bash
    uv sync
    ```

3.  **Sanity Check (Tests)**:
    Verifies that the codebase is stable before starting work.
    ```bash
    uv run python -m unittest discover tests
    ```
