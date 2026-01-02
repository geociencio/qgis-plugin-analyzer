"""AST utilities for Python code analysis.

This module provides helper functions for extracting information and calculating
metrics from Python Abstract Syntax Trees (AST).
"""

import ast
from typing import Any, Dict, List


def calculate_complexity(node: ast.AST) -> int:
    """Calculates Cyclomatic Complexity for a node.

    Args:
        node: The AST node to analyze.

    Returns:
        The cyclomatic complexity score.
    """
    complexity = 1
    for child in ast.walk(node):
        if isinstance(
            child,
            (
                ast.If,
                ast.For,
                ast.While,
                ast.And,
                ast.Or,
                ast.ExceptHandler,
                ast.With,
                ast.AsyncWith,
            ),
        ):
            complexity += 1
    return complexity


def extract_functions_from_ast(tree: ast.AST) -> List[Dict[str, Any]]:
    """Extracts function information from AST.

    Args:
        tree: The AST tree root.

    Returns:
        A list of dictionaries containing function metadata (name, args, line, complexity, etc.).
    """
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_complexity = calculate_complexity(node)
            functions.append(
                {
                    "name": node.name,
                    "args": [arg.arg for arg in node.args.args],
                    "line": node.lineno,
                    "end_line": getattr(node, "end_lineno", node.lineno),
                    "complexity": func_complexity,
                    "docstring": ast.get_docstring(node) is not None,
                }
            )
    return functions


def extract_classes_from_ast(tree: ast.AST) -> List[str]:
    """Extracts class information from AST.

    Args:
        tree: The AST tree root.

    Returns:
        A list of class signatures (e.g., "ClassName(BaseClass)").
    """
    classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            bases = [ast.unparse(b) for b in node.bases]
            classes.append(f"{node.name}({', '.join(bases)})" if bases else node.name)
    return classes


def extract_imports_from_ast(tree: ast.AST) -> List[str]:
    """Extracts import information from AST.

    Args:
        tree: The AST tree root.

    Returns:
        A sorted list of imported module names.
    """
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(n.name for n in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return sorted(set(imports))


def calculate_module_complexity(tree: ast.AST) -> int:
    """Calculates module-level complexity based on decision points.

    Args:
        tree: The AST tree root.

    Returns:
        The module-level complexity score.
    """
    complexity = 1
    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.For, ast.While, ast.And, ast.Or, ast.ExceptHandler)):
            complexity += 1
    return complexity


def check_main_guard(tree: ast.AST) -> bool:
    """Checks if module has __name__ == '__main__' guard.

    Args:
        tree: The AST tree root.

    Returns:
        True if the main guard is found, False otherwise.
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            if isinstance(node.test, ast.Compare) and isinstance(node.test.left, ast.Name):
                if node.test.left.id == "__name__":
                    for cmp in node.test.comparators:
                        if isinstance(cmp, ast.Constant) and cmp.value == "__main__":
                            return True
    return False
