"""Tests for the design-pattern / anti-pattern visitor and Halstead metrics."""

import ast
import unittest

from analyzer.utils.halstead import calculate_halstead_metrics
from analyzer.visitors.patterns_visitor import PatternsVisitor


def _analyze(code: str) -> PatternsVisitor:
    visitor = PatternsVisitor("m.py")
    visitor.visit(ast.parse(code))
    return visitor


class TestDesignPatterns(unittest.TestCase):
    def test_singleton(self):
        code = (
            "class Config:\n"
            "    _instance = None\n"
            "    def __new__(cls):\n"
            "        if cls._instance is None:\n"
            "            cls._instance = super().__new__(cls)\n"
            "        return cls._instance\n"
        )
        self.assertEqual(_analyze(code).patterns.get("singleton"), ["Config"])

    def test_factory_by_name(self):
        self.assertEqual(
            _analyze("class ShapeFactory: pass\n").patterns.get("factory"), ["ShapeFactory"]
        )

    def test_factory_by_method(self):
        code = "class Builder:\n    def create(self): return 1\n"
        self.assertEqual(_analyze(code).patterns.get("factory"), ["Builder"])

    def test_observer(self):
        code = (
            "class Subject:\n"
            "    def subscribe(self, o): pass\n"
            "    def unsubscribe(self, o): pass\n"
            "    def notify(self): pass\n"
        )
        self.assertEqual(_analyze(code).patterns.get("observer"), ["Subject"])

    def test_strategy(self):
        code = "class Context:\n    def set_strategy(self, s): pass\n"
        self.assertEqual(_analyze(code).patterns.get("strategy"), ["Context"])

    def test_decorator(self):
        code = (
            "def logged(func):\n"
            "    def wrapper(*a, **k):\n"
            "        return func(*a, **k)\n"
            "    return wrapper\n"
        )
        self.assertEqual(_analyze(code).patterns.get("decorator"), ["logged"])


class TestAntiPatterns(unittest.TestCase):
    def _types(self, code: str) -> set[str]:
        return {issue["type"] for issue in _analyze(code).issues}

    def test_magic_number(self):
        self.assertIn("MAGIC_NUMBER", self._types("def f(x):\n    return x == 42\n"))

    def test_god_object_by_methods(self):
        methods = "".join(f"    def m{i}(self): pass\n" for i in range(21))
        self.assertIn("GOD_OBJECT", self._types(f"class Blob:\n{methods}"))

    def test_spaghetti_code(self):
        code = (
            "def f(x):\n"
            "    if x:\n"
            "        if x:\n"
            "            if x:\n"
            "                if x:\n"
            "                    if x:\n"
            "                        return 1\n"
            "    return 0\n"
        )
        self.assertIn("SPAGHETTI_CODE", self._types(code))

    def test_dead_code(self):
        self.assertIn("DEAD_CODE", self._types("if False:\n    x = 1\n"))


class TestHalstead(unittest.TestCase):
    def test_metrics_are_computed(self):
        metrics = calculate_halstead_metrics(ast.parse("a = b + c\n"))

        self.assertGreater(metrics["vocabulary"], 0)
        self.assertGreater(metrics["length"], 0)
        self.assertGreaterEqual(metrics["volume"], 0)

    def test_empty_expression(self):
        metrics = calculate_halstead_metrics(ast.parse(""))

        self.assertEqual(metrics["volume"], 0)


if __name__ == "__main__":
    unittest.main()
