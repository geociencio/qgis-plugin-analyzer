import ast
import pathlib
import shutil
import tempfile
import unittest

from analyzer.semantic import DependencyGraph, ResourceValidator
from analyzer.utils.ast_utils import extract_runtime_imports_from_ast


class TestSemanticAnalysis(unittest.TestCase):
    """Unit tests for semantic analysis (dependency graph and resource validation)."""

    def setUp(self) -> None:
        """Sets up the test environment for semantic analysis."""
        self.test_dir = pathlib.Path(tempfile.mkdtemp())
        self.graph = DependencyGraph()

    def tearDown(self) -> None:
        """Cleans up temporary resources."""
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
        self.assertGreaterEqual(len(cycles), 1)  # A->B->A cycle detected

        # Verify cycle content
        self.assertTrue(any("a.py" in c and "b.py" in c for c in cycles))

    def test_coupling_metrics(self):
        # A imports B and C
        # B imports C
        self.graph.adjacency_list = {"a": {"b", "c"}, "b": {"c"}, "c": set()}
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

        missing = validator.validate_usage(
            [":/plugins/test/icon.png", ":/plugins/test/missing.png"]
        )

        self.assertEqual(len(missing), 1)
        self.assertEqual(missing[0], ":/plugins/test/missing.png")

    def test_cycle_deduplication(self):
        """A single cycle A->B->A must be reported exactly once, not twice."""
        # A -> B -> A: DFS enters from both A and B, but canonical form deduplicates
        self.graph.add_node("a.py", {})
        self.graph.add_node("b.py", {})
        self.graph.adjacency_list["a.py"] = {"b.py"}
        self.graph.adjacency_list["b.py"] = {"a.py"}

        cycles = self.graph.detect_cycles()
        self.assertEqual(
            len(cycles), 1, f"Expected 1 cycle, got {len(cycles)}: {cycles}"
        )

    def test_resolve_nonexistent_file(self):
        """_resolve_import must return '' for modules that don't exist on disk."""
        project = pathlib.Path(tempfile.mkdtemp())
        try:
            # Create only module_a.py; module_b does NOT exist
            (project / "module_a.py").write_text("")
            self.graph.add_node("module_a.py", {"imports": ["module_b"]})
            self.graph.add_node(
                "module_b.py", {}
            )  # node exists in graph but not on disk

            self.graph.build_edges(project)

            # No edge should be created because module_b.py doesn't exist on disk
            self.assertEqual(
                self.graph.adjacency_list["module_a.py"],
                set(),
                "Should not create edge to non-existent file",
            )
        finally:
            import shutil as _shutil

            _shutil.rmtree(project)

    def test_type_checking_imports_excluded(self):
        """extract_runtime_imports_from_ast must exclude TYPE_CHECKING-guarded imports."""
        code = """
from __future__ import annotations
from typing import TYPE_CHECKING

import os  # runtime import

if TYPE_CHECKING:
    from .other_module import SomeType  # type-only, NOT runtime
"""
        tree = ast.parse(code)
        runtime_imports = extract_runtime_imports_from_ast(tree)

        self.assertIn("os", runtime_imports)
        self.assertNotIn(".other_module", runtime_imports)


if __name__ == "__main__":
    unittest.main()
