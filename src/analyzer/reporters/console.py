"""Low-level console formatting primitives for terminal reporters.

This leaf module holds the ANSI-formatting helpers shared by the summary and
security reporters. It has no project-specific logic so it can be imported from
any reporter without creating cycles.
"""

from typing import Any

# Score thresholds for the colored output (below fair is red).
_SCORE_GOOD = 80
_SCORE_FAIR = 50


def print_header(title: str) -> None:
    """Print a formatted section header.

    Args:
        title: The header title to display.
    """
    print(f"\n\033[1m{title}\033[0m")


def print_separator(char: str = "=", length: int = 45) -> None:
    """Print a separator line.

    Args:
        char: The character to use for the separator.
        length: The length of the separator line.
    """
    print(char * length)


def print_success(message: str) -> None:
    """Print a success message in green.

    Args:
        message: The success message to display.
    """
    print(f"\n\033[92m{message}\033[0m")


def print_colored_score(label: str, score: Any) -> None:
    """Prints a score with ANSI colors based on its value.

    Args:
        label: The label for the score.
        score: The numeric score value (or "N/A").
    """
    if score == "N/A":
        print(f"{label}: \033[90mN/A\033[0m")
        return

    try:
        val = float(score)
        if val >= _SCORE_GOOD:
            color = "\033[92m"  # Green
        elif val >= _SCORE_FAIR:
            color = "\033[93m"  # Yellow
        else:
            color = "\033[91m"  # Red
        print(f"{label}: {color}{val:.1f}/100\033[0m")
    except (ValueError, TypeError):
        print(f"{label}: {score}")
