"""Secret detection logic for QGIS Plugin Analyzer.

Handles regex-based matching of API keys and high-entropy string detection.
"""

import math
import re
from dataclasses import dataclass

# Shannon-entropy threshold above which a string is treated as a possible secret.
_ENTROPY_THRESHOLD = 4.5


@dataclass
class SecretFinding:
    """Represents a detected secret or sensitive string."""

    type: str
    message: str
    line: int
    confidence: str


class SecretScanner:
    """Scanner for hardcoded secrets and high-entropy strings."""

    # Common patterns for API keys and tokens
    PATTERNS = {
        "AWS_KEY": r"(?i)AKIA[0-9A-Z]{16}",
        "GOOGLE_API_KEY": r"(?i)AIza[0-9A-Za-z\\-_]{35}",
        "TWILIO_KEY": r"(?i)SK[a-z0-9]{32}",
        "GENERIC_SECRET": r"(?i)(password|secret|passwd|api_key|token|access_key)[\"']?\s*[:=]\s*[\"']?([A-Za-z0-9/+=]{16,})[\"']?",
    }

    def __init__(self, include_entropy: bool = True):
        """Initializes the scanner.

        Args:
            include_entropy: Whether to run the Shannon-entropy heuristic in
                addition to the regex patterns. ``security --deep`` enables it
                for the focused command; ``analyze`` keeps it enabled.
        """
        self.include_entropy = include_entropy
        self.compiled_patterns = {k: re.compile(v) for k, v in self.PATTERNS.items()}

    @classmethod
    def rule_ids(cls) -> set[str]:
        """Returns the ids of all secret-detection rules.

        Returns:
            The ``PATTERNS`` keys plus the inline ``HIGH_ENTROPY`` rule.
        """
        return set(cls.PATTERNS) | {"HIGH_ENTROPY"}

    def scan_text(self, text: str) -> list[SecretFinding]:
        """Scans a file's content for secrets line by line."""
        findings = []
        lines = text.splitlines()

        for i, line in enumerate(lines, 1):
            # 1. Regex Pattern Matching
            for p_name, pattern in self.compiled_patterns.items():
                match = pattern.search(line)
                if match:
                    findings.append(
                        SecretFinding(
                            type=p_name,
                            message=f"Possible hardcoded secret detected: {p_name}",
                            line=i,
                            confidence=("HIGH" if p_name != "GENERIC_SECRET" else "MEDIUM"),
                        )
                    )

            # 2. Entropy Analysis for long strings (heuristic)
            if not self.include_entropy:
                continue
            # Find strings in double or single quotes
            str_matches = re.finditer(r"[\"']([A-Za-z0-9/+=]{20,})[\"']", line)
            for m in str_matches:
                candidate = m.group(1)
                entropy = self.calculate_entropy(candidate)
                # Shanon entropy: random strings usually > 3.5 - 4.0
                if entropy > _ENTROPY_THRESHOLD:
                    findings.append(
                        SecretFinding(
                            type="HIGH_ENTROPY",
                            message=f"High-entropy string detected (possible token/key): {candidate[:8]}...",
                            line=i,
                            confidence="MEDIUM",
                        )
                    )

        return findings

    @staticmethod
    def calculate_entropy(data: str) -> float:
        """Calculates Shannon entropy of a string."""
        if not data:
            return 0.0
        entropy = 0.0
        for x in range(256):
            p_x = float(data.count(chr(x))) / len(data)
            if p_x > 0:
                entropy += -p_x * math.log(p_x, 2)
        return entropy
