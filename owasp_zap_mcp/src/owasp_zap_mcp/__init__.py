# -*- coding: utf-8 -*-

"""
OWASP ZAP MCP Server Package

A Model Context Protocol (MCP) server implementation for integrating OWASP ZAP
security scanning capabilities with AI-powered development workflows.

Author: Mat Davies (@ashmere)
Project: https://github.com/ashmere/owasp-zap-mcp
"""

__version__ = "0.2.0"
__title__ = "owasp-zap-mcp"
__description__ = "OWASP ZAP MCP Server for AI-powered security testing"
__url__ = "https://github.com/ashmere/owasp-zap-mcp"
__author__ = "Mat Davies"
__author_email__ = "mat.davies@ashmere.dev"
__license__ = "MIT"
__copyright__ = "Copyright 2024 Mat Davies"

from . import tools
from .config import load_config

# Import main components
from .zap_client import ZAPClient

__all__ = [
    "__version__",
    "__title__",
    "__description__",
    "__url__",
    "__author__",
    "__author_email__",
    "__license__",
    "__copyright__",
]
