# -*- coding: utf-8 -*-

"""
Core MCP instance and startup logic for stdio mode.
"""

import asyncio
import json
import logging
import sys
import traceback
from typing import Any, Dict

# Import necessary components from mcp and our project
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger("owasp-zap-mcp-core")

# --- Global MCP Instance for Stdio ---
# Create the instance when the module is imported.
# Tools will be registered before running.
stdio_mcp = FastMCP(
    name="owasp-zap-mcp-stdio-core",
    description="OWASP ZAP MCP Server (stdio via core)",
)


def run_stdio():
    """
    Synchronous entry point for running the stdio server.
    Mimics the Doris MCP pattern by calling .run() on the instance.
    Handles tool registration beforehand.
    """
    logger.info("Executing run_stdio (synchronous entry point)...")

    # Load configuration when actually running
    from .config import load_config

    load_config()

    # Register tools synchronously by running the async function
    try:
        logger.info("Registering OWASP ZAP MCP tools...")
        from .tools.tool_initializer import register_mcp_tools

        asyncio.run(register_mcp_tools(stdio_mcp))
        logger.info("Tools registered successfully")
    except Exception as e:
        logger.critical(f"Failed to register tools: {e}", exc_info=True)
        print(f"ERROR: Failed to register tools: {e}", file=sys.stderr, flush=True)
        sys.exit(1)

    # --- Run the stdio server using the instance's run() method ---
    logger.info("Calling stdio_mcp.run()...")
    try:
        # Assuming stdio_mcp has a synchronous run() method for stdio
        stdio_mcp.run()
        logger.info("stdio_mcp.run() completed.")
    except KeyboardInterrupt:
        logger.info("Stdio server stopped by KeyboardInterrupt.")
    except AttributeError:
        logger.critical(
            "Error: stdio_mcp object does not have a '.run()' method suitable for stdio.",
            exc_info=False,
        )
        print(
            "ERROR: stdio_mcp object does not have a '.run()' method.",
            file=sys.stderr,
            flush=True,
        )
        sys.exit(1)
    except Exception as e:
        logger.critical(
            f"run_stdio encountered an error during stdio_mcp.run(): {e}", exc_info=True
        )
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
