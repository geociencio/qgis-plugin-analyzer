# /***************************************************************************
#  QGIS Plugin Analyzer
#
#  Semantic analysis module for cross-file dependency and resource validation.
#  ***************************************************************************/

import pathlib
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Set


class DependencyGraph:
    """Builds and analyzes the module dependency graph."""

    def __init__(self):
        # Maps module path -> set of imported module paths
        self.adjacency_list: Dict[str, Set[str]] = {}
        # Maps module path -> metadata (imports, functions, etc.)
        self.nodes: Dict[str, Dict[str, Any]] = {}

    def add_node(self, module_path: str, data: Dict[str, Any]):
        """Adds a module node to the graph."""
        self.nodes[module_path] = data
        self.adjacency_list[module_path] = set()

    def build_edges(self, project_path: pathlib.Path):
        """Resolves imports to build edges between nodes."""
        for module_path, data in self.nodes.items():
            current_file = project_path / module_path
            current_dir = current_file.parent

            for imp in data.get("imports", []):
                resolved_path = self._resolve_import(imp, current_dir, project_path)
                if resolved_path and resolved_path in self.nodes:
                    self.adjacency_list[module_path].add(resolved_path)

    def _resolve_import(
        self, import_name: str, current_dir: pathlib.Path, project_path: pathlib.Path
    ) -> str:
        """Attempts to resolve a Python import string to a file path in the project."""
        # Handle relative imports (e.g., .utils)
        if import_name.startswith("."):
            # This is a simplification. Ideally AST gives better level info.
            # Assuming same package level for now if single dot
            parts = import_name.lstrip(".").split(".")
            target = current_dir.joinpath(*parts).with_suffix(".py")
            try:
                rel = str(target.relative_to(project_path))
                return rel
            except ValueError:
                pass
            return ""

        # Handle absolute imports within project
        parts = import_name.split(".")
        target = project_path.joinpath(*parts).with_suffix(".py")
        try:
            rel = str(target.relative_to(project_path))
            return rel
        except ValueError:
            # Maybe it is a package (__init__.py)
            target_pkg = project_path.joinpath(*parts) / "__init__.py"
            try:
                rel = str(target_pkg.relative_to(project_path))
                return rel
            except ValueError:
                pass
        return ""

    def detect_cycles(self) -> List[List[str]]:
        """Detects circular import cycles using DFS."""
        visited = set()
        recursion_stack = set()
        cycles = []

        def dfs(node, path):
            visited.add(node)
            recursion_stack.add(node)
            path.append(node)

            for neighbor in self.adjacency_list.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path)
                elif neighbor in recursion_stack:
                    # Cycle found
                    cycle_start_index = path.index(neighbor)
                    cycles.append(path[cycle_start_index:] + [neighbor])

            recursion_stack.remove(node)
            path.pop()

        for node in self.nodes:
            if node not in visited:
                dfs(node, [])

        return cycles

    def get_coupling_metrics(self) -> Dict[str, Dict[str, int]]:
        """Calculates Fan-In and Fan-Out for each module."""
        metrics = {node: {"fan_in": 0, "fan_out": 0} for node in self.nodes}

        for source, targets in self.adjacency_list.items():
            metrics[source]["fan_out"] = len(targets)
            for target in targets:
                if target in metrics:  # Should always be true if graph valid
                    metrics[target]["fan_in"] += 1

        return metrics


class ResourceValidator:
    """Validates Qt resource usage against available qrc/py files."""

    def __init__(self, project_path: pathlib.Path):
        self.project_path = project_path
        self.available_resources: Set[str] = set()

    def scan_project_resources(self, ignore_matcher=None):
        """Scans .qrc files (and potentially converted _rc.py) to find valid resource paths."""
        # Strategy: Parse .qrc files primarily as they are the source of truth
        # Regex to find <file>path/to/icon.png</file> inside <qresource prefix="/plugins/myplugin">

        for qrc_file in self.project_path.rglob("*.qrc"):
            # Skip if matches ignore pattern
            if ignore_matcher and ignore_matcher.is_ignored(qrc_file):
                continue

            try:
                # Use standard xml.etree.ElementTree for robust parsing
                # Note: ElementTree is safe against XXE by default in Python 3.x
                # as it does not resolve entities unless a custom parser is provided.
                try:
                    tree = ET.parse(qrc_file)
                    root = tree.getroot()
                    for qresource in root.findall("qresource"):
                        prefix = qresource.get("prefix", "/")
                        if not prefix.startswith("/"):
                            prefix = "/" + prefix

                        for file_elem in qresource.findall("file"):
                            if file_elem.text:
                                clean_path = file_elem.text.strip()
                                # Construct full resource path: :/prefix/path
                                res_path = f":{prefix}/{clean_path}".replace("//", "/")
                                self.available_resources.add(res_path)
                except ET.ParseError:
                    pass  # Fallback or log warning

            except Exception:
                pass

    def validate_usage(self, resource_matches: List[str]) -> List[str]:
        """Returns a list of resource paths used in code but missing in definition."""
        missing = []
        for res in resource_matches:
            # Simple exact match check.
            # Note: Alias handling is complex without compilation, ignoring for now.
            if res not in self.available_resources:
                missing.append(res)
        return sorted(list(set(missing)))
