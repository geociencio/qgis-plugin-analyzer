import ast
import unittest
from analyzer.visitors.metrics_visitor import MetricsVisitor


class TestMetricsVisitorExtended(unittest.TestCase):
    def test_async_function_metrics(self):
        code = """
async def complex_async_func(a: int, b: int) -> bool:
    \"\"\"
    Google Style.
    
    Args:
        a: param a
        b: param b
        
    Returns:
        bool: success
    \"\"\"
    if a:
        if b:
            if c:
                if d:
                    if e:
                        if f:
                            if g:
                                if h:
                                    if i:
                                        if j:
                                            if k:
                                                if l:
                                                    if m:
                                                        if n:
                                                            if o:
                                                                if p:
                                                                    return True
    return False
"""
        tree = ast.parse(code)
        visitor = MetricsVisitor("test.py")
        visitor.visit(tree)
        
        # Should have Google style detected
        self.assertIn("Google", visitor.docstring_styles)
        
        # Should have high complexity issue
        issues = [i for i in visitor.issues if i["type"] == "HIGH_COMPLEXITY"]
        self.assertGreater(len(issues), 0)
        
        # Type hints
        self.assertEqual(visitor.type_hint_stats["annotated_parameters"], 2)
        self.assertEqual(visitor.type_hint_stats["has_return_hint"], 1)

    def test_numpy_docstring_style(self):
        code = """
def numpy_func(x):
    \"\"\"
    NumPy Style.
    
    Parameters
    ----------
    x : int
        The value.
    \"\"\"
    return x
"""
        tree = ast.parse(code)
        visitor = MetricsVisitor("test.py")
        visitor.visit(tree)
        self.assertIn("NumPy", visitor.docstring_styles)

    def test_class_docstring(self):
        code = "class MyClass:\n    \"\"\"Class docstring.\"\"\"\n    pass"
        tree = ast.parse(code)
        visitor = MetricsVisitor("test.py")
        visitor.visit(tree)
        self.assertEqual(visitor.docstring_stats["has_docstring"], 1) # Class only (no module doc)


if __name__ == "__main__":
    unittest.main()
