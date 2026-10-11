"""Type definitions for the auto-fix engine.

These TypedDicts describe the contract shared between the fix registry
(handlers) and :class:`analyzer.fixer.AutoFixer`.
"""

import pathlib
from typing import Any, TypedDict


class FixContext(TypedDict):
    """Context information for a fix handler."""

    project_path: pathlib.Path
    file_path: pathlib.Path
    issue: dict[str, Any]
    content: str  # Original file content
    dry_run: bool


class FixHandlerResult(TypedDict):
    """Result of a fix execution."""

    applied: bool
    message: str
    new_content: str | None  # Transformed code if applied
    diff: str | None
    error: str | None
