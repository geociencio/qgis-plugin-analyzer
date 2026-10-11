"""Fix-handler registry and AST-based handler factories.

Registration happens via module import side effects: importing this module
registers every built-in AST handler in the global :data:`registry`. It is
imported eagerly by :mod:`analyzer.fixer` so the registry is never empty —
a registry populated purely by import side effects is fragile (see
``AGENT_LESSONS.md`` 2026-10-10) and is guarded by
``tests/test_fixer_registry.py``.
"""

from typing import Any

from .fix_types import FixContext, FixHandlerResult
from .transformers import (
    GDALImportTransformer,
    I18nTransformer,
    LegacyImportTransformer,
    PrintToLogTransformer,
    apply_transformation_to_content,
)


class FixRegistry:
    """Registry for managing and discovering fix handlers."""

    def __init__(self) -> None:
        self._handlers: dict[str, Any] = {}

    def register(self, issue_type: str):
        """Decorator to register a fix handler for a specific issue type."""

        def decorator(func):
            self._handlers[issue_type] = func
            return func

        return decorator

    def get_handler(self, issue_type: str) -> Any | None:
        """Retrieves a handler for a given issue type."""
        return self._handlers.get(issue_type)


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
