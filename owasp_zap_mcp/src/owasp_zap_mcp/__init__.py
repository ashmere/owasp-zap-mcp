#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
OWASP ZAP MCP Server

A native Model Context Protocol (MCP) server for OWASP ZAP security scanning.
Enables AI-driven security testing through direct integration with Cursor IDE
and other MCP-compatible clients.

DISCLAIMER: This project is an independent implementation and is not officially
associated with, endorsed by, or affiliated with the OWASP Foundation or the
OWASP ZAP project. OWASP and ZAP are trademarks of the OWASP Foundation.
"""

__version__ = "0.1.0"
__author__ = "ZAP-MCP-Tooling Team"
__description__ = "Native MCP server for OWASP ZAP security scanning"

from . import tools
from .config import load_config

# Import main components
from .zap_client import ZAPClient

__all__ = ["ZAPClient", "load_config", "tools"]
