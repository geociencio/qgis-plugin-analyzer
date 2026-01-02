# /***************************************************************************
#  QGIS Plugin Analyzer
#
#  Repository compliance validators for QGIS.org policies.
#  ***************************************************************************/

import ipaddress
import pathlib
import socket
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List

# Prohibited binary extensions per QGIS repository policy
BINARY_EXTENSIONS = {".exe", ".dll", ".so", ".dylib", ".pyd", ".bin", ".a", ".lib"}


def scan_for_binaries(project_path: pathlib.Path, ignore_matcher: Any = None) -> List[str]:
    """Scans the project for prohibited binary files per QGIS policies.

    Args:
        project_path: Root path of the project.
        ignore_matcher: Optional object to determine if a path should be ignored.

    Returns:
        A list of relative paths to any binary files found.
    """
    binaries = []

    for file_path in project_path.rglob("*"):
        if file_path.is_file():
            # Skip if matches ignore pattern
            if ignore_matcher and ignore_matcher.is_ignored(file_path):
                continue

            if file_path.suffix.lower() in BINARY_EXTENSIONS:
                rel_path = str(file_path.relative_to(project_path))
                binaries.append(rel_path)

    return binaries


def calculate_package_size(project_path: pathlib.Path, ignore_matcher: Any = None) -> float:
    """Calculates the total package size in Megabytes (MB).

    Args:
        project_path: Root path of the project.
        ignore_matcher: Optional object to determine if a path should be ignored.

    Returns:
        The total size of the plugin package in MB.
    """
    total_size = 0

    for file_path in project_path.rglob("*"):
        if file_path.is_file():
            # Skip if matches ignore pattern
            if ignore_matcher:
                str(file_path.relative_to(project_path))
                if ignore_matcher.is_ignored(file_path):
                    continue

            total_size += file_path.stat().st_size

    # Convert bytes to MB
    return total_size / (1024 * 1024)


def is_ssrf_safe(url: str) -> bool:
    """Checks if a URL is safe from Server-Side Request Forgery (SSRF).

    Validates that the hostname does not resolve to private, loopback, or
    local IP ranges.

    Args:
        url: The URL string to validate.

    Returns:
        True if the URL is considered safe for outbound requests, False otherwise.
    """
    try:
        parsed = urllib.parse.urlparse(url)
        hostname = parsed.hostname
        # We also block URLs without a hostname or non-standard ports if needed,
        # but here we focus on IP resolving.
        if not hostname:
            return False

        # Basic name check for common local addresses
        if hostname.lower() in ("localhost", "127.0.0.1", "::1"):
            return False

        # Resolve host to IP
        # We use socket.getaddrinfo to handle both IPv4 and IPv6
        # This is more robust than gethostbyname
        try:
            addresses = socket.getaddrinfo(hostname, None)
        except socket.gaierror:
            # If we can't resolve it, it's either invalid or an internal name
            # we shouldn't trust for public URL validation.
            return False

        for addr in addresses:
            ip_str = addr[4][0]
            ip = ipaddress.ip_address(ip_str)
            # Check for private ranges:
            # 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16 (Private)
            # 127.0.0.0/8 (Loopback)
            # 169.254.0.0/16 (Link Local)
            # and IPv6 equivalents
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_unspecified:
                return False

        return True
    except Exception:
        return False


def validate_metadata_urls(metadata: Dict[str, str]) -> Dict[str, str]:
    """Validates the accessibility of URLs defined in the plugin metadata.

    Args:
        metadata: A dictionary containing metadata fields and their values.

    Returns:
        A dictionary mapping each URL to its validation status (e.g., 'ok', 'error').
    """
    url_fields = ["homepage", "tracker", "repository"]
    results = {}

    for field in url_fields:
        url = metadata.get(field, "").strip()
        if not url:
            continue

        # Skip if not a valid URL
        if not url.startswith(("http://", "https://")):
            results[url] = "invalid"
            continue

        # SSRF Protection: check if URL is safe before making the request
        if not is_ssrf_safe(url):
            results[url] = "error_ssrf_blocked"
            continue

        try:
            # HEAD request to check availability
            req = urllib.request.Request(url, method="HEAD")
            req.add_header("User-Agent", "QGIS-Plugin-Analyzer/1.0")

            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    results[url] = "ok"
                else:
                    results[url] = f"error_{response.status}"

        except urllib.error.HTTPError as e:
            results[url] = f"error_{e.code}"
        except urllib.error.URLError:
            results[url] = "error"
        except TimeoutError:
            results[url] = "timeout"
        except Exception:
            results[url] = "error"

    return results


def validate_plugin_structure(project_path: pathlib.Path) -> Dict[str, Any]:
    """Validates that the plugin following the required QGIS file structure.

    Args:
        project_path: Root path of the plugin project.

    Returns:
        A dictionary containing the validation results and overall status.
    """
    mandatory = ["metadata.txt", "__init__.py", "LICENSE"]
    found = {f: (project_path / f).exists() for f in mandatory}

    # Check classFactory in __init__.py
    init_file = project_path / "__init__.py"
    has_factory = False
    if init_file.exists():
        try:
            content = init_file.read_text(encoding="utf-8", errors="replace")
            has_factory = "def classFactory" in content
        except Exception:
            has_factory = False

    missing = [f for f, exists in found.items() if not exists]
    py_files = list(project_path.glob("*.py"))
    has_python = len(py_files) > 0

    return {
        "files": found,
        "missing_files": missing,
        "has_class_factory": has_factory,
        "has_python_files": has_python,
        "is_valid": all(found.values()) and has_factory and has_python,
    }


def validate_metadata(metadata_path: pathlib.Path) -> Dict[str, Any]:
    """Validates the content of the metadata.txt file against QGIS requirements.

    Args:
        metadata_path: Path to the metadata.txt file.

    Returns:
        A dictionary containing validation details and mandatory/recommended missing fields.
    """
    required_fields = [
        "name",
        "description",
        "version",
        "qgisMinimumVersion",
        "author",
        "email",
    ]

    recommended_fields = [
        "homepage",
        "tracker",
        "repository",
        "tags",
        "category",
    ]

    if not metadata_path.exists():
        return {
            "is_valid": False,
            "missing": required_fields,
            "recommended_missing": recommended_fields,
        }

    # Parse metadata.txt
    metadata = {}
    try:
        with open(metadata_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    metadata[key.strip()] = value.strip()
    except Exception:
        return {
            "is_valid": False,
            "missing": required_fields,
            "recommended_missing": recommended_fields,
            "error": "Failed to parse metadata.txt",
        }

    missing = [f for f in required_fields if f not in metadata or not metadata[f]]
    recommended_missing = [f for f in recommended_fields if f not in metadata or not metadata[f]]

    return {
        "is_valid": len(missing) == 0,
        "missing": missing,
        "recommended_missing": recommended_missing,
        "metadata": metadata,
    }
