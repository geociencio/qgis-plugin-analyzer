import ast
import unittest
from analyzer.visitors.standards_visitor import StandardsVisitor


class TestStandardsVisitorExtended(unittest.TestCase):
    def test_spatial_index_detection(self):
        code = """
for f in layer.getFeatures():
    pass
for f in layer.getFeatures(QgsFeatureRequest()):
    pass
"""
        tree = ast.parse(code)
        visitor = StandardsVisitor("test.py")
        visitor.visit(tree)
        
        issues = [i for i in visitor.issues if i["type"] == "SPATIAL_INDEX"]
        self.assertEqual(len(issues), 2)

    def test_non_pythonic_loop_detection(self):
        code = """
i = 0
for x in data:
    i += 1
    process(x)
"""
        tree = ast.parse(code)
        visitor = StandardsVisitor("test.py")
        visitor.visit(tree)
        
        issues = [i for i in visitor.issues if i["type"] == "NON_PYTHONIC_LOOP"]
        self.assertEqual(len(issues), 1)
        self.assertIn("Manual counter", issues[0]["message"])

    def test_missing_slot_detection(self):
        code = """
class MyPlugin:
    def initGui(self):
        self.btn.clicked.connect(self.not_existent_method)
    
    def existing_method(self):
        pass
"""
        tree = ast.parse(code)
        visitor = StandardsVisitor("test.py")
        visitor.visit(tree)
        
        issues = [i for i in visitor.issues if i["type"] == "POTENTIAL_MISSING_SLOT"]
        self.assertEqual(len(issues), 1)
        self.assertIn("not_existent_method", issues[0]["message"])

    def test_iface_as_argument(self):
        code = "def my_func(iface: QgisInterface): pass"
        tree = ast.parse(code)
        visitor = StandardsVisitor("test.py")
        visitor.visit(tree)
        
        issues = [i for i in visitor.issues if i["type"] == "IFACE_AS_ARGUMENT"]
        self.assertEqual(len(issues), 1)

    def test_unsafe_subprocess_shell_true(self):
        code = "subprocess.run('ls', shell=True)"
        tree = ast.parse(code)
        visitor = StandardsVisitor("test.py")
        visitor.visit(tree)
        
        issues = [i for i in visitor.issues if i["type"] == "UNSAFE_SUBPROCESS"]
        self.assertEqual(len(issues), 1)
        self.assertIn("shell=True", issues[0]["message"])


if __name__ == "__main__":
    unittest.main()
