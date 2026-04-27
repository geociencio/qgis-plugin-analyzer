import ast
import unittest

from analyzer.utils.ast_utils import calculate_complexity
from analyzer.visitors.i18n_visitor import I18nVisitor
from analyzer.visitors.qgis_rules_visitor import QGISRulesVisitor


class TestAdvancedFeatures(unittest.TestCase):
    def test_density_complexity_penalty(self):
        """Test that density-based complexity penalty is applied."""
        # Case 1: Low density (10 lines for 4 decision points)
        code_low_density = """
def func():
    if a:
        print(1)
    if b:
        print(2)
    if c:
        print(3)
    # Some filler
    # Some filler
    # Some filler
    if d:
        print(4)
"""
        tree_low = ast.parse(code_low_density)
        # Complexity: 1 (base) + 4 (ifs) = 5
        # 4 decisions in approx 10 lines -> density < 0.5
        comp_low = calculate_complexity(tree_low)
        self.assertEqual(comp_low, 5)

        # Case 2: High density (4 lines for 4 decision points)
        code_high_density = """
def func():
    if a: pass
    if b: pass
    if c: pass
    if d: pass
"""
        tree_high = ast.parse(code_high_density)
        # Complexity base: 5
        # 4 decisions in 4 lines -> density = 1.0 > 0.5
        # Penalty: 5 * 1.5 = 7.5 -> 7
        comp_high = calculate_complexity(tree_high)
        self.assertEqual(comp_high, 7)

    def test_i18n_heuristics(self):
        """Test that i18n heuristics correctly filter strings."""
        visitor = I18nVisitor("test.py")

        # Valid translatable strings
        self.assertTrue(visitor.is_translatable_string("Click Here"))
        self.assertTrue(visitor.is_translatable_string("Are you sure?"))
        self.assertTrue(visitor.is_translatable_string("cancel"))  # lowercase word is candidate

        # Invalid strings (technical)
        self.assertFalse(visitor.is_translatable_string("id"))  # too short
        self.assertFalse(visitor.is_translatable_string("/path/to/icon.png"))  # path
        self.assertFalse(visitor.is_translatable_string("column_name"))  # snake_case
        self.assertFalse(visitor.is_translatable_string("PascalCase"))  # Camel/PascalCase
        self.assertFalse(visitor.is_translatable_string("CONSTANT_NAME"))  # Uppercase
        self.assertFalse(visitor.is_translatable_string(":/plugins/myicon.svg"))  # QRC path

    def test_qgis_rules_visitor_imports(self):
        """Test QGISRulesVisitor import detection."""
        visitor = QGISRulesVisitor("test.py")
        code = "import gdal\nimport PyQt5.QtWidgets\nfrom osgeo import ogr"
        visitor.visit(ast.parse(code))

        self.assertEqual(visitor.gdal_style, "Legacy")
        self.assertIn("PyQt5.QtWidgets", visitor.qt_imports["PyQt5"])

        # Check issues reported
        issue_types = [i["type"] for i in visitor.issues]
        self.assertIn("LEGACY_GDAL_IMPORT", issue_types)
        self.assertIn("PYQT5_IMPORT", issue_types)

    def test_qgis_rules_visitor_signals(self):
        """Test QGISRulesVisitor legacy signal detection."""
        visitor = QGISRulesVisitor("test.py")
        code = "self.emit(SIGNAL('triggered()'))"
        visitor.visit(ast.parse(code))

        self.assertEqual(visitor.legacy_signals, 1)
        issue_types = [i["type"] for i in visitor.issues]
        self.assertIn("LEGACY_SIGNAL_SLOT", issue_types)

    def test_qgis_rules_visitor_processing(self):
        """Test QGISRulesVisitor processing framework detection."""
        visitor = QGISRulesVisitor("test.py")
        code = "class MyAlg(QgsProcessingAlgorithm): pass"
        visitor.visit(ast.parse(code))

        self.assertTrue(visitor.processing_framework)


if __name__ == "__main__":
    unittest.main()
