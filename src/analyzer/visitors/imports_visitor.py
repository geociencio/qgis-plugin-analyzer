"""AST visitor for import validation and analysis."""

import ast
from typing import Any, cast

from .base import BaseVisitor


class ImportsVisitor(BaseVisitor):
    """Visitor focused on import-related checks.

    Detects issues like:
    - Direct GDAL imports
    - Legacy PyQt4/PyQt5 imports
    - Protected member imports
    - Heavy dependencies in UI files
    """

    def visit_Import(self, node: ast.Import) -> None:
        """Analyzes import nodes.

        Args:
            node: The import AST node.
        """
        for alias in node.names:
            self._check_import_name(alias.name, node, ast.unparse(node))
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Analyzes 'from import' nodes.

        Args:
            node: The import-from AST node.
        """
        if node.module:
            self._check_import_name(node.module, node, ast.unparse(node))

            # HEAVY_LOGIC_UI check
            heavy_libs = {"pandas", "numpy", "scipy", "sklearn", "matplotlib"}
            is_ui_file = "gui" in self.rel_path.lower() or "ui" in self.rel_path.lower()
            if is_ui_file and (
                node.module in heavy_libs or node.module.split(".")[0] in heavy_libs
            ):
                self._report_issue(
                    "HEAVY_LOGIC_UI",
                    node.lineno,
                    f"Heavy dependency '{node.module}' detected in UI file. Move logic to core.",
                    ast.unparse(node),
                )
        self.generic_visit(node)

    def _check_import_name(self, name: str, node: ast.AST, code_snippet: str) -> None:
        """Checks a single import name for violations.

        Args:
            name: The import name to check.
            node: The AST node containing the import.
            code_snippet: String representation of the import statement.
        """
        # QGIS_PROTECTED_MEMBER
        if name.startswith("qgis._") and not name.startswith("qgis._3d"):
            self._report_issue(
                "QGIS_PROTECTED_MEMBER",
                cast(Any, node).lineno,
                f"Protected member import detected: '{name}'. Protected members are unstable.",
                code_snippet,
            )

        # GDAL_DIRECT_IMPORT
        if name == "gdal":
            self._report_issue(
                "GDAL_DIRECT_IMPORT",
                cast(Any, node).lineno,
                "Direct 'gdal' import detected. Use 'from osgeo import gdal'.",
                code_snippet,
            )

        # QGIS_LEGACY_IMPORT
        if name.startswith(("PyQt4", "PyQt5")):
            self._report_issue(
                "QGIS_LEGACY_IMPORT",
                cast(Any, node).lineno,
                f"Legacy import detected: '{name}'. Use 'qgis.PyQt' for compatibility.",
                code_snippet,
            )
