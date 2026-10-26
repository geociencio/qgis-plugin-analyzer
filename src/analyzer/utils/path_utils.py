"""Path and file matching utilities."""

import fnmatch
import pathlib
from typing import Any

# Default patterns to ignore if not specified. They are applied first so a
# later ``!pattern`` (gitignore/.qgisignore/.analyzerignore/--exclude) can
# re-include an explicitly requested path.
DEFAULT_EXCLUDE: tuple[str, ...] = (
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
    ".gitignore",
    ".qgisignore",
    ".analyzer_cache.json",
    "analysis_results/",
    "docs/",
    "tests/",
)

# Prohibited binary extensions per QGIS repository policy
BINARY_EXTENSIONS = {".exe", ".dll", ".so", ".dylib", ".pyd", ".bin", ".a", ".lib"}


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
    """Ordered ignore matcher with gitignore-style negation support.

    Patterns are evaluated in order and the last matching pattern wins, so a
    later ``!pattern`` can re-include a path ignored by a default, a
    ``.gitignore`` entry or an earlier exclude.
    """

    def __init__(self, root_path: pathlib.Path, patterns: list[str]):
        """Initializes the matcher with root path and patterns.

        Args:
            root_path: The project root path.
            patterns: Ordered ignore pattern strings (``!`` negates).
        """
        self.root_path = root_path
        cleaned = [p.strip() for p in patterns if p.strip() and not p.lstrip().startswith("#")]
        # Defaults come first; user/CLI patterns can override them with ``!``.
        self.patterns = [*DEFAULT_EXCLUDE, *cleaned]
        self._cache: dict[str, bool] = {}

    def is_ignored(self, path: pathlib.Path) -> bool:
        """Checks if a path matches the ordered ignore patterns.

        Args:
            path: The path to check.

        Returns:
            True if ignored, False otherwise.
        """
        str_path = str(path)
        if str_path in self._cache:
            return self._cache[str_path]

        try:
            rel_path = path.relative_to(self.root_path).as_posix()
        except ValueError:
            return False

        result = self._check_patterns(rel_path, path.name)
        self._cache[str_path] = result
        return result

    def _check_patterns(self, rel_path: str, name: str) -> bool:
        """Apply patterns in order; the last match wins."""
        ignored = False
        for raw_pattern in self.patterns:
            negated = raw_pattern.startswith("!")
            pattern = raw_pattern[1:] if negated else raw_pattern
            if pattern and self._matches(pattern.strip(), rel_path, name):
                ignored = not negated
        return ignored

    @staticmethod
    def _matches(pattern: str, rel_path: str, name: str) -> bool:
        """Return whether one normalized pattern matches a relative path."""
        if not pattern:
            return False

        anchored = pattern.startswith("/")
        clean = pattern.lstrip("/")
        is_dir = clean.endswith("/")
        clean = clean.rstrip("/")
        if not clean:
            return False

        # ``**/foo`` matches foo at any depth; normalize the common form.
        if clean.startswith("**/"):
            clean = clean[3:]
            if not clean:
                return False

        if is_dir:
            if anchored or "/" in clean:
                return rel_path == clean or rel_path.startswith(clean + "/")
            return clean in rel_path.split("/")

        if anchored or "/" in clean:
            return fnmatch.fnmatch(rel_path, clean)
        if fnmatch.fnmatch(rel_path, clean) or fnmatch.fnmatch(name, clean):
            return True
        # A slash-less pattern also matches a directory component (gitignore
        # semantics for patterns such as ``.venv`` or ``node_modules``).
        return any(fnmatch.fnmatch(part, clean) for part in rel_path.split("/")[:-1])


def load_ignore_patterns(ignore_file: pathlib.Path) -> list[str]:
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


def discover_project_files(project_path: pathlib.Path, matcher: IgnoreMatcher) -> dict[str, Any]:
    """Scans the project directory once to discover all relevant files and metrics.
    This replaces multiple redundant rglob calls, optimizing I/O performance.

    Args:
        project_path: Root path of the project.
        matcher: IgnoreMatcher instance for filtering.

    Returns:
        A dictionary with:
            - python_files: List of Paths to .py files.
            - binaries: List of relative paths to binary files.
            - total_size_mb: Total size of non-ignored files in MB.
            - has_metadata: Boolean indicating if metadata.txt exists.
    """
    python_files = []
    binaries = []
    total_bytes = 0
    has_metadata = False

    for file_path in project_path.rglob("*"):
        if not file_path.is_file():
            continue

        # Check metadata (before ignore to ensure project type detection is robust)
        if file_path.name == "metadata.txt" and file_path.parent == project_path:
            has_metadata = True

        if matcher.is_ignored(file_path):
            continue

        # Basics
        total_bytes += file_path.stat().st_size

        # Classify by extension
        ext = file_path.suffix.lower()
        if ext == ".py":
            python_files.append(file_path)
        elif ext in BINARY_EXTENSIONS:
            binaries.append(str(file_path.relative_to(project_path)))

    return {
        "python_files": python_files,
        "binaries": binaries,
        "total_size_mb": total_bytes / (1024 * 1024),
        "has_metadata": has_metadata,
    }
