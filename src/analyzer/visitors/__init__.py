"""AST Visitors for QGIS Plugin Analysis.

This package provides modular AST visitors for analyzing QGIS plugin code.
Each visitor is specialized for a specific concern (imports, metrics, standards, security).
"""

from .composite_visitor import CompositeVisitor
from .security_visitor import SecurityVisitor

# Maintain backward compatibility
QGISASTVisitor = CompositeVisitor
QGISSecurityVisitor = SecurityVisitor

__all__ = [
    "QGISASTVisitor",
    "QGISSecurityVisitor",
    "CompositeVisitor",
    "SecurityVisitor",
]
