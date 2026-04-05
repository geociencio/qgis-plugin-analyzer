"""Core infrastructure for security scanning in QGIS Plugin Analyzer.

Inspired by Bandit's architecture, this module provides a decorator-based
registry for security checks and a context helper for AST analysis.
"""

import ast
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Type


@dataclass
class SecurityFinding:
    """Represents a detected security vulnerability."""

    id: str
    severity: str  # LOW, MEDIUM, HIGH
    confidence: str  # LOW, MEDIUM, HIGH
    message: str
    line: int
    code_snippet: Optional[str] = None
    cwe: Optional[int] = None


class SecurityContext:
    """Helper class providing easy access to AST node information for security checks."""

    def __init__(self, node: ast.AST, filename: str):
        self.node = node
        self.filename = filename

    @property
    def call_function_name(self) -> Optional[str]:
        """Returns the name of the function being called if the node is a Call."""
        if isinstance(self.node, ast.Call):
            if isinstance(self.node.func, ast.Name):
                return self.node.func.id
            if isinstance(self.node.func, ast.Attribute):
                return self.node.func.attr
        return None

    @property
    def call_args_count(self) -> int:
        """Returns the number of positional arguments in a Call node."""
        if isinstance(self.node, ast.Call):
            return len(self.node.args)
        return 0

    def get_call_keyword_value(self, keyword_name: str) -> Any:
        """Returns the value of a specific keyword argument in a Call node."""
        if isinstance(self.node, ast.Call):
            for kw in self.node.keywords:
                if kw.arg == keyword_name:
                    if isinstance(kw.value, ast.Constant):
                        return kw.value.value
        return None


class SecurityRegistry:
    """Registry for security checks managed by decorators."""

    _checks: Dict[
        Type[ast.AST], List[Callable[[SecurityContext], Optional[SecurityFinding]]]
    ] = {}

    @classmethod
    def register(cls, node_type: Type[ast.AST]) -> Callable:
        """Decorator to register a function as a security check for a specific node type."""

        def decorator(func: Callable[[SecurityContext], Optional[SecurityFinding]]):
            if node_type not in cls._checks:
                cls._checks[node_type] = []
            cls._checks[node_type].append(func)
            return func

        return decorator

    @classmethod
    def get_checks_for_node(
        cls, node_type: Type[ast.AST]
    ) -> List[Callable[[SecurityContext], Optional[SecurityFinding]]]:
        """Returns all registered checks for a given AST node type."""
        return cls._checks.get(node_type, [])


# Decorator alias
security_check = SecurityRegistry.register
