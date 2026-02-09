"""Graph command implementation for dependency visualization."""

import argparse

from ..base import BaseAnalyzerCommand


class GraphCommand(BaseAnalyzerCommand):
    """Command to visualize dependency graphs and architectural cycles."""

    @property
    def name(self) -> str:
        """Command name."""
        return "graph"

    @property
    def help(self) -> str:
        """Command help text."""
        return "Visualize dependency graphs and architectural cycles"

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        """Configure graph command arguments.

        Args:
            parser: The argument parser for this command.
        """
        parser.add_argument(
            "project_path",
            nargs="?",
            default=".",
            help="Path to the QGIS project to analyze (default: current directory)",
        )
        self.add_common_args(parser, include_output=True, include_strict=False)
        parser.add_argument(
            "--format",
            choices=["text", "mermaid"],
            default="text",
            help="Output format (default: text)",
        )

    def execute(self, args: argparse.Namespace) -> int:
        """Execute the graph command.

        Args:
            args: Parsed command-line arguments.

        Returns:
            Exit code (0 for success).
        """
        print(f"🕸️  Analyzing dependencies for: {args.project_path}...")

        from ...utils import discover_project_files

        analyzer = self.get_analyzer(args)

        # We need to run the analysis to get the metadata
        discovery = discover_project_files(analyzer.project_path, analyzer.matcher)
        files = discovery["python_files"]
        rules_config = analyzer.config.rules

        modules_data = analyzer._run_parallel_analysis(files, rules_config)
        semantic = analyzer._run_semantic_analysis(modules_data)

        cycles = semantic.get("cycles", [])
        graph = semantic.get("graph", {})

        if args.format == "mermaid":
            self._print_mermaid(graph, cycles)
        else:
            self._print_text(graph, cycles)

        return 0

    def _print_text(self, graph: dict, cycles: list) -> None:
        """Print ASCII dependency summary."""
        print("\n📊 Dependency Summary")
        print("=" * 30)

        if not graph:
            print("No dependencies detected.")
        else:
            for module, deps in graph.items():
                if deps:
                    print(f"📦 {module}")
                    for dep in deps:
                        print(f"   └── ➡️ {dep}")

        if cycles:
            print("\n🚨 Circular Dependencies Detected!")
            print("-" * 30)
            for i, cycle in enumerate(cycles):
                print(f"Cycle {i + 1}: {' -> '.join(cycle)} -> {cycle[0]}")
        else:
            print("\n✅ No circular dependencies detected.")

    def _print_mermaid(self, graph: dict, cycles: list) -> None:
        """Print Mermaid diagram source."""
        print("\n```mermaid")
        print("graph TD")

        # Flatten all nodes for styling
        all_nodes = set(graph.keys())
        for deps in graph.values():
            all_nodes.update(deps)

        # Draw edges
        for module, deps in graph.items():
            for dep in deps:
                print(f"    {module} --> {dep}")

        # Highlight cycles
        if cycles:
            for cycle in cycles:
                for _j in range(len(cycle)):
                    # We don't have a good way to "color" edges in mermaid easily without classes
                    # but we can add annotations or just list them below
                    pass

        print("```\n")
