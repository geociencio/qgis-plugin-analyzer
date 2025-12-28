import pathlib
import pytest
from src.analyzer.scanner import validate_plugin_structure, validate_metadata, audit_qgis_standards

def test_validate_plugin_structure(tmp_path):
    # Setup: Create a fake plugin structure
    (tmp_path / "metadata.txt").write_text("name=Test")
    (tmp_path / "__init__.py").write_text("def classFactory(): pass")
    (tmp_path / "LICENSE").write_text("GPL")
    
    result = validate_plugin_structure(tmp_path)
    assert result["is_valid"] is True
    assert result["files"]["metadata.txt"] is True
    assert result["has_class_factory"] is True

def test_validate_plugin_structure_missing_file(tmp_path):
    (tmp_path / "__init__.py").write_text("def classFactory(): pass")
    
    result = validate_plugin_structure(tmp_path)
    assert result["is_valid"] is False
    assert result["files"]["metadata.txt"] is False

def test_validate_metadata(tmp_path):
    metadata_content = """
[general]
name=Test Plugin
description=A description
version=0.1
qgisMinimumVersion=3.0
author=Tester
email=test@test.com
"""
    meta_file = tmp_path / "metadata.txt"
    meta_file.write_text(metadata_content)
    
    result = validate_metadata(tmp_path)
    assert result["is_valid"] is True
    assert len(result["missing"]) == 0

def test_validate_metadata_missing_fields(tmp_path):
    meta_file = tmp_path / "metadata.txt"
    meta_file.write_text("name=Test\nversion=0.1")
    
    result = validate_metadata(tmp_path)
    assert result["is_valid"] is False
    assert "description" in result["missing"]

def test_audit_qgis_standards(tmp_path):
    py_content = """
layer = mapLayersByName("test")[0]
QIcon("icons/my_icon.png")
print("debug")
"""
    py_file = tmp_path / "test_plugin.py"
    py_file.write_text(py_content)
    
    modules_data = [{"path": "test_plugin.py"}]
    results = audit_qgis_standards(modules_data, tmp_path)
    
    issue_types = [i["type"] for i in results["issues"]]
    assert "UNPRECISE_LAYER_LOOKUP" in issue_types
    assert "MANUAL_RESOURCE_PATH" in issue_types
    assert "PRINT_STATEMENT" in issue_types
