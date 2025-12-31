
import unittest
import pathlib
import tempfile
import shutil
from analyzer.semantic import DependencyGraph, ResourceValidator

class TestSemanticAnalysis(unittest.TestCase):
    def setUp(self):
        self.test_dir = pathlib.Path(tempfile.mkdtemp())
        self.graph = DependencyGraph()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_cycle_detection(self):
        # A -> B -> A
        self.graph.add_node("a.py", {"imports": ["b"]})
        self.graph.add_node("b.py", {"imports": ["a"]})
        
        # Mock file system resolution
        # We manually build edges to bypass file system check for this unit test
        self.graph.adjacency_list["a.py"] = {"b.py"}
        self.graph.adjacency_list["b.py"] = {"a.py"}

        cycles = self.graph.detect_cycles()
        self.assertGreaterEqual(len(cycles), 1) # A->B->A cycle detected
        
        # Verify cycle content
        self.assertTrue(any("a.py" in c and "b.py" in c for c in cycles))

    def test_coupling_metrics(self):
        # A imports B and C
        # B imports C
        self.graph.adjacency_list = {
            "a": {"b", "c"},
            "b": {"c"},
            "c": set()
        }
        # Populate nodes keys
        self.graph.nodes = {"a": {}, "b": {}, "c": {}}
        
        metrics = self.graph.get_coupling_metrics()
        
        self.assertEqual(metrics["a"]["fan_out"], 2)
        self.assertEqual(metrics["c"]["fan_in"], 2)
        self.assertEqual(metrics["b"]["fan_in"], 1)

    def test_resource_validator(self):
        # Create dummy .qrc
        qrc_content = """<RCC>
            <qresource prefix="/plugins/test">
                <file>icon.png</file>
                <file>images/logo.svg</file>
            </qresource>
        </RCC>"""
        (self.test_dir / "resources.qrc").write_text(qrc_content)
        
        validator = ResourceValidator(self.test_dir)
        validator.scan_project_resources()
        
        self.assertIn(":/plugins/test/icon.png", validator.available_resources)
        self.assertIn(":/plugins/test/images/logo.svg", validator.available_resources)
        
        missing = validator.validate_usage([
            ":/plugins/test/icon.png",
            ":/plugins/test/missing.png"
        ])
        
        self.assertEqual(len(missing), 1)
        self.assertEqual(missing[0], ":/plugins/test/missing.png")

if __name__ == "__main__":
    unittest.main()
