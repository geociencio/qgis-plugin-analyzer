# /***************************************************************************
#  QGIS Plugin Analyzer
#
#  AST-based code transformers for auto-fixing common issues.
#  ***************************************************************************/

import ast
import pathlib
from typing import Optional


class GDALImportTransformer(ast.NodeTransformer):
    """AST transformer that replaces direct GDAL imports with the OSGeo version.

    Transforms 'import gdal' into 'from osgeo import gdal'.
    """

    def __init__(self) -> None:
        """Initializes the transformer state."""
        self.changes_made = False

    def visit_Import(self, node: ast.Import) -> Optional[ast.ImportFrom]:
        for alias in node.names:
            if alias.name == "gdal":
                self.changes_made = True
                # Create 'from osgeo import gdal'
                return ast.ImportFrom(
                    module="osgeo",
                    names=[ast.alias(name="gdal", asname=alias.asname)],
                    level=0,
                )
        return node


class LegacyImportTransformer(ast.NodeTransformer):
    """AST transformer that modernizes PyQt4/PyQt5 imports to qgis.PyQt.

    Attributes:
        changes_made: Boolean flag indicating if any changes were applied.
    """

    def __init__(self) -> None:
        """Initializes the transformer state."""
        self.changes_made = False

    def visit_Import(self, node: ast.Import) -> ast.Import:
        for alias in node.names:
            if alias.name.startswith(("PyQt4", "PyQt5")):
                self.changes_made = True
                # Replace PyQt5.QtCore -> qgis.PyQt.QtCore
                new_name = alias.name.replace("PyQt5", "qgis.PyQt").replace("PyQt4", "qgis.PyQt")
                alias.name = new_name
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.ImportFrom:
        if node.module and node.module.startswith(("PyQt4", "PyQt5")):
            self.changes_made = True
            node.module = node.module.replace("PyQt5", "qgis.PyQt").replace("PyQt4", "qgis.PyQt")
        return node


class PrintToLogTransformer(ast.NodeTransformer):
    """AST transformer that replaces print() calls with QgsMessageLog.logMessage().

    Attributes:
        changes_made: Boolean flag indicating if any changes were applied.
        needs_import: Boolean flag indicating if a new import is required.
    """

    def __init__(self) -> None:
        """Initializes the transformer state."""
        self.changes_made = False
        self.needs_import = False

    def visit_Expr(self, node: ast.Expr) -> ast.Expr:
        # Check if it's a print() call
        if isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Name) and node.value.func.id == "print":
                self.changes_made = True
                self.needs_import = True

                # Get the message argument
                if node.value.args:
                    message = node.value.args[0]
                else:
                    message = ast.Constant(value="")

                # Create QgsMessageLog.logMessage(message, "Plugin", Qgis.Info)
                new_call = ast.Expr(
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id="QgsMessageLog", ctx=ast.Load()),
                            attr="logMessage",
                            ctx=ast.Load(),
                        ),
                        args=[
                            message,
                            ast.Constant(value="Plugin"),
                            ast.Attribute(
                                value=ast.Name(id="Qgis", ctx=ast.Load()),
                                attr="Info",
                                ctx=ast.Load(),
                            ),
                        ],
                        keywords=[],
                    )
                )
                return new_call
        return node


class I18nTransformer(ast.NodeTransformer):
    """AST transformer that wraps UI strings in self.tr() for internationalization.

    Attributes:
        changes_made: Boolean flag indicating if any changes were applied.
        i18n_methods: Set of method names that accept strings for UI display.
    """

    def __init__(self) -> None:
        """Initializes the transformer state."""
        self.changes_made = False
        self.i18n_methods = {
            "setText",
            "setWindowTitle",
            "setTitle",
            "setToolTip",
            "setPlaceholderText",
            "setTabText",
        }

    def visit_Call(self, node: ast.Call) -> ast.Call:
        # Check if it's a UI method call with a string literal
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in self.i18n_methods:
                # Check if first argument is a string literal
                if node.args and isinstance(node.args[0], ast.Constant):
                    if isinstance(node.args[0].value, str):
                        val = node.args[0].value
                        # Skip empty strings or placeholders
                        if val.strip() and not val.startswith("%"):
                            self.changes_made = True
                            # Wrap in self.tr()
                            node.args[0] = ast.Call(
                                func=ast.Attribute(
                                    value=ast.Name(id="self", ctx=ast.Load()),
                                    attr="tr",
                                    ctx=ast.Load(),
                                ),
                                args=[ast.Constant(value=val)],
                                keywords=[],
                            )
        self.generic_visit(node)
        return node


def apply_transformation(file_path: pathlib.Path, transformer: ast.NodeTransformer) -> bool:
    """Applies an AST transformation to a file and writes back the modified code.

    Args:
        file_path: Path to the Python file to transform.
        transformer: The AST node transformer to apply.

    Returns:
        True if the file was modified, False otherwise.
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        # Apply transformation
        new_tree = transformer.visit(tree)
        ast.fix_missing_locations(new_tree)

        if hasattr(transformer, "changes_made") and transformer.changes_made:
            # Unparse back to code
            new_code = ast.unparse(new_tree)

            # Add necessary imports if needed
            if hasattr(transformer, "needs_import") and transformer.needs_import:
                if "from qgis.core import QgsMessageLog, Qgis" not in new_code:
                    new_code = "from qgis.core import QgsMessageLog, Qgis\n\n" + new_code

            file_path.write_text(new_code, encoding="utf-8")
            return True

        return False
    except Exception as e:
        print(f"Error transforming {file_path}: {e}")
        return False
