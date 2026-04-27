import ast
import unittest

from analyzer.visitors.imports_visitor import ImportsVisitor


class TestImportsVisitor(unittest.TestCase):
    def test_gdal_direct_import(self):
        visitor = ImportsVisitor("test.py")
        code = "import gdal"
        visitor.visit(ast.parse(code))

        issue_types = [i["type"] for i in visitor.issues]
        self.assertIn("GDAL_DIRECT_IMPORT", issue_types)

    def test_legacy_pyqt_import(self):
        visitor = ImportsVisitor("test.py")
        code = "from PyQt5.QtWidgets import QDialog\nimport PyQt4.QtCore"
        visitor.visit(ast.parse(code))

        issue_types = [i["type"] for i in visitor.issues]
        self.assertIn("QGIS_LEGACY_IMPORT", issue_types)
        self.assertEqual(issue_types.count("QGIS_LEGACY_IMPORT"), 2)

    def test_protected_member_import(self):
        visitor = ImportsVisitor("test.py")
        code = "import qgis._gui"
        visitor.visit(ast.parse(code))

        issue_types = [i["type"] for i in visitor.issues]
        self.assertIn("QGIS_PROTECTED_MEMBER", issue_types)

        # Should NOT report for qgis._3d (it's a known exception)
        visitor_3d = ImportsVisitor("test.py")
        visitor_3d.visit(ast.parse("import qgis._3d"))
        self.assertEqual(len(visitor_3d.issues), 0)

    def test_heavy_logic_ui(self):
        # Should report in UI files
        visitor_ui = ImportsVisitor("my_gui.py")
        code = "import pandas as pd\nfrom sklearn.model_selection import train_test_split"
        visitor_ui.visit(ast.parse(code))

        issue_types = [i["type"] for i in visitor_ui.issues]
        self.assertIn("HEAVY_LOGIC_UI", issue_types)

        # Should NOT report in core files
        visitor_core = ImportsVisitor("core_logic.py")
        visitor_core.visit(ast.parse(code))
        self.assertEqual(len(visitor_core.issues), 0)


if __name__ == "__main__":
    unittest.main()
