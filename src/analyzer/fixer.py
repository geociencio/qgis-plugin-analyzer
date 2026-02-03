# /***************************************************************************
#  QGIS Plugin Analyzer
#
#  Auto-fix engine for applying code corrections.
#  ***************************************************************************/

import difflib
import pathlib
import subprocess
from typing import Any, Dict, List, Optional, TypedDict

from .transformers import (
    GDALImportTransformer,
    I18nTransformer,
    LegacyImportTransformer,
    PrintToLogTransformer,
    apply_transformation_to_content,
)

# --- Types ---


class FixContext(TypedDict):
    """Context information for a fix handler."""

    project_path: pathlib.Path
    file_path: pathlib.Path
    issue: Dict[str, Any]
    content: str  # Original file content
    dry_run: bool


class FixHandlerResult(TypedDict):
    """Result of a fix execution."""

    applied: bool
    message: str
    new_content: Optional[str]  # Transformed code if applied
    diff: Optional[str]
    error: Optional[str]


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


# --- Fix Registry ---


class FixRegistry:
    """Registry for managing and discovering fix handlers."""

    def __init__(self) -> None:
        self._handlers: Dict[str, Any] = {}

    def register(self, issue_type: str):
        """Decorator to register a fix handler for a specific issue type."""

        def decorator(func):
            self._handlers[issue_type] = func
            return func

        return decorator

    def get_handler(self, issue_type: str) -> Optional[Any]:
        """Retrieves a handler for a given issue type."""
        return self._handlers.get(issue_type)

    def get_all_handlers(self) -> List[Any]:
        """Returns all registered handlers."""
        return list(self._handlers.values())


registry = FixRegistry()


def create_ast_handler(issue_type: str, transformer_cls: Any, description_msg: str) -> Any:
    """Factory function to create standard AST-based handlers.

    Args:
        issue_type: The issue identifier this handler targets.
        transformer_cls: The AST NodeTransformer class to instantiate.
        description_msg: Human-readable description of the fix.

    Returns:
        A handler function compatible with FixRegistry.
    """

    def handler(ctx: FixContext) -> FixHandlerResult:
        if ctx["issue"].get("type") != issue_type:
            return {
                "applied": False,
                "message": "",
                "new_content": None,
                "diff": None,
                "error": None,
            }

        if ctx["dry_run"]:
            return {
                "applied": True,
                "message": description_msg,
                "new_content": None,  # Not computed in dry-run
                "diff": None,
                "error": None,
            }

        transformer = transformer_cls()
        new_code = apply_transformation_to_content(ctx["content"], transformer)

        if new_code is not None:
            return {
                "applied": True,
                "message": description_msg,
                "new_content": new_code,
                "diff": None,
                "error": None,
            }

        return {
            "applied": False,
            "message": "",
            "new_content": None,
            "diff": None,
            "error": None,
        }

    return handler


# --- Fix Handlers Registration ---

registry.register("GDAL_DIRECT_IMPORT")(
    create_ast_handler(
        "GDAL_DIRECT_IMPORT",
        GDALImportTransformer,
        "Replace 'import gdal' with 'from osgeo import gdal'",
    )
)

registry.register("QGIS_LEGACY_IMPORT")(
    create_ast_handler(
        "QGIS_LEGACY_IMPORT",
        LegacyImportTransformer,
        "Replace PyQt4/PyQt5 imports with qgis.PyQt",
    )
)

registry.register("PRINT_STATEMENT")(
    create_ast_handler(
        "PRINT_STATEMENT",
        PrintToLogTransformer,
        "Replace print() with QgsMessageLog.logMessage()",
    )
)

registry.register("MISSING_I18N")(
    create_ast_handler(
        "MISSING_I18N",
        I18nTransformer,
        "Wrap hardcoded string in self.tr()",
    )
)


class AutoFixer:
    """Orchestrates the identification and application of auto-fixes.

    Attributes:
        project_path: Root path of the project.
        dry_run: If True, changes are proposed but not written.
        registry: FixRegistry instance containing handlers.
    """

    def __init__(self, project_path: pathlib.Path, dry_run: bool = True) -> None:
        """Initializes the auto-fixer.

        Args:
            project_path: Root path of the project.
            dry_run: Whether to run in simulation mode.
        """
        self.project_path = project_path
        self.dry_run = dry_run
        self.registry = registry

    def get_fixable_issues(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filters a list of issues to identify those that can be auto-fixed.

        Args:
            issues: A list of issue dictionaries.

        Returns:
            A list of fixable issues, each enriched with a 'handler' function.
        """
        fixable = []
        for issue in issues:
            handler = self.registry.get_handler(issue.get("type", ""))
            if handler:
                # We use a temporary context in dry_run mode to check if handler can fix it
                ctx = self._create_context(pathlib.Path(), issue, "")
                result = handler(ctx)
                if result["applied"]:
                    # Enriched issue with its handler and description
                    issue["handler"] = handler
                    issue["fix_description"] = result["message"]
                    fixable.append(issue)
        return fixable

    def _create_context(
        self, file_path: pathlib.Path, issue: Dict[str, Any], content: str
    ) -> FixContext:
        """Creates a standardized FixContext."""
        return {
            "project_path": self.project_path,
            "file_path": file_path,
            "issue": issue,
            "content": content,
            "dry_run": self.dry_run,
        }

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

    def apply_fixes(self, issues: List[Dict[str, Any]], interactive: bool = True) -> Dict[str, int]:
        """Applies fixes to identified issues, grouping by file.

        Args:
            issues: List of issues to fix.
            interactive: Whether to prompt for confirmation and show diffs.

        Returns:
            A dictionary containing processing statistics (applied, skipped, failed).
        """
        stats = {"applied": 0, "skipped": 0, "failed": 0}

        if not self._check_git_status_with_prompt(interactive):
            return stats

        by_file = self._group_issues_by_file(issues)

        for file_rel, file_issues in by_file.items():
            file_path = self.project_path / file_rel
            print(f"\n📄 {file_rel}")

            try:
                current_content = file_path.read_text(encoding="utf-8")
            except Exception as e:
                print(f"  ❌ Error reading file: {e}")
                stats["failed"] += len(file_issues)
                continue

            file_modified = False
            for issue in file_issues:
                handler = issue.get("handler")
                if not handler:
                    continue

                description = issue.get("fix_description", "Automatic fix")
                print(f"  Line {issue.get('line', '?')}: {description}")

                # Context with current memory buffer
                ctx = self._create_context(file_path, issue, current_content)

                if interactive and not self.dry_run:
                    # In-memory transformation for preview
                    # For interactive mode, we show diff of the single fix
                    work_ctx = ctx.copy()
                    work_ctx["dry_run"] = False
                    result = handler(work_ctx)

                    if result["applied"] and result["new_content"]:
                        show_diff(file_path, current_content, result["new_content"])
                    else:
                        print("    (No changes suggested by handler)")

                    response = input("    Apply fix? [y/n/q]: ").lower()
                    if response == "q":
                        print("Aborted by user.")
                        return stats
                    if response != "y":
                        stats["skipped"] += 1
                        continue

                # Actual application on memory buffer
                if not self.dry_run:
                    work_ctx = ctx.copy()
                    work_ctx["dry_run"] = False
                    result = handler(work_ctx)

                    if result["applied"] and result["new_content"]:
                        current_content = result["new_content"]
                        stats["applied"] += 1
                        file_modified = True
                        print(f"    ✅ Applied: {result['message']}")
                    else:
                        stats["failed"] += 1
                        error = result.get("error", "Transformation returned no changes")
                        print(f"    ❌ Failed: {error}")
                else:
                    # Simulation
                    stats["applied"] += 1

            # Write back the modified content once per file
            if file_modified and not self.dry_run:
                try:
                    file_path.write_text(current_content, encoding="utf-8")
                except Exception as e:
                    print(f"  ❌ Error writing back to file: {e}")
                    # We already counted them as applied, but technically it failed
                    pass

        return stats
