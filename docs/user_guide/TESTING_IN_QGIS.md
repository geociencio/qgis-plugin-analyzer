# Testing Inside QGIS (No Mocks Required) 🌍

If you want to run tests that interact with the real `qgis` API (without mocking), you can execute them directly inside the **QGIS Runtime** (e.g., via the Python Console).

## Why do this?
- **Real Integration**: Verify that your code works with the actual C++ bindings.
- **No Mocks**: `qgis.core`, `iface`, and `qgis.gui` are fully available.
- **Visual Feedback**: You can see layers being loaded or UI widgets appearing.

## Workflow

### 1. The Test Runner Script
Save this script as `scripts/run_tests_in_qgis.py` in your project:

```python
import sys
import os
import unittest
import logging

# 1. Add your project path to sys.path
PROJECT_ROOT = "/path/to/your/project"  # CHANGE THIS
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 2. Setup Logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

def run_tests():
    """Discover and run tests inside QGIS."""
    # Reload modules if needed (optional, for iterative dev)
    # import my_module
    # import importlib
    # importlib.reload(my_module)

    # 3. Create Test Suite
    loader = unittest.TestLoader()
    # Discover tests in the 'tests' directory
    suite = loader.discover(
        start_dir=os.path.join(PROJECT_ROOT, "tests"),
        pattern="test_*.py"
    )

    # 4. Run Runner
    print("🚀 Running Tests inside QGIS...")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result

# Execute
if __name__ == "__console__":
    run_tests()
```

### 2. Execution in QGIS
1. Open **QGIS**.
2. Open the **Python Console** (`Ctrl+Alt+P`).
3. Click the **"Show Editor"** button (notepad icon).
4. Open the `scripts/run_tests_in_qgis.py` file.
5. Click **Run Script** (Play button).

### 3. CI/CD (Headless)
For CI, you can use `qgis_process` or launch QGIS with a startup script:

```bash
qgis --nologo --noversion --code scripts/run_tests_in_qgis.py
```
