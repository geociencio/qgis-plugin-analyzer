import unittest
import ast
import pathlib
import tempfile
import shutil
from analyzer.transformers import (
    GDALImportTransformer,
    LegacyImportTransformer,
    PrintToLogTransformer,
    I18nTransformer,
    apply_transformation,
)


class TestTransformers(unittest.TestCase):
    def setUp(self):
        self.test_dir = pathlib.Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_gdal_import_transformer(self):
        code = "import gdal\n"
        tree = ast.parse(code)
        transformer = GDALImportTransformer()
        new_tree = transformer.visit(tree)
        
        self.assertTrue(transformer.changes_made)
        new_code = ast.unparse(new_tree)
        self.assertIn("from osgeo import gdal", new_code)
        # Verify it's not a standalone "import gdal" statement
        self.assertNotRegex(new_code, r'^\s*import gdal\s*$', msg="Should not have standalone 'import gdal'")

    def test_legacy_import_transformer(self):
        code = "from PyQt5.QtCore import Qt\n"
        tree = ast.parse(code)
        transformer = LegacyImportTransformer()
        new_tree = transformer.visit(tree)
        
        self.assertTrue(transformer.changes_made)
        new_code = ast.unparse(new_tree)
        self.assertIn("from qgis.PyQt.QtCore import Qt", new_code)

    def test_print_to_log_transformer(self):
        code = 'print("Hello")\n'
        tree = ast.parse(code)
        transformer = PrintToLogTransformer()
        new_tree = transformer.visit(tree)
        
        self.assertTrue(transformer.changes_made)
        self.assertTrue(transformer.needs_import)
        new_code = ast.unparse(new_tree)
        self.assertIn("QgsMessageLog.logMessage", new_code)
        self.assertNotIn("print", new_code)

    def test_i18n_transformer(self):
        code = '''
class MyDialog:
    def setup_ui(self):
        self.button.setText("Click Me")
'''
        tree = ast.parse(code)
        transformer = I18nTransformer()
        new_tree = transformer.visit(tree)
        
        self.assertTrue(transformer.changes_made)
        new_code = ast.unparse(new_tree)
        self.assertIn("self.tr('Click Me')", new_code)
        # Verify the original hardcoded string is wrapped
        self.assertNotRegex(new_code, r'setText\(["\']Click Me["\']\)')

    def test_apply_transformation_to_file(self):
        test_file = self.test_dir / "test.py"
        test_file.write_text("import gdal\n")
        
        transformer = GDALImportTransformer()
        result = apply_transformation(test_file, transformer)
        
        self.assertTrue(result)
        new_content = test_file.read_text()
        self.assertIn("from osgeo import gdal", new_content)

    def test_no_changes_when_not_needed(self):
        code = "from osgeo import gdal\n"
        tree = ast.parse(code)
        transformer = GDALImportTransformer()
        transformer.visit(tree)
        
        self.assertFalse(transformer.changes_made)


if __name__ == "__main__":
    unittest.main()
