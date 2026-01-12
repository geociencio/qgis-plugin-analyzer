
import ast
from collections import Counter
from typing import Any, List, Dict

def extract_functions(tree: ast.AST) -> List[str]:
    """Extrae nombres de funciones."""
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_info = node.name
            # Extraer argumentos
            args_count = len(node.args.args)
            if args_count > 0:
                func_info = f"{func_info}({args_count} args)"
            functions.append(func_info)
    return functions

def extract_classes(tree: ast.AST) -> List[str]:
    """Extrae nombres de clases con herencia."""
    classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Incluir información de herencia
            bases = [get_base_name(base) for base in node.bases]
            inheritance = f"({', '.join(bases)})" if bases else ""
            classes.append(f"{node.name}{inheritance}")
    return classes

def get_base_name(node: ast.AST) -> str:
    """Obtiene nombre de clase base."""
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        return ast.unparse(node)
    else:
        return "Unknown"

def check_docstrings(tree: ast.AST) -> Dict[str, Any]:
    """Verifica docstrings por elemento."""
    docstrings = {"module": False, "classes": {}, "functions": {}}

    # Docstring del módulo
    if isinstance(tree, ast.Module):
        docstrings["module"] = ast.get_docstring(tree) is not None

    # Docstrings de clases y funciones
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            docstrings["classes"][node.name] = ast.get_docstring(node) is not None
        elif isinstance(node, ast.FunctionDef):
            docstrings["functions"][node.name] = ast.get_docstring(node) is not None

    return docstrings

def has_main_guard(tree: ast.AST) -> bool:
    """Verifica si el módulo tiene if __name__ == '__main__'."""
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            try:
                # Verificar condición __name__ == '__main__'
                if (
                    isinstance(node.test, ast.Compare)
                    and isinstance(node.test.left, ast.Name)
                    and node.test.left.id == "__name__"
                ):
                    for comparator in node.test.comparators:
                        if (
                            isinstance(comparator, ast.Constant)
                            and comparator.value == "__main__"
                        ):
                            return True
            except:
                continue
    return False

def calculate_type_hint_coverage(tree: ast.AST) -> Dict[str, Any]:
    """Calcula el porcentaje de funciones y clases con type hints."""
    total_items = 0
    typed_items = 0

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            total_items += 1
            # Comprobar retorno
            has_return_type = node.returns is not None

            # Comprobar argumentos (excluyendo self/cls)
            args = [arg for arg in node.args.args if arg.arg not in ("self", "cls")]
            total_args = len(args)
            typed_args = sum(1 for arg in args if arg.annotation is not None)

            if has_return_type and (total_args in (0, typed_args)):
                typed_items += 1

    return {
        "total_functions": total_items,
        "typed_functions": typed_items,
        "coverage": (typed_items / total_items * 100) if total_items > 0 else 100.0,
    }

def calculate_halstead_metrics(tree: ast.AST) -> Dict[str, Any]:
    """Calcula métricas de Halstead básicas."""
    operators = Counter()
    operands = Counter()

    for node in ast.walk(tree):
        node_type = type(node).__name__
        if isinstance(
            node,
            ast.Add
            | ast.Sub
            | ast.Mult
            | ast.Div
            | ast.Mod
            | ast.Pow
            | ast.LShift
            | ast.RShift
            | ast.BitOr
            | ast.BitXor
            | ast.BitAnd
            | ast.FloorDiv
            | ast.And
            | ast.Or
            | ast.Not
            | ast.Invert
            | ast.UAdd
            | ast.USub
            | ast.Eq
            | ast.NotEq
            | ast.Lt
            | ast.LtE
            | ast.Gt
            | ast.GtE
            | ast.Is
            | ast.IsNot
            | ast.In
            | ast.NotIn
            | ast.If
            | ast.For
            | ast.While
            | ast.Try
            | ast.With
            | ast.FunctionDef
            | ast.ClassDef,
        ):
            operators[node_type] += 1
        elif isinstance(node, ast.Name):
            operands[node.id] += 1
        elif isinstance(node, ast.Constant):
            operands[str(node.value)] += 1

    n1 = len(operators)  # unique operators
    n2 = len(operands)  # unique operands
    N1 = sum(operators.values())  # total operators
    N2 = sum(operands.values())  # total operands

    h_vocabulary = n1 + n2
    h_length = N1 + N2

    if n1 > 0 and n2 > 0:
        h_volume = h_length * (h_vocabulary.bit_length() - 1)
        h_difficulty = (n1 / 2) * (N2 / n2)
        h_effort = h_difficulty * h_volume
    else:
        h_volume = h_difficulty = h_effort = 0

    return {
        "vocabulary": h_vocabulary,
        "length": h_length,
        "volume": round(h_volume, 2),
        "difficulty": round(h_difficulty, 2),
        "effort": round(h_effort, 2),
    }

def extract_imports(tree: ast.AST) -> List[str]:
    """Extrae imports de forma optimizada."""
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                if module:
                    imports.append(f"{module}.{alias.name}")
                else:
                    imports.append(alias.name)

    # De-duplicar manteniendo orden
    seen = set()
    unique_imports = []
    for imp in imports:
        if imp not in seen:
            seen.add(imp)
            unique_imports.append(imp)

    return unique_imports

def calculate_complexity(tree: ast.AST) -> int:
    """Calcula complejidad ciclomática optimizada."""
    complexity = 0
    decision_lines = set()

    for node in ast.walk(tree):
        # Decisiones básicas
        if isinstance(
            node,
            ast.If
            | ast.While
            | ast.For
            | ast.Try
            | ast.ExceptHandler
            | ast.AsyncFor
            | ast.AsyncWith,
        ):
            complexity += 1
            if hasattr(node, "lineno"):
                decision_lines.add(node.lineno)

        # Operadores booleanos
        elif isinstance(node, ast.BoolOp):
            complexity += len(node.values) - 1

        # Comprehensions
        elif isinstance(node, ast.ListComp | ast.SetComp | ast.DictComp | ast.GeneratorExp):
            complexity += len(node.generators)

    # Penalizar módulos con muchas decisiones en pocas líneas
    if decision_lines:
        density_penalty = len(decision_lines) * 0.3
        complexity += int(density_penalty)

    return complexity
