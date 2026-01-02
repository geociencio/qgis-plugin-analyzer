
import ast
import unittest

from analyzer.scanner import QGISASTVisitor


class TestSignalSafety(unittest.TestCase):

    def test_missing_slot_detection(self):
        code = """
class MyDialog:
    def __init__(self):
        self.button.clicked.connect(self.existing_slot)
        self.button.clicked.connect(self.missing_slot) # Should detect this

    def existing_slot(self):
        pass
"""
        tree = ast.parse(code)
        visitor = QGISASTVisitor("dummy.py")
        visitor.visit(tree)

        issues = visitor.issues
        missing_slots = [i for i in issues if i["id"] == "POTENTIAL_MISSING_SLOT"]

        self.assertEqual(len(missing_slots), 1)
        self.assertIn("missing_slot", missing_slots[0]["message"])
        self.assertNotIn("existing_slot", [i["message"] for i in missing_slots])

    def test_inherited_slot_warning(self):
        # Even if allowed in Python, strict check should warn (as designed)
        # Testing behavior confirmation
        code = """
class Child(Parent):
    def __init__(self):
        self.start.connect(self.inherited_method)
"""
        tree = ast.parse(code)
        visitor = QGISASTVisitor("dummy.py")
        visitor.visit(tree)

        # It should warn because 'inherited_method' is not in Child
        issues = visitor.issues
        self.assertTrue(any("inherited_method" in i["message"] for i in issues))

if __name__ == "__main__":
    unittest.main()
