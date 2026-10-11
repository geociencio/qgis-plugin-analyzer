"""Strongly typed project configuration for the analysis engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ProjectConfig:
    """Strongly typed project configuration."""

    strict: bool = False
    generate_html: bool = True
    fail_on_error: bool = False
    project_type: str = "auto"
    rules: dict[str, Any] = field(default_factory=dict)
    fail_on_critical: bool = False
    include_content: bool = False
    workers: int | None = None
    cache: bool = True
