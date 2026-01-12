
---
description: Ends session: runs tests, updates logs (Dev/Maintenance), regenerates AI context, and proposes closing commit.
---

This workflow ensures a clean and documented closure of the work performed.

1.  **Sanity Check (Tests)**:
    Verifies that we haven't broken anything critical before leaving.
    ```bash
    uv run python -m unittest discover tests
    ```

2.  **Memory Update (Logs)**:
    *   Reads `docs/DEVELOPMENT_LOG.md`.
    *   Generates and writes a new entry with today's date (`## [YYYY-MM-DD] Summary`) summarizing the achievements of this session.
    *   If there were structural changes, updates `docs/source/MAINTENANCE_LOG.md`.

3.  **Final Context Sync**:
    Updates the metrics and long-term memory of the project.
    // turbo
    ```bash
    ai-ctx analyze
    ```

4.  **Closing Commit (Proposal)**:
    Reviews the status and proposes a commit.
    ```bash
    git status
    ```
    (The model will propose `git add .` and `git commit` with an appropriate message based on the context. Wait for confirmation).

5.  **Farewell**:
    Shows a final summary of what was achieved and closes the session.
