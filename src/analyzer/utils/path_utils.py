"""Path and file matching utilities."""

import fnmatch
import os
import pathlib
from typing import Dict, List

# Default patterns to ignore if not specified
DEFAULT_EXCLUDE = {
    ".venv/",
    "venv/",
    "__pycache__/",
    ".git/",
    ".github/",
    "build/",
    "dist/",
    ".pytest_cache/",
    ".ruff_cache/",
    ".mypy_cache/",
    ".analyzerignore",
    "analysis_results/",
}


def safe_path_resolve(base_path: pathlib.Path, target_path_str: str) -> pathlib.Path:
    """Resolves a target path safely relative to a base path.

    Args:
        base_path: The root directory for resolution.
        target_path_str: The path string to resolve.

    Returns:
        The resolved absolute Path.

    Raises:
        ValueError: If path traversal is detected.
    """
    base_abs = base_path.resolve()
    target_abs = (base_path / target_path_str).resolve()

    # Check if target is still within base
    try:
        target_abs.relative_to(base_abs)
    except (ValueError, RuntimeError):
        raise ValueError(
            f"Path traversal detected: '{target_path_str}' is outside base '{base_path}'"
        ) from None

    return target_abs


class IgnoreMatcher:
    """Handles .analyzerignore patterns using fnmatch-style globbing."""

    def __init__(self, root_path: pathlib.Path, patterns: List[str]):
        """Initializes the matcher with root path and patterns.

        Args:
            root_path: The project root path.
            patterns: List of ignore pattern strings.
        """
        self.root_path = root_path
        # Combine user patterns with defaults
        all_patterns = set(p.strip() for p in patterns if p.strip() and not p.startswith("#"))
        all_patterns.update(DEFAULT_EXCLUDE)
        self.patterns = list(all_patterns)
        self._cache: Dict[str, bool] = {}

    def is_ignored(self, path: pathlib.Path) -> bool:
        """Checks if a path matches any ignore pattern.

        Args:
            path: The path to check.

        Returns:
            True if ignored, False otherwise.
        """
        str_path = str(path)
        if str_path in self._cache:
            return self._cache[str_path]

        try:
            rel_path = path.relative_to(self.root_path)
            str_rel_path = str(rel_path)
            result = self._check_patterns(str_rel_path, path.name)
            self._cache[str_path] = result
            return result
        except ValueError:
            return False

    def _check_patterns(self, str_rel_path: str, name: str) -> bool:
        for pattern in self.patterns:
            # Handle anchored patterns (starting with /)
            is_anchored = pattern.startswith("/")
            clean_pattern = pattern.lstrip("/")

            # Handle directory-specific patterns (ending in /)
            is_dir_pattern = clean_pattern.endswith("/")
            clean_pattern = clean_pattern.rstrip("/")

            if is_dir_pattern:
                if is_anchored:
                    if str_rel_path == clean_pattern or str_rel_path.startswith(
                        clean_pattern + os.sep
                    ):
                        return True
                else:
                    parts = str_rel_path.split(os.sep)
                    if clean_pattern in parts:
                        return True
            else:
                if is_anchored:
                    if fnmatch.fnmatch(str_rel_path, clean_pattern):
                        return True
                else:
                    if fnmatch.fnmatch(str_rel_path, clean_pattern):
                        return True
                    if "/" not in clean_pattern and fnmatch.fnmatch(name, clean_pattern):
                        return True
        return False


def load_ignore_patterns(ignore_file: pathlib.Path) -> List[str]:
    """Loads ignore patterns from a file.

    Args:
        ignore_file: Path to the .analyzerignore file.

    Returns:
        List of pattern strings.
    """
    if not ignore_file.exists():
        return []
    with open(ignore_file) as f:
        return f.readlines()
