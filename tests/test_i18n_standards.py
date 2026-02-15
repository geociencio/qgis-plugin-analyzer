import ast

from analyzer.visitors.composite_visitor import CompositeVisitor


def test_i18n_excludes_docstrings():
    """Verify that docstrings are not flagged as missing translations."""
    code = """
def my_function():
    \"\"\"This is a docstring that shouldn't be translated.\"\"\"
    print("This is a user message that should be translated.")
"""
    tree = ast.parse(code)
    visitor = CompositeVisitor("test_file.py")
    visitor.visit(tree)

    # MISSING_DOCSTRING (from MetricsVisitor) and HIGH_COMPLEXITY etc might be present
    # but we care about MISSING_I18N
    i18n_issues = [i for i in visitor.issues if i["type"] == "MISSING_I18N"]

    # Should only find the user message on line 4 (in the snippet above, it's line 5 in the parsed tree due to leading newline)
    # Let's check messages
    messages = [i["message"] for i in i18n_issues]
    assert any("user message" in m for m in messages)
    assert not any("docstring" in m for m in messages)
    assert len(i18n_issues) == 1


def test_i18n_includes_user_facing_strings():
    """Verify that actual user-facing strings are still flagged."""
    code = """
class MyWidget:
    def __init__(self):
        self.label = "Name:"
"""
    tree = ast.parse(code)
    visitor = CompositeVisitor("test_file.py")
    visitor.visit(tree)

    i18n_issues = [i for i in visitor.issues if i["type"] == "MISSING_I18N"]
    assert len(i18n_issues) == 1
    assert "Name:" in i18n_issues[0]["message"]
