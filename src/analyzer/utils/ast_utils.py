"""AST utilities for Python code analysis.

This module provides helper functions for extracting information and calculating
metrics from Python Abstract Syntax Trees (AST).
"""

import ast
from typing import Any


def calculate_complexity(node: ast.AST) -> int:
    """Calculates Cyclomatic Complexity for a node with density-based penalty.

    Args:
        node: The AST node to analyze.

    Returns:
        The cyclomatic complexity score.
    """
    complexity = 1
    decision_lines = set()

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
                ast.IfExp,
            ),
        ):
            complexity += 1
            if hasattr(child, "lineno"):
                decision_lines.add(child.lineno)

    # Apply penalty for dense logic (many decision points in few lines)
    if decision_lines:
        line_range = max(decision_lines) - min(decision_lines) + 1
        density = len(decision_lines) / line_range
        # Threshold: 0.5 (1 decision every 2 lines)
        if density > 0.5:
            complexity = int(complexity * 1.5)

    return complexity


def extract_functions_from_ast(tree: ast.AST) -> list[dict[str, Any]]:
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


def extract_classes_from_ast(tree: ast.AST) -> list[str]:
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


def extract_imports_from_ast(tree: ast.AST) -> list[str]:
    """Extracts import information from AST.

    Args:
        tree: The AST tree root.

    Returns:
        A sorted list of imported module names.
    """
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(n.name for n in node.names)
        elif isinstance(node, ast.ImportFrom):
            module_name = node.module if node.module else ""
            if node.level > 0:
                # Add leading dots for relative imports
                module_name = ("." * node.level) + module_name
            if module_name:
                imports.append(module_name)
    return sorted(set(imports))


def _is_type_checking_guard(node: ast.If) -> bool:
    """Returns True if the If node is a TYPE_CHECKING guard.

    Matches both ``if TYPE_CHECKING:`` and
    ``if typing.TYPE_CHECKING:`` patterns.

    Args:
        node: An AST If node.

    Returns:
        True if the node is a TYPE_CHECKING guard, False otherwise.
    """
    test = node.test
    if isinstance(test, ast.Name) and test.id == "TYPE_CHECKING":
        return True
    if (
        isinstance(test, ast.Attribute)
        and test.attr == "TYPE_CHECKING"
        and isinstance(test.value, ast.Name)
        and test.value.id == "typing"
    ):
        return True
    return False


def _collect_type_checking_lines(statements: list[ast.stmt]) -> set[int]:
    """Collects line numbers of nodes nested inside TYPE_CHECKING guards.

    Args:
        statements: Top-level statements of the module.

    Returns:
        The set of line numbers that belong to TYPE_CHECKING blocks.
    """
    lines: set[int] = set()
    for node in statements:
        if isinstance(node, ast.If) and _is_type_checking_guard(node):
            for child in ast.walk(node):
                lineno = getattr(child, "lineno", None)
                if lineno is not None:
                    lines.add(lineno)
    return lines


def _imported_module_names(node: ast.AST) -> list[str]:
    """Extracts the module name(s) contributed by an import node.

    Args:
        node: A candidate AST node; only Import/ImportFrom contribute names.

    Returns:
        The imported module name(s), or an empty list for other node types.
    """
    if isinstance(node, ast.Import):
        return [alias.name for alias in node.names]
    if isinstance(node, ast.ImportFrom):
        module_name = node.module if node.module else ""
        if node.level > 0:
            module_name = ("." * node.level) + module_name
        return [module_name] if module_name else []
    return []


def extract_runtime_imports_from_ast(tree: ast.AST) -> list[str]:
    """Extracts only runtime imports, excluding TYPE_CHECKING-guarded ones.

    Imports inside ``if TYPE_CHECKING:`` blocks are used exclusively for
    static type analysis and do not exist at runtime. Including them in the
    dependency graph creates false edges that lead to phantom circular import
    cycles.

    Args:
        tree: The AST tree root (must be an ``ast.Module``).

    Returns:
        A sorted list of runtime-only imported module names.
    """
    # Only top-level statements can hold TYPE_CHECKING guards.
    top_level = tree.body if isinstance(tree, ast.Module) else []
    type_checking_lines = _collect_type_checking_lines(top_level)

    imports: list[str] = []
    for child_node in ast.walk(tree):
        lineno = getattr(child_node, "lineno", None)
        if lineno is not None and lineno in type_checking_lines:
            continue
        imports.extend(_imported_module_names(child_node))

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
