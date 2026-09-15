"""Configuration and TOML parsing utilities."""

import logging
import pathlib
import tomllib
from typing import Any

logger = logging.getLogger("qgis_analyzer")


def load_profile_config(
    project_path: pathlib.Path, profile_name: str = "default"
) -> dict[str, Any]:
    """Loads a specific profile configuration from pyproject.toml.

    Args:
        project_path: Root path of the project.
        profile_name: Name of the configuration profile.

    Returns:
        A dictionary containing the profile configuration.
    """
    pyproject = project_path / "pyproject.toml"
    default_config = {
        "strict": False,
        "generate_html": False,
        "fail_on_error": False,
        "rules": {},
    }

    if not pyproject.exists():
        return default_config

    try:
        with open(pyproject, "rb") as f:
            data = tomllib.load(f)

        profiles = data.get("tool", {}).get("qgis-analyzer", {}).get("profiles", {})
        profile_data = profiles.get(profile_name)

        if not profile_data:
            if profile_name != "default":
                logger.warning(f"Profile '{profile_name}' not found. Using default values.")
            return default_config

        rules_config = profile_data.get("rules", {})

        return {
            **default_config,
            **profile_data,
            "rules": rules_config,
        }
    except Exception as e:
        logger.error(f"Error loading profile: {e}")
        return default_config
