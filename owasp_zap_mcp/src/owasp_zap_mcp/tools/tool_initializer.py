# -*- coding: utf-8 -*-

"""
OWASP ZAP MCP Tool Initializer

This module handles the initialization and registration of ZAP tools for the MCP server.
"""

import json
import logging
import traceback
from typing import Any, Dict, Optional

# Import ZAP tool implementations
from .zap_tools import (
    mcp_zap_active_scan,
    mcp_zap_active_scan_status,
    mcp_zap_clear_session,
    mcp_zap_generate_html_report,
    mcp_zap_generate_json_report,
    mcp_zap_get_alerts,
    mcp_zap_health_check,
    mcp_zap_scan_summary,
    mcp_zap_spider_scan,
    mcp_zap_spider_status,
)

# Get logger
logger = logging.getLogger("owasp-zap-tools-initializer")


async def register_mcp_tools(mcp):
    """Register MCP tool functions

    Args:
        mcp: FastMCP instance
    """
    logger.info("=== Starting OWASP ZAP MCP Tool Registration ===")

    # Tool definition mapping
    tools_to_register = [
        {
            "name": "zap_health_check",
            "description": "Check if ZAP is running and accessible",
            "function": mcp_zap_health_check,
            "parameters": {
                "type": "object",
                "properties": {
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools",
                    }
                },
                "required": ["random_string"],
            },
        },
        {
            "name": "zap_spider_scan",
            "description": "Start a spider scan to discover content on a target URL",
            "function": mcp_zap_spider_scan,
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Target URL to scan"},
                    "max_depth": {
                        "type": "integer",
                        "description": "Maximum crawl depth, default 5",
                    },
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools",
                    },
                },
                "required": ["random_string"],
            },
        },
        {
            "name": "zap_active_scan",
            "description": "Start an active security scan on a target URL",
            "function": mcp_zap_active_scan,
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Target URL to scan"},
                    "scan_policy": {
                        "type": "string",
                        "description": "Custom scan policy name",
                    },
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools",
                    },
                },
                "required": ["random_string"],
            },
        },
        {
            "name": "zap_spider_status",
            "description": "Get the status of a spider scan",
            "function": mcp_zap_spider_status,
            "parameters": {
                "type": "object",
                "properties": {
                    "scan_id": {
                        "type": "string",
                        "description": "ID of the spider scan to check",
                    },
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools",
                    },
                },
                "required": ["random_string"],
            },
        },
        {
            "name": "zap_active_scan_status",
            "description": "Get the status of an active scan",
            "function": mcp_zap_active_scan_status,
            "parameters": {
                "type": "object",
                "properties": {
                    "scan_id": {
                        "type": "string",
                        "description": "ID of the active scan to check",
                    },
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools",
                    },
                },
                "required": ["random_string"],
            },
        },
        {
            "name": "zap_get_alerts",
            "description": "Get security alerts from ZAP",
            "function": mcp_zap_get_alerts,
            "parameters": {
                "type": "object",
                "properties": {
                    "risk_level": {
                        "type": "string",
                        "description": "Filter by risk level (High, Medium, Low, Informational)",
                    },
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools",
                    },
                },
                "required": ["random_string"],
            },
        },
        {
            "name": "zap_generate_html_report",
            "description": "Generate an HTML security report from ZAP",
            "function": mcp_zap_generate_html_report,
            "parameters": {
                "type": "object",
                "properties": {
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools",
                    }
                },
                "required": ["random_string"],
            },
        },
        {
            "name": "zap_generate_json_report",
            "description": "Generate a JSON security report from ZAP",
            "function": mcp_zap_generate_json_report,
            "parameters": {
                "type": "object",
                "properties": {
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools",
                    }
                },
                "required": ["random_string"],
            },
        },
        {
            "name": "zap_clear_session",
            "description": "Clear ZAP session data",
            "function": mcp_zap_clear_session,
            "parameters": {
                "type": "object",
                "properties": {
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools",
                    }
                },
                "required": ["random_string"],
            },
        },
        {
            "name": "zap_scan_summary",
            "description": "Get a comprehensive scan summary for a URL",
            "function": mcp_zap_scan_summary,
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Target URL to get summary for",
                    },
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools",
                    },
                },
                "required": ["random_string"],
            },
        },
    ]

    # Track registration statistics
    registered_count = 0
    failed_count = 0

    # Register each tool
    for tool_def in tools_to_register:
        tool_name = tool_def["name"]
        logger.debug(f"Registering tool: {tool_name}")

        try:
            # Verify function is callable
            if not callable(tool_def["function"]):
                raise ValueError(f"Tool function for {tool_name} is not callable")

            # Register the tool with MCP
            @mcp.tool(name=tool_name, description=tool_def["description"])
            async def tool_wrapper(**kwargs):
                """MCP tool wrapper that defers to SSE server parameter processing"""
                # This wrapper is called by MCP but actual execution should happen
                # via the SSE server's call_tool method which handles parameter processing
                raise RuntimeError(
                    f"Tool {tool_name} should be called via SSE server parameter processing"
                )

            # Store the actual function reference for SSE server access
            tool_wrapper.actual_function = tool_def["function"]
            tool_wrapper.parameters = tool_def["parameters"]

            registered_count += 1
            logger.debug(f"✅ Successfully registered tool: {tool_name}")

            # Log parameter schema in debug mode
            if logger.isEnabledFor(logging.DEBUG):
                param_names = list(tool_def["parameters"].get("properties", {}).keys())
                logger.debug(f"   Parameters: {param_names}")

        except Exception as e:
            failed_count += 1
            logger.error(f"❌ Failed to register tool {tool_name}: {e}", exc_info=True)
            # Continue with other tools even if one fails

    # Log registration summary
    total_tools = len(tools_to_register)
    logger.info(f"=== Tool Registration Summary ===")
    logger.info(f"Total tools: {total_tools}")
    logger.info(f"Successfully registered: {registered_count}")
    logger.info(f"Failed to register: {failed_count}")

    if failed_count > 0:
        logger.warning(f"⚠️  {failed_count} tools failed to register")

    if registered_count == total_tools:
        logger.info("✅ All tools registered successfully!")
    elif registered_count > 0:
        logger.warning(
            f"⚠️  Partial registration: {registered_count}/{total_tools} tools registered"
        )
    else:
        logger.error("❌ No tools were registered successfully!")
        raise RuntimeError("Tool registration failed completely")

    # Verify registration by listing tools
    if logger.isEnabledFor(logging.DEBUG):
        try:
            registered_tools = await mcp.list_tools()
            tool_names = [getattr(tool, "name", str(tool)) for tool in registered_tools]
            logger.debug(f"Verified registered tools: {tool_names}")
        except Exception as e:
            logger.warning(f"Could not verify tool registration: {e}")

    logger.info("=== Tool Registration Complete ===")
    return registered_count
