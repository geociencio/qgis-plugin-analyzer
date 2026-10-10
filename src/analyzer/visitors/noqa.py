"""Reusable ``# noqa`` opt-out detection for AST visitors.

Parses source lines with :mod:`tokenize` so that only real comments are
considered, and maps each source line to the rule codes it suppresses.
"""

import io
import tokenize


def collect_noqa_directives(lines: list[str]) -> dict[int, set[str] | None]:
    """Maps source line numbers to their ``# noqa`` suppression codes.

    A value of ``None`` means the line suppresses **all** rules (bare
    ``# noqa``). Otherwise the value is the set of explicit rule codes taken
    from ``# noqa: CODE1, CODE2``.

    Args:
        lines: Source lines of the file being analyzed.

    Returns:
        A mapping of 1-indexed line number to suppression codes (or ``None``).
    """
    directives: dict[int, set[str] | None] = {}
    source = "\n".join(lines)

    try:
        tokens = tokenize.generate_tokens(io.StringIO(source).readline)
        for token in tokens:
            if token.type != tokenize.COMMENT:
                continue

            body = token.string.lstrip("#").strip()
            if not body.startswith("noqa"):
                continue

            remainder = body[len("noqa") :].strip()
            codes: set[str] | None
            if remainder.startswith(":"):
                raw = remainder[1:].strip()
                codes = (
                    {code.strip() for code in raw.replace(",", " ").split() if code.strip()}
                    if raw
                    else None
                )
            else:
                codes = None

            line = token.start[0]
            existing = directives.get(line)
            if line not in directives:
                directives[line] = codes
            elif existing is None or codes is None:
                directives[line] = None
            else:
                directives[line] = existing | codes
    except tokenize.TokenError:
        return {}

    return directives
