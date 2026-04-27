"""Security rules for QGIS Plugin Analyzer.

Each check is registered for a specific AST node type and performs a focused
security audit.
"""

import ast
from typing import Optional, cast

from .security_checker import SecurityContext, SecurityFinding, security_check


@security_check(node_type=ast.Call)
def check_exec_eval(context: SecurityContext) -> Optional[SecurityFinding]:
    """B102/B307: Detect use of exec or eval."""
    func_name = context.call_function_name
    if func_name in ("exec", "eval"):
        node = cast(ast.Call, context.node)
        return SecurityFinding(
            id="B102" if func_name == "exec" else "B307",
            severity="HIGH",
            confidence="HIGH",
            message=f"Use of '{func_name}' detected. This can lead to arbitrary code execution.",
            line=node.lineno,
            code_snippet=ast.unparse(node),
            cwe=95 if func_name == "eval" else 78,
        )
    return None


@security_check(node_type=ast.Call)
def check_insecure_deserialization(
    context: SecurityContext,
) -> Optional[SecurityFinding]:
    """B301: Detect unsafe pickle.load()."""
    if context.call_function_name == "load":
        # Check if it's from 'pickle'
        node = cast(ast.Call, context.node)
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            if node.func.value.id == "pickle":
                return SecurityFinding(
                    id="B301",
                    severity="HIGH",
                    confidence="HIGH",
                    message="Use of 'pickle.load()' detected. Deserializing untrusted data can lead to remote code execution.",
                    line=node.lineno,
                    code_snippet=ast.unparse(node),
                    cwe=502,
                )
    return None


@security_check(node_type=ast.Call)
def check_subprocess_shell(context: SecurityContext) -> Optional[SecurityFinding]:
    """B602: Subprocess call with shell=True."""
    func_name = context.call_function_name
    subprocess_funcs = {"run", "call", "Popen", "check_call", "check_output"}

    if func_name in subprocess_funcs:
        shell_val = context.get_call_keyword_value("shell")
        if shell_val is True:
            node = cast(ast.Call, context.node)
            return SecurityFinding(
                id="B602",
                severity="HIGH",
                confidence="HIGH",
                message=f"Subprocess call '{func_name}' with 'shell=True' detected. This is a primary source of shell injection.",
                line=node.lineno,
                code_snippet=ast.unparse(node),
                cwe=78,
            )
    return None


@security_check(node_type=ast.Call)
def check_sql_injection(context: SecurityContext) -> Optional[SecurityFinding]:
    """B608: Basic detection of SQL injection via string formatting."""
    if context.call_function_name == "execute":
        if context.call_args_count > 0:
            node = cast(ast.Call, context.node)
            sql_arg = node.args[0]
            # Check for f-strings or .format() or % formatting in the first argument
            is_unsafe = False
            if isinstance(sql_arg, ast.JoinedStr):
                is_unsafe = True
            elif isinstance(sql_arg, ast.BinOp) and isinstance(sql_arg.op, ast.Mod):
                is_unsafe = True
            elif isinstance(sql_arg, ast.Call) and isinstance(sql_arg.func, ast.Attribute):
                if sql_arg.func.attr == "format":
                    is_unsafe = True

            if is_unsafe:
                return SecurityFinding(
                    id="B608",
                    severity="HIGH",
                    confidence="MEDIUM",
                    message="Possible SQL injection detected. Use parameterized queries instead of string formatting.",
                    line=node.lineno,
                    code_snippet=ast.unparse(node),
                    cwe=89,
                )
    return None


@security_check(node_type=ast.Assign)
def check_hardcoded_secrets(context: SecurityContext) -> Optional[SecurityFinding]:
    """Detect assignments of sensitive names to constants."""
    node = context.node
    if not isinstance(node, ast.Assign):
        return None

    sensitive_names = {"password", "token", "api_key", "secret", "access_key"}

    for target in node.targets:
        if isinstance(target, ast.Name) and any(s in target.id.lower() for s in sensitive_names):
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                # Only flag if it's not empty and looks like a secret
                val = node.value.value
                if len(val) > 8:
                    cast_node = cast(ast.Assign, node)
                    return SecurityFinding(
                        id="HARDCODED_SECRET",
                        severity="MEDIUM",
                        confidence="MEDIUM",
                        message=f"Possible hardcoded secret in assignment to '{target.id}'.",
                        line=cast_node.lineno,
                        code_snippet=ast.unparse(cast_node),
                    )
    return None
