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
    """Checks if the Git working directory is clean.

    Args:
        project_path: Root path of the Git project.

    Returns:
        True if there are no uncommitted changes, False otherwise.
        Returns True if Git is not available.
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


def show_diff(file_path: pathlib.Path, original_content: str, new_content: str) -> None:
    """Displays a colorized unified diff between original and new content.

    Args:
        file_path: Path to the file being compared.
        original_content: The original content of the file.
        new_content: The modified content of the file.
    """
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
    """Abstract base class for all auto-fix strategies."""

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
    """Orchestrates the identification and application of auto-fixes.

    Attributes:
        project_path: Root path of the project.
        dry_run: If True, changes are proposed but not written.
        strategies: List of available fix strategies.
    """

    def __init__(self, project_path: pathlib.Path, dry_run: bool = True) -> None:
        """Initializes the auto-fixer.

        Args:
            project_path: Root path of the project.
            dry_run: Whether to run in simulation mode.
        """
        self.project_path = project_path
        self.dry_run = dry_run
        self.strategies: List[FixStrategy] = [
            GDALImportFixer(),
            LegacyImportFixer(),
            PrintToLogFixer(),
            I18nFixer(),
        ]

    def get_fixable_issues(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filters a list of issues to identify those that can be auto-fixed.

        Args:
            issues: A list of issue dictionaries.

        Returns:
            A list of fixable issues, each enriched with a 'fixer' strategy.
        """
        fixable = []
        for issue in issues:
            for strategy in self.strategies:
                if strategy.can_fix(issue):
                    issue["fixer"] = strategy
                    fixable.append(issue)
                    break
        return fixable

    def _check_git_status_with_prompt(self, interactive: bool) -> bool:
        """Checks git status and prompts user if needed. Returns True to continue."""
        if self.dry_run:
            return True

        is_clean = check_git_status(self.project_path)
        if not is_clean:
            print("\n⚠️  WARNING: Working directory has uncommitted changes.")
            print("   It's recommended to commit or stash changes before applying fixes.")
            if interactive:
                response = input("   Continue anyway? [y/N]: ").lower()
                if response != "y":
                    print("Aborted by user.")
                    return False
            print()
        return True

    def _group_issues_by_file(
        self, issues: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Groups issues by file path."""
        by_file: Dict[str, List[Dict[str, Any]]] = {}
        for issue in issues:
            file_path = issue.get("file", "")
            if file_path not in by_file:
                by_file[file_path] = []
            by_file[file_path].append(issue)
        return by_file

    def _apply_single_fix(
        self,
        file_path: pathlib.Path,
        issue: Dict[str, Any],
        original_content: str,
        interactive: bool,
        stats: Dict[str, int],
    ) -> bool:
        """Applies a single fix and updates stats. Returns True to continue, False to abort."""
        fixer: FixStrategy = issue["fixer"]
        description = fixer.get_description(issue)

        print(f"  Line {issue.get('line', '?')}: {description}")

        if interactive and not self.dry_run:
            # Show diff preview
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
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
                return False
            if response != "y":
                stats["skipped"] += 1
                return True

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

        return True

    def apply_fixes(self, issues: List[Dict[str, Any]], interactive: bool = True) -> Dict[str, int]:
        """Applies fixes to identified issues, grouping by file.

        Args:
            issues: List of issues to fix.
            interactive: Whether to prompt for confirmation and show diffs.

        Returns:
            A dictionary containing processing statistics (applied, skipped, failed).
        """
        stats = {"applied": 0, "skipped": 0, "failed": 0}

        # Git status check
        if not self._check_git_status_with_prompt(interactive):
            return stats

        # Group by file
        by_file = self._group_issues_by_file(issues)

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
                if not self._apply_single_fix(
                    file_path, issue, original_content, interactive, stats
                ):
                    return stats

        return stats
