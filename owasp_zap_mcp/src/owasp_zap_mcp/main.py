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
from .sse_server import ZAPMCPSseServer
from .tools.tool_initializer import register_mcp_tools

# Load environment variables (load early for all modes)
load_dotenv(override=True)

# Get logger - note: logging will be configured by load_config()
logger = logging.getLogger("owasp-zap-mcp-main")

# --- Configuration Loading and Logging Setup ---
config = load_config()
logger.info("Main module loaded, configuration initialized")

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
    
    args = parser.parse_args()
    logger.debug(f"Parsed command line arguments: {vars(args)}")
    return args


@asynccontextmanager
async def app_lifespan(app_instance: FastAPI) -> AsyncIterator[None]:
    logger.info("SSE application lifecycle starting...")
    
    # Store configuration in app state
    app_instance.state.config = config
    logger.debug("Configuration stored in app state")
    
    try:
        logger.info("Application startup complete, yielding control")
        yield
    except Exception as e:
        logger.error(f"Error during application lifespan: {e}", exc_info=True)
        raise
    finally:
        logger.info("Cleaning up SSE application resources...")


async def start_sse_server(args):
    """Start SSE Web server mode (Configures the global 'app')"""
    logger.info("=== Starting OWASP ZAP MCP SSE Server ===")
    logger.debug(f"Start arguments: {vars(args)}")
    
    global app

    # --- Initialize MCP and Tools for SSE ---
    logger.info("Initializing MCP instance for SSE mode...")
    sse_mcp = FastMCP(
        name="owasp-zap-mcp-sse",
        description="OWASP ZAP MCP Server (SSE)",
        lifespan=None,  # Managed by FastAPI
    )
    logger.debug(f"MCP instance created: {sse_mcp.name}")
    
    logger.info("Registering MCP tools for SSE mode...")
    try:
        await register_mcp_tools(sse_mcp)
        logger.info("✅ MCP tools registered successfully for SSE mode")
        
        # Debug: List registered tools
        if logger.isEnabledFor(logging.DEBUG):
            tools = await sse_mcp.list_tools()
            tool_names = [getattr(tool, 'name', str(tool)) for tool in tools]
            logger.debug(f"Registered tools: {tool_names}")
            
    except Exception as e:
        logger.error(f"❌ Failed to register MCP tools: {e}", exc_info=True)
        raise

    # --- Configure Lifespan and CORS for the global app ---
    logger.debug("Configuring FastAPI app lifespan and CORS...")
    app.router.lifespan_context = app_lifespan
    
    origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    allow_credentials = os.getenv("MCP_ALLOW_CREDENTIALS", "false").lower() == "true"
    
    logger.debug(f"CORS Origins: {origins}")
    logger.debug(f"CORS Allow Credentials: {allow_credentials}")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Mcp-Session-Id"],
    )
    logger.debug("CORS middleware configured")

    # --- Initialize SSE Server Handler and Register Routes ---
    logger.info("Initializing SSE server handler...")
    try:
        sse_server_handler = ZAPMCPSseServer(sse_mcp, app)
        logger.info("✅ SSE server handler initialized and routes registered")
    except Exception as e:
        logger.error(f"❌ Failed to initialize SSE server handler: {e}", exc_info=True)
        raise

    # --- Print Configuration and Endpoints ---
    print("\n" + "="*50)
    print("     OWASP ZAP MCP Server (SSE Mode)")
    print("="*50)
    print(f"🔧 Server Host: {args.host}")
    print(f"🔧 Server Port: {args.port}")
    print(f"🔧 Log Level: {config.get('log_level_str', 'INFO')}")
    print(f"🔧 Debug Mode: {args.debug}")
    print(f"🔧 Reload Mode: {args.reload}")
    print(f"🔧 ZAP Base URL: {config.get('zap_base_url', 'NOT SET')}")
    print(f"🔧 Allowed Origins: {origins}")
    print(f"🔧 Allow Credentials: {allow_credentials}")
    print("-" * 50)
    
    base_url = f"http://{args.host}:{args.port}"
    print(f"🌐 Service URL: {base_url}")
    print(f"🏥 Health Check: GET {base_url}/health")
    print(f"📊 Status Check: GET {base_url}/status")
    print(f"🔄 SSE Endpoint: GET {base_url}/sse")
    print(f"📨 MCP Messages: POST {base_url}/mcp/messages")
    print("-" * 50)
    print("📖 Usage Examples:")
    print(f"   curl {base_url}/health")
    print(f"   curl {base_url}/status")
    print("-" * 50)
    print("⚠️  Use Ctrl+C to stop the service")
    print("="*50 + "\n")

    # --- Start Uvicorn Server ---
    logger.info(f"Starting Uvicorn server on {args.host}:{args.port}")
    logger.debug(f"Uvicorn config - debug: {args.debug}, reload: {args.reload}")
    
    try:
        config = Config(
            app=app,
            host=args.host,
            port=args.port,
            log_level="debug" if args.debug else "info",
            reload=args.reload,
        )
        server = Server(config=config)
        logger.info("🚀 Uvicorn server starting...")
        await server.serve()
        
    except Exception as e:
        logger.error(f"❌ Failed to start Uvicorn server: {e}", exc_info=True)
        raise


# --- Main Execution Logic ---
def run_main_sync():
    """Synchronous wrapper, primarily for SSE mode now."""
    sync_logger = logging.getLogger("run_main_sync")
    sync_logger.info("Entering run_main_sync (SSE mode entry point)")
    
    try:
        args = parse_args()
        sync_logger.debug(f"Command line arguments parsed: {vars(args)}")

        if args.sse:
            sync_logger.info("SSE mode requested, starting async server...")
            try:
                # Run the async SSE server setup and Uvicorn loop
                asyncio.run(start_sse_server(args))
                sync_logger.info("✅ SSE server completed successfully")
                
            except KeyboardInterrupt:
                sync_logger.info("🛑 SSE server stopped by user (Ctrl+C)")
                print("\n🛑 Server stopped by user")
                
            except Exception as e:
                sync_logger.critical(f"💥 Critical error in SSE server: {e}", exc_info=True)
                print(f"\n💥 Critical error: {e}")
                raise
        else:
            # If run without --sse, print help/error
            message = (
                "❌ Error: This entry point requires --sse flag.\n"
                "For stdio mode, use 'owasp-zap-mcp' command or the appropriate MCP client setup."
            )
            sync_logger.error(message)
            print(message, file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        sync_logger.critical(f"💥 Fatal error in run_main_sync: {e}", exc_info=True)
        print(f"\n💥 Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_main_sync()
