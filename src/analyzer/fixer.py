# /***************************************************************************
#  QGIS Plugin Analyzer
#
#  Auto-fix engine for applying code corrections.
#  ***************************************************************************/

import difflib
import pathlib
import subprocess
import tempfile
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from .transformers import (
    GDALImportTransformer,
    I18nTransformer,
    LegacyImportTransformer,
    PrintToLogTransformer,
    apply_transformation,
)


def check_git_status(project_path: pathlib.Path) -> bool:
    """
    Checks if the working directory is clean.
    Returns True if clean, False if there are uncommitted changes.
    """
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return len(result.stdout.strip()) == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        # Git not available or timeout
        return True  # Don't block if git is not available


def show_diff(file_path: pathlib.Path, original_content: str, new_content: str):
    """Displays a unified diff between original and new content."""
    diff = difflib.unified_diff(
        original_content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile=f"a/{file_path.name}",
        tofile=f"b/{file_path.name}",
        lineterm="",
    )

    print("    " + "─" * 60)
    for line in diff:
        line = line.rstrip()
        if line.startswith("+++") or line.startswith("---"):
            print(f"    {line}")
        elif line.startswith("+"):
            print(f"    \033[32m{line}\033[0m")  # Green
        elif line.startswith("-"):
            print(f"    \033[31m{line}\033[0m")  # Red
        elif line.startswith("@@"):
            print(f"    \033[36m{line}\033[0m")  # Cyan
        else:
            print(f"    {line}")
    print("    " + "─" * 60)


class FixStrategy(ABC):
    """Abstract base class for fix strategies."""

    @abstractmethod
    def can_fix(self, issue: Dict[str, Any]) -> bool:
        """Returns True if this strategy can fix the given issue."""
        pass

    @abstractmethod
    def apply_fix(self, file_path: pathlib.Path, issue: Dict[str, Any]) -> bool:
        """Applies the fix to the file. Returns True if successful."""
        pass

    @abstractmethod
    def get_description(self, issue: Dict[str, Any]) -> str:
        """Returns a human-readable description of the fix."""
        pass


class GDALImportFixer(FixStrategy):
    """Fixes direct GDAL imports."""

    def can_fix(self, issue: Dict[str, Any]) -> bool:
        return issue.get("type") == "GDAL_DIRECT_IMPORT"

    def apply_fix(self, file_path: pathlib.Path, issue: Dict[str, Any]) -> bool:
        transformer = GDALImportTransformer()
        return apply_transformation(file_path, transformer)

    def get_description(self, issue: Dict[str, Any]) -> str:
        return "Replace 'import gdal' with 'from osgeo import gdal'"


class LegacyImportFixer(FixStrategy):
    """Fixes PyQt4/PyQt5 imports."""

    def can_fix(self, issue: Dict[str, Any]) -> bool:
        return issue.get("type") == "QGIS_LEGACY_IMPORT"

    def apply_fix(self, file_path: pathlib.Path, issue: Dict[str, Any]) -> bool:
        transformer = LegacyImportTransformer()
        return apply_transformation(file_path, transformer)

    def get_description(self, issue: Dict[str, Any]) -> str:
        return "Replace PyQt4/PyQt5 imports with qgis.PyQt"


class PrintToLogFixer(FixStrategy):
    """Fixes print() statements to use QgsMessageLog."""

    def can_fix(self, issue: Dict[str, Any]) -> bool:
        # This would need a new rule type in scanner.py
        return issue.get("type") == "PRINT_STATEMENT"

    def apply_fix(self, file_path: pathlib.Path, issue: Dict[str, Any]) -> bool:
        transformer = PrintToLogTransformer()
        return apply_transformation(file_path, transformer)

    def get_description(self, issue: Dict[str, Any]) -> str:
        return "Replace print() with QgsMessageLog.logMessage()"


class I18nFixer(FixStrategy):
    """Wraps hardcoded UI strings in self.tr()."""

    def can_fix(self, issue: Dict[str, Any]) -> bool:
        return issue.get("type") == "MISSING_I18N"

    def apply_fix(self, file_path: pathlib.Path, issue: Dict[str, Any]) -> bool:
        transformer = I18nTransformer()
        return apply_transformation(file_path, transformer)

    def get_description(self, issue: Dict[str, Any]) -> str:
        return "Wrap hardcoded string in self.tr() for internationalization"


class AutoFixer:
    """Orchestrates the auto-fix process."""

    def __init__(self, project_path: pathlib.Path, dry_run: bool = True):
        self.project_path = project_path
        self.dry_run = dry_run
        self.strategies: List[FixStrategy] = [
            GDALImportFixer(),
            LegacyImportFixer(),
            PrintToLogFixer(),
            I18nFixer(),
        ]

    def get_fixable_issues(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filters issues to only those that can be auto-fixed."""
        fixable = []
        for issue in issues:
            for strategy in self.strategies:
                if strategy.can_fix(issue):
                    issue["fixer"] = strategy
                    fixable.append(issue)
                    break
        return fixable

    def apply_fixes(
        self, issues: List[Dict[str, Any]], interactive: bool = True
    ) -> Dict[str, int]:
        """
        Applies fixes to the given issues.

        Returns a dict with counts: {'applied': N, 'skipped': M, 'failed': K}
        """
        stats = {"applied": 0, "skipped": 0, "failed": 0}

        # Git status check
        if not self.dry_run:
            is_clean = check_git_status(self.project_path)
            if not is_clean:
                print("\n⚠️  WARNING: Working directory has uncommitted changes.")
                print("   It's recommended to commit or stash changes before applying fixes.")
                if interactive:
                    response = input("   Continue anyway? [y/N]: ").lower()
                    if response != "y":
                        print("Aborted by user.")
                        return stats
                print()

        # Group by file
        by_file: Dict[str, List[Dict[str, Any]]] = {}
        for issue in issues:
            file_path = issue.get("file", "")
            if file_path not in by_file:
                by_file[file_path] = []
            by_file[file_path].append(issue)

        for file_rel, file_issues in by_file.items():
            file_path = self.project_path / file_rel

            print(f"\n📄 {file_rel}")

            # Read original content for diff
            try:
                original_content = file_path.read_text(encoding="utf-8")
            except Exception as e:
                print(f"  ❌ Error reading file: {e}")
                stats["failed"] += len(file_issues)
                continue

            for issue in file_issues:
                fixer: FixStrategy = issue["fixer"]
                description = fixer.get_description(issue)

                print(f"  Line {issue.get('line', '?')}: {description}")

                if interactive and not self.dry_run:
                    # Show diff preview

                    # Create temp file to test transformation
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
                        tmp.write(original_content)
                        tmp_path = pathlib.Path(tmp.name)

                    try:
                        fixer.apply_fix(tmp_path, issue)
                        new_content = tmp_path.read_text(encoding="utf-8")

                        if new_content != original_content:
                            show_diff(file_path, original_content, new_content)
                    finally:
                        tmp_path.unlink()

                    response = input("    Apply fix? [y/n/q]: ").lower()
                    if response == "q":
                        print("Aborted by user.")
                        return stats
                    if response != "y":
                        stats["skipped"] += 1
                        continue

                if not self.dry_run:
                    success = fixer.apply_fix(file_path, issue)
                    if success:
                        stats["applied"] += 1
                        print("    ✅ Applied")
                    else:
                        stats["failed"] += 1
                        print("    ❌ Failed")
                else:
                    stats["applied"] += 1  # Count as "would apply"

        return stats
