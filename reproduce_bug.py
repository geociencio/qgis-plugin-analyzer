import ast
import sys
import os

# Añadir src al path para importar el visitor
sys.path.insert(0, os.path.abspath("src"))

from analyzer.visitors.metrics_visitor import MetricsVisitor

def reproduce_issue():
    code = """
def my_complex_function(
    self,
    param1: str,
    param2: int
) -> bool:
    return True
"""
    tree = ast.parse(code)
    visitor = MetricsVisitor("test.py")
    visitor.visit(tree)
    
    stats = visitor.type_hint_stats
    print(f"Stats: {stats}")
    
    if stats["has_return_hint"] == 1:
        print("SUCCESS: Return hint detected correctly.")
    else:
        print("FAILURE: Return hint NOT detected.")

if __name__ == "__main__":
    reproduce_issue()
