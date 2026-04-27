import ast
import unittest

from analyzer.utils.ast_utils import (
    calculate_complexity,
    check_main_guard,
    extract_classes_from_ast,
    extract_imports_from_ast,
    extract_runtime_imports_from_ast,
)


class TestAstUtilsExtended(unittest.TestCase):
    def test_calculate_complexity_special_nodes(self):
        # Test With, AsyncWith, And, Or, IfExp
        code = """
async def func():
    with open('a'): pass
    async with lock: pass
    res = 1 if a else 2
    if a and b or c:
        pass
"""
        tree = ast.parse(code)
        func_node = [n for n in ast.walk(tree) if isinstance(n, ast.AsyncFunctionDef)][0]
        # Base(1) + with(1) + asyncwith(1) + ifexp(1) + and(1) + or(1) + if(1) = 7
        # Density penalty might apply if lines are close.
        complexity = calculate_complexity(func_node)
        self.assertGreaterEqual(complexity, 7)

    def test_extract_runtime_imports(self):
        code = """
import os
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import pandas
    from . import local_mod
import sys
"""
        tree = ast.parse(code)
        imports = extract_runtime_imports_from_ast(tree)

        self.assertIn("os", imports)
        self.assertIn("sys", imports)
        self.assertIn("typing", imports)
        self.assertNotIn("pandas", imports)
        self.assertNotIn(".local_mod", imports)

    def test_extract_runtime_imports_relative(self):
        code = "from .. import parent_mod"
        tree = ast.parse(code)
        imports = extract_runtime_imports_from_ast(tree)
        self.assertIn("..", imports)

    def test_check_main_guard(self):
        code_with = "if __name__ == '__main__': main()"
        self.assertTrue(check_main_guard(ast.parse(code_with)))

        code_without = "print('hello')"
        self.assertFalse(check_main_guard(ast.parse(code_without)))

    def test_extract_classes(self):
        code = "class MyClass(Base, Mixin): pass"
        classes = extract_classes_from_ast(ast.parse(code))
        self.assertIn("MyClass(Base, Mixin)", classes)

    def test_extract_imports_levels(self):
        code = "from .sub import name"
        imports = extract_imports_from_ast(ast.parse(code))
        self.assertIn(".sub", imports)


if __name__ == "__main__":
    unittest.main()
