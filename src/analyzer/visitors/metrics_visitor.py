"""AST visitor for docstring and metrics collection."""

import ast
import re
from typing import Any, Dict, List, Optional

from ..utils.ast_utils import calculate_complexity
from .base import BaseVisitor


class MetricsVisitor(BaseVisitor):
    """Visitor focused on collecting research-based metrics.

    Collects:
    - Docstring coverage and styles
    - Type hint coverage
    - Complexity metrics
    """

    def __init__(
        self,
        rel_path: str,
        rules_config: Optional[Dict[str, Any]] = None,
        scope: str = "all",
    ) -> None:
        """Initializes the metrics visitor.

        Args:
            rel_path: Relative path to the file being analyzed.
            rules_config: Optional configuration for audit rules and severities.
            scope: Analysis scope.
        """
        super().__init__(rel_path, rules_config, scope)
        self.docstring_styles: List[str] = []
        self.type_hint_stats = {
            "total_parameters": 0,
            "annotated_parameters": 0,
            "has_return_hint": 0,
            "total_functions": 0,
        }
        self.docstring_stats = {"total_public_items": 0, "has_docstring": 0}

    def visit_Module(self, node: ast.Module) -> None:
        """Analyzes a module-level AST node.

        Args:
            node: The module AST node.
        """
        doc = ast.get_docstring(node)
        self.docstring_stats["total_public_items"] += 1
        if doc:
            self.docstring_stats["has_docstring"] += 1
            self._check_docstring_style(doc)
        else:
            self._report_issue(
                "MISSING_DOCSTRING",
                1,
                "Module is missing a docstring (PEP 257).",
                f"Module: {self.rel_path}",
            )
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Analyzes function definitions.

        Args:
            node: The function definition AST node.
        """
        # HIGH_COMPLEXITY
        complexity = calculate_complexity(node)
        if complexity > 15:
            self._report_issue(
                "HIGH_COMPLEXITY",
                node.lineno,
                f"Function '{node.name}' is too complex (CC={complexity} > 15). Consider extracting methods.",
                f"def {node.name}...",
            )

        self._check_docstring_and_metrics(node)
        self._check_type_hints(node)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Analyzes class definitions.

        Args:
            node: The class definition AST node.
        """
        # Missing Docstring
        if not node.name.startswith("_"):
            doc = ast.get_docstring(node)
            self.docstring_stats["total_public_items"] += 1
            if doc:
                self.docstring_stats["has_docstring"] += 1
                self._check_docstring_style(doc)
            else:
                self._report_issue(
                    "MISSING_DOCSTRING",
                    node.lineno,
                    f"Public class '{node.name}' is missing a docstring.",
                    f"class {node.name}...",
                )
        self.generic_visit(node)

        pass

    def _check_docstring_style(self, doc: Optional[str]) -> None:
        """Identifies Google or NumPy docstring styles within a string.

        Args:
            doc: The docstring to analyze.
        """
        if not doc:
            return
        # Google: Args: or Returns: or Raises: as headers
        if re.search(r"\n\s*(Args|Returns|Raises|Yields):\s*\n", doc):
            self.docstring_styles.append("Google")
        # NumPy: Underlined headers
        elif re.search(r"\n(Parameters|Returns|Raises|Yields)\n\s*-{3,}", doc):
            self.docstring_styles.append("NumPy")

    def _check_docstring_and_metrics(self, node: ast.FunctionDef) -> None:
        """Checks docstrings and collects metrics.

        Args:
            node: The function definition AST node.
        """
        if not node.name.startswith("_") and node.name != "__init__":
            doc = ast.get_docstring(node)
            self.docstring_stats["total_public_items"] += 1
            if doc:
                self.docstring_stats["has_docstring"] += 1
                self._check_docstring_style(doc)
            else:
                self._report_issue(
                    "MISSING_DOCSTRING",
                    node.lineno,
                    f"Public function '{node.name}' is missing a docstring.",
                    f"def {node.name}...",
                )

    def _check_type_hints(self, node: ast.FunctionDef) -> None:
        """Checks for type hints.

        Args:
            node: The function definition AST node.
        """
        if node.name == "__init__":
            return

        self.type_hint_stats["total_functions"] += 1
        params = [a for a in node.args.args if a.arg != "self" and a.arg != "cls"]
        self.type_hint_stats["total_parameters"] += len(params)
        annotated = [a for a in params if a.annotation]
        self.type_hint_stats["annotated_parameters"] += len(annotated)
        if node.returns:
            self.type_hint_stats["has_return_hint"] += 1

        if params and not annotated and not node.returns:
            self._report_issue(
                "MISSING_TYPE_HINTS",
                node.lineno,
                f"Function '{node.name}' has no type annotations.",
                f"def {node.name}...",
            )
