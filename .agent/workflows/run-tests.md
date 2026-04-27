---
description: How to run unit tests reliably
agent: QA Engineer
skills: [qa-docker, qa-standards]
validation: |
  - Verify that all tests pass
  - Confirm that there are no regressions
---

# Workflow: Run Tests

This workflow ensures that the project's stability is verified through unit and integration tests.

### 1. Run Tests (Local)
Always set `PYTHONPATH=src` (or the appropriate source directory) when running tests from the project root.
// turbo
```bash
env PYTHONPATH=src uv run python3 -m unittest discover tests
```

### 2. Recommended Method (Docker - Complete)
The definitive health check is running all tests in an isolated Docker container:
// turbo
```bash
docker build -t qgis-analyzer-qa -f docker/QA.Dockerfile . && docker run --rm qgis-analyzer-qa pytest
```

**Key Notes:**
- The project uses `unittest` for the core suite.
- Ensure `uv.lock` is synchronized before running tests (`uv sync`).

🤖 **Agent Action**: Use **qa-standards** skill to interpret failures and validate the testing strategy.

## Expected Result
- Clear report of the project's stability status.
- Identification of regressions or environment-specific failures.
- Confirmation of whether the code is safe to be integrated.

## Structured Result Summary
🤖 **Agent Action**: Conclude with a YAML block summarizing the test run:
```yaml
test_run: complete
total_tests: [count]
passed: [count]
failed: [count]
errors: [count]
coverage: [percentage]
```
