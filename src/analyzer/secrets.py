"""Secret detection logic for QGIS Plugin Analyzer.

Handles regex-based matching of API keys and high-entropy string detection.
"""

import math
import re
from dataclasses import dataclass
from typing import List


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

    def __init__(self):
        self.compiled_patterns = {k: re.compile(v) for k, v in self.PATTERNS.items()}

    def scan_text(self, text: str) -> List[SecretFinding]:
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
            # Find strings in double or single quotes
            str_matches = re.finditer(r"[\"']([A-Za-z0-9/+=]{20,})[\"']", line)
            for m in str_matches:
                candidate = m.group(1)
                entropy = self.calculate_entropy(candidate)
                # Shanon entropy: random strings usually > 3.5 - 4.0
                if entropy > 4.5:
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
