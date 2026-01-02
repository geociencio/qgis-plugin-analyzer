"""Configuration and TOML parsing utilities."""

import logging
import pathlib
import re
from typing import Any, Dict

logger = logging.getLogger("qgis_analyzer")


def _parse_toml_value(val_str: str) -> Any:
    """Converts a TOML value string to appropriate Python type."""
    if val_str.lower() == "true":
        return True
    elif val_str.lower() == "false":
        return False
    elif re.match(r"^-?\d+$", val_str):
        return int(val_str)
    elif (val_str.startswith('"') and val_str.endswith('"')) or (
        val_str.startswith("'") and val_str.endswith("'")
    ):
        return val_str[1:-1]
    return val_str


def _process_section_header(line: str, profile_regex: re.Pattern, rules_regex: re.Pattern) -> tuple:
    """Processes a TOML section header."""
    rules_match = rules_regex.match(line)
    if rules_match:
        return rules_match.group(1), True

    profile_match = profile_regex.match(line)
    if profile_match:
        return profile_match.group(1), False

    return None, False


def _ensure_profile_structure(data: dict, profile_name: str, is_rules: bool) -> None:
    """Ensures the profile structure exists in the data dictionary."""
    if profile_name not in data["tool"]["qgis-analyzer"]["profiles"]:
        data["tool"]["qgis-analyzer"]["profiles"][profile_name] = {}

    if is_rules and "rules" not in data["tool"]["qgis-analyzer"]["profiles"][profile_name]:
        data["tool"]["qgis-analyzer"]["profiles"][profile_name]["rules"] = {}


def _minimal_toml_load(file_obj) -> Dict[str, Any]:
    """EXTREMELY minimal TOML parser for pyproject.toml."""
    data = {"tool": {"qgis-analyzer": {"profiles": {}}}}
    current_profile = None
    in_rules_section = False

    profile_regex = re.compile(r"^\[tool\.qgis-analyzer\.profiles\.([\w-]+)\]")
    rules_regex = re.compile(r"^\[tool\.qgis-analyzer\.profiles\.([\w-]+)\.rules\]")

    try:
        content = file_obj.read().decode("utf-8")
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if line.startswith("[") and line.endswith("]"):
                profile_name, is_rules = _process_section_header(line, profile_regex, rules_regex)
                if profile_name:
                    current_profile = profile_name
                    in_rules_section = is_rules
                    _ensure_profile_structure(data, current_profile, in_rules_section)
                else:
                    current_profile = None
                    in_rules_section = False
                continue

            if current_profile and "=" in line:
                key, val = line.split("=", 1)
                key = key.strip()
                val = _parse_toml_value(val.strip())

                if in_rules_section:
                    data["tool"]["qgis-analyzer"]["profiles"][current_profile]["rules"][key] = val
                else:
                    data["tool"]["qgis-analyzer"]["profiles"][current_profile][key] = val
    except Exception as e:
        logger.error(f"Error in minimal TOML parser: {e}")

    return data


try:
    import tomllib
except ImportError:
    tomllib = None


def load_profile_config(
    project_path: pathlib.Path, profile_name: str = "default"
) -> Dict[str, Any]:
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
        "generate_html": True,
        "fail_on_error": False,
        "rules": {},
    }

    if not pyproject.exists():
        return default_config

    try:
        with open(pyproject, "rb") as f:
            if tomllib:
                import tomllib as tl  # type: ignore

                data = tl.load(f)
            else:
                data = _minimal_toml_load(f)

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
