# /***************************************************************************
#  QGIS Plugin Analyzer
#
#  Repository compliance validators for QGIS.org policies.
#  ***************************************************************************/

import pathlib
import urllib.request
import urllib.error
from typing import Dict, List, Tuple


# Prohibited binary extensions per QGIS repository policy
BINARY_EXTENSIONS = {".exe", ".dll", ".so", ".dylib", ".pyd", ".bin", ".a", ".lib"}


def scan_for_binaries(project_path: pathlib.Path) -> List[str]:
    """
    Scans project for prohibited binary files.
    
    Returns list of relative paths to binary files found.
    """
    binaries = []
    
    for file_path in project_path.rglob("*"):
        if file_path.is_file():
            if file_path.suffix.lower() in BINARY_EXTENSIONS:
                rel_path = str(file_path.relative_to(project_path))
                binaries.append(rel_path)
    
    return binaries


def calculate_package_size(
    project_path: pathlib.Path, ignore_matcher=None
) -> float:
    """
    Calculates total package size in MB.
    
    Respects ignore patterns if provided.
    Returns size in megabytes (MB).
    """
    total_size = 0
    
    for file_path in project_path.rglob("*"):
        if file_path.is_file():
            # Skip if matches ignore pattern
            if ignore_matcher:
                rel_path = str(file_path.relative_to(project_path))
                if ignore_matcher.is_ignored(file_path):
                    continue
            
            total_size += file_path.stat().st_size
    
    # Convert bytes to MB
    return total_size / (1024 * 1024)


def validate_metadata_urls(metadata: Dict[str, str]) -> Dict[str, str]:
    """
    Validates URLs from metadata.txt.
    
    Checks: homepage, tracker, repository
    Returns dict: {url: status} where status is 'ok', 'error', or 'timeout'
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


def validate_plugin_structure(project_path: pathlib.Path) -> Dict[str, any]:
    """
    Validates required plugin structure.
    
    Checks for:
    - __init__.py (and classFactory)
    - metadata.txt
    - LICENSE
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



def validate_metadata(metadata_path: pathlib.Path) -> Dict[str, any]:
    """
    Validates metadata.txt content.
    
    Checks for required fields per QGIS repository requirements.
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
        with open(metadata_path, "r", encoding="utf-8") as f:
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
    recommended_missing = [
        f for f in recommended_fields if f not in metadata or not metadata[f]
    ]
    
    return {
        "is_valid": len(missing) == 0,
        "missing": missing,
        "recommended_missing": recommended_missing,
        "metadata": metadata,
    }
