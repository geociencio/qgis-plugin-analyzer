"""Halstead complexity metrics for Python ASTs."""

import ast
from collections import Counter

# Operator node types counted as Halstead operators.
_OPERATORS: tuple[type[ast.AST], ...] = (
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Mod,
    ast.Pow,
    ast.LShift,
    ast.RShift,
    ast.BitOr,
    ast.BitXor,
    ast.BitAnd,
    ast.FloorDiv,
    ast.And,
    ast.Or,
    ast.Not,
    ast.Invert,
    ast.UAdd,
    ast.USub,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
    ast.Is,
    ast.IsNot,
    ast.In,
    ast.NotIn,
    ast.If,
    ast.For,
    ast.While,
    ast.Try,
    ast.With,
    ast.FunctionDef,
    ast.ClassDef,
)


class _HalsteadCounter(ast.NodeVisitor):
    """Counts Halstead operators and operands in an AST."""

    def __init__(self) -> None:
        """Initializes the operator and operand counters."""
        self.operators: Counter[str] = Counter()
        self.operands: Counter[str] = Counter()

    def visit(self, node: ast.AST) -> None:
        """Records operator/operand occurrences.

        Args:
            node: The AST node being visited.
        """
        if isinstance(node, _OPERATORS):
            self.operators[type(node).__name__] += 1
        elif isinstance(node, ast.Name):
            self.operands[node.id] += 1
        elif isinstance(node, ast.Constant):
            self.operands[str(node.value)] += 1
        super().visit(node)


def calculate_halstead_metrics(tree: ast.AST) -> dict[str, float]:
    """Calculates Halstead complexity metrics for an AST.

    Args:
        tree: The AST tree root.

    Returns:
        A dictionary with ``vocabulary``, ``length``, ``volume``,
        ``difficulty`` and ``effort``.
    """
    counter = _HalsteadCounter()
    counter.visit(tree)

    n1 = len(counter.operators)
    n2 = len(counter.operands)
    big_n1 = sum(counter.operators.values())
    big_n2 = sum(counter.operands.values())

    vocabulary = n1 + n2
    length = big_n1 + big_n2

    volume = 0.0
    difficulty = 0.0
    effort = 0.0
    if n1 > 0 and n2 > 0:
        volume = float(length * (vocabulary.bit_length() - 1))
        difficulty = (n1 / 2) * (big_n2 / n2)
        effort = difficulty * volume

    return {
        "vocabulary": vocabulary,
        "length": length,
        "volume": round(volume, 2),
        "difficulty": round(difficulty, 2),
        "effort": round(effort, 2),
    }
