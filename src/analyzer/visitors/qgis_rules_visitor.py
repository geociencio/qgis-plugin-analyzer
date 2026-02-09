"""Modular visitor for QGIS-specific rules and transition patterns."""

import ast
from typing import Any, Dict, List, Optional

from .base import BaseVisitor


class QGISRulesVisitor(BaseVisitor):
    """Visitor for modular QGIS standards and PyQt transition patterns.

    Detects:
    - GDAL import style (osgeo vs legacy)
    - PyQt transition (PyQt5 vs PyQt6)
    - Legacy Signal/Slot markers (SIGNAL, SLOT)
    - QGIS Processing framework usage
    """

    def __init__(self, rel_path: str, rules_config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(rel_path, rules_config)
        self.processing_framework = False
        self.gdal_style = "Modern"
        self.qt_imports: Dict[str, List[str]] = {"PyQt5": [], "PyQt6": []}
        self.legacy_signals = 0

    def visit_Import(self, node: ast.Import) -> None:
        """Inspects imports for legacy patterns."""
        for alias in node.names:
            self._check_import_name(alias.name, node.lineno)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Inspects from-imports for legacy patterns."""
        if node.module:
            self._check_import_name(node.module, node.lineno)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Detects QGIS Processing framework baseline."""
        processing_bases = {"QgsProcessingAlgorithm", "QgsProcessingProvider"}
        for base in node.bases:
            name = self._get_node_name(base)
            if name in processing_bases:
                self.processing_framework = True
                break
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Detects legacy SIGNAL/SLOT markers."""
        name = self._get_node_name(node.func)
        if name in ("SIGNAL", "SLOT"):
            self.legacy_signals += 1
            self._report_issue(
                "LEGACY_SIGNAL_SLOT",
                node.lineno,
                f"Legacy '{name}' marker detected. Use modern Python signals.",
                ast.unparse(node),
            )
        self.generic_visit(node)

    def _check_import_name(self, name: str, lineno: int) -> None:
        """Helper to classify imports."""
        # GDAL Style
        if name == "gdal":
            self.gdal_style = "Legacy"
            self._report_issue(
                "LEGACY_GDAL_IMPORT",
                lineno,
                "Legacy 'import gdal' detected. Use 'from osgeo import gdal'.",
                f"import {name}",
            )
        elif name.startswith("osgeo") and self.gdal_style != "Legacy":
            self.gdal_style = "Correct"

        # PyQt Transition
        for version in ["PyQt5", "PyQt6"]:
            if name.startswith(version):
                if name not in self.qt_imports[version]:
                    self.qt_imports[version].append(name)

        if name.startswith("PyQt5"):
            self._report_issue(
                "PYQT5_IMPORT",
                lineno,
                f"PyQt5 import detected: '{name}'. Consider upgrading to PyQt6/PySide6.",
                f"import {name}",
            )

    def _get_node_name(self, node: ast.AST) -> str:
        """Helper to extract name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        return ""
