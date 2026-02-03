"""AST visitor for security vulnerability detection."""

import ast
from typing import Any, Dict, List

from ..security_checker import SecurityContext, SecurityRegistry


class SecurityVisitor(ast.NodeVisitor):
    """AST visitor focused on security vulnerabilities (Bandit-inspired).

    Attributes:
        rel_path: Relative path to the file being analyzed.
        findings: List of security findings detected.
    """

    def __init__(self, rel_path: str):
        """Initializes the security visitor.

        Args:
            rel_path: Relative path to the file being analyzed.
        """
        self.rel_path = rel_path
        self.findings: List[Dict[str, Any]] = []

    def visit(self, node: ast.AST):
        """Dispatches security checks for the current node.

        Args:
            node: The AST node to analyze.
        """
        checks = SecurityRegistry.get_checks_for_node(type(node))
        context = SecurityContext(node, self.rel_path)

        for check_func in checks:
            finding = check_func(context)
            if finding:
                self.findings.append(
                    {
                        "file": self.rel_path,
                        "line": finding.line,
                        "type": finding.id,
                        "severity": finding.severity.lower(),
                        "message": finding.message,
                        "code": finding.code_snippet,
                        "confidence": finding.confidence.lower()
                        if hasattr(finding, "confidence")
                        else "medium",
                    }
                )

        super().generic_visit(node)
