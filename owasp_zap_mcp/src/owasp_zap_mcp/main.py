#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
OWASP ZAP MCP Server Main Entry - Primarily handles SSE mode

Stdio mode is handled by owasp_zap_mcp.mcp_core:run_stdio.
"""

import argparse
import asyncio
import logging
import os
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, Dict

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import Config, Server

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# MCP related imports
from mcp.server.fastmcp import FastMCP

# Config and Tool Initializer
from .config import SERVER_HOST, SERVER_PORT, load_config
from .tools.tool_initializer import register_mcp_tools
from .sse_server import ZAPMCPSseServer

# Load environment variables (load early for all modes)
load_dotenv(override=True)

# Get logger
logger = logging.getLogger("owasp-zap-mcp-main")

# --- Configuration Loading and Logging Setup ---
load_config()

# --- Create FastAPI App (Global Scope for SSE Mode) ---
app = FastAPI(
    title="OWASP ZAP MCP Server (SSE Mode)",
)


# --- Command Line Argument Parsing ---
def parse_args():
    parser = argparse.ArgumentParser(
        description="OWASP ZAP MCP Server (SSE Mode Entry)"
    )
    parser.add_argument(
        "--sse", action="store_true", help="Start SSE Web server mode (required)"
    )
    parser.add_argument("--host", type=str, default=SERVER_HOST, help="Host address")
    parser.add_argument("--port", type=int, default=SERVER_PORT, help="Port number")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    return parser.parse_args()


# --- SSE Mode Specific Code ---
@dataclass
class AppContext:
    config: Dict[str, Any]


@asynccontextmanager
async def app_lifespan(app_instance: FastAPI) -> AsyncIterator[None]:
    logger.info("SSE application lifecycle start...")
    config = load_config()
    app_instance.state.config = config
    try:
        yield
    finally:
        logger.info("Cleaning up SSE application resources...")


async def start_sse_server(args):
    """Start SSE Web server mode (Configures the global 'app')"""
    logger.info("Starting SSE Web server mode...")
    global app

    # --- Initialize MCP and Tools for SSE ---
    sse_mcp = FastMCP(
        name="owasp-zap-mcp-sse",
        description="OWASP ZAP MCP Server (SSE)",
        lifespan=None,  # Managed by FastAPI
    )
    logger.info("Registering MCP tools for SSE mode...")
    await register_mcp_tools(sse_mcp)
    logger.info("MCP tools registered for SSE.")

    # --- Configure Lifespan and CORS for the global app ---
    app.router.lifespan_context = app_lifespan
    origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    allow_credentials = os.getenv("MCP_ALLOW_CREDENTIALS", "false").lower() == "true"
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Mcp-Session-Id"],
    )

    # --- Initialize SSE Server Handler and Register Routes ---
    logger.info("Initializing SSE server handler and registering routes...")
    sse_server_handler = ZAPMCPSseServer(sse_mcp, app)
    logger.info("SSE Server handler initialized and routes registered.")

    # --- Print Configuration and Endpoints ---
    print("--- SSE Mode Configuration ---")
    print(f"Server Host: {args.host}")
    print(f"Server Port: {args.port}")
    print(f"Allowed Origins: {origins}")
    print(f"Allow Credentials: {allow_credentials}")
    print(f"Log Level: {os.getenv('LOG_LEVEL', 'info')}")
    print(f"Debug Mode: {args.debug}")
    print(f"Reload Mode: {args.reload}")
    print(f"ZAP Base URL: {os.getenv('ZAP_BASE_URL')}")
    print("------------------------------")
    base_url = f"http://{args.host}:{args.port}"
    print(f"Service running at: {base_url}")
    print(f"  Health Check: GET {base_url}/health")
    print(f"  Status Check: GET {base_url}/status")
    print(f"  SSE Init: GET {base_url}/sse")
    print(f"  MCP Messages: POST {base_url}/mcp/messages")
    print("------------------------------")
    print("Use Ctrl+C to stop the service")

    # --- Start Uvicorn Server ---
    config = Config(
        app=app,
        host=args.host,
        port=args.port,
        log_level="debug" if args.debug else "info",
        reload=args.reload,
    )
    server = Server(config=config)
    await server.serve()


# --- Main Execution Logic ---
def run_main_sync():
    """Synchronous wrapper, primarily for SSE mode now."""
    sync_logger = logging.getLogger("run_main_sync")
    sync_logger.info("Entering run_main_sync (SSE focus)...")
    args = parse_args()

    if args.sse:
        try:
            # Run the async SSE server setup and Uvicorn loop
            asyncio.run(start_sse_server(args))
            sync_logger.info("asyncio.run(start_sse_server) completed.")
        except KeyboardInterrupt:
            sync_logger.info("SSE server stopped by KeyboardInterrupt.")
        except Exception as e:
            sync_logger.critical(
                f"Error during asyncio.run(start_sse_server): {e}", exc_info=True
            )
            raise
    else:
        # If run without --sse, print help/error
        message = "Error: This entry point requires --sse flag. For stdio mode, use 'owasp-zap-mcp' or the appropriate command for your stdio setup."
        sync_logger.error(message)
        print(message, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_main_sync()
