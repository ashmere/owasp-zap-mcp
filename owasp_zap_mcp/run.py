#!/usr/bin/env python3
"""
DEPRECATED: Legacy run script

This file is deprecated. Please use the new modular structure:

For stdio mode:
- Use: owasp-zap-mcp (CLI command from pyproject.toml)
- Or: python -m owasp_zap_mcp.mcp_core

For SSE/HTTP mode:
- Use: python -m owasp_zap_mcp.main --sse

The new implementation follows Apache Doris MCP server patterns.
"""

import logging
import sys
import warnings


def main():
    """Show deprecation warning and exit."""
    warnings.warn(
        "This run.py file is deprecated. Use 'owasp-zap-mcp' command or new modular structure.",
        DeprecationWarning,
        stacklevel=2,
    )

    print("=" * 80)
    print("DEPRECATED: This run.py file is deprecated!")
    print()
    print("Please use the new modular structure:")
    print()
    print("For stdio mode:")
    print("  owasp-zap-mcp")
    print("  # or")
    print("  python -m owasp_zap_mcp.mcp_core")
    print()
    print("For SSE/HTTP mode:")
    print("  python -m owasp_zap_mcp.main --sse")
    print()
    print("The new implementation follows Apache Doris MCP server patterns.")
    print("=" * 80)

    sys.exit(1)


if __name__ == "__main__":
    main()
