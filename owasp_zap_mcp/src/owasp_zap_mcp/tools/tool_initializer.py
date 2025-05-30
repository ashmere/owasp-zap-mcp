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
    logger.info("Starting to register OWASP ZAP MCP tools...")

    try:
        # Register Tool: Health Check
        @mcp.tool(
            "zap_health_check",
            description="""[Function Description]: Check if OWASP ZAP is running and accessible.
[Parameter Content]:
- No parameters required""",
        )
        async def zap_health_check_tool(random_string: str = "") -> Dict[str, Any]:
            """Wrapper: Check ZAP health status"""
            return await mcp_zap_health_check()

        # Register Tool: Spider Scan
        @mcp.tool(
            "zap_spider_scan",
            description="""[Function Description]: Start a spider scan to discover content on a target URL.
[Parameter Content]:
- url (string) [Required] - Target URL to scan
- max_depth (integer) [Optional] - Maximum crawl depth, default 5""",
        )
        async def zap_spider_scan_tool(random_string: str = "") -> Dict[str, Any]:
            """Wrapper: Start spider scan
            
            The random_string parameter will be processed by the SSE server to extract
            the URL and other parameters automatically.
            """
            # This function signature uses random_string which gets processed by SSE server
            # The SSE server's _process_tool_arguments will extract URL from random_string
            # and call the actual function with proper parameters
            raise RuntimeError("This wrapper should be called via SSE server parameter processing")

        # Register Tool: Active Scan
        @mcp.tool(
            "zap_active_scan",
            description="""[Function Description]: Start an active security scan on a target URL.
[Parameter Content]:
- url (string) [Required] - Target URL to scan
- scan_policy (string) [Optional] - Custom scan policy name""",
        )
        async def zap_active_scan_tool(random_string: str = "") -> Dict[str, Any]:
            """Wrapper: Start active security scan
            
            The random_string parameter will be processed by the SSE server to extract
            the URL and other parameters automatically.
            """
            raise RuntimeError("This wrapper should be called via SSE server parameter processing")

        # Register Tool: Spider Status
        @mcp.tool(
            "zap_spider_status",
            description="""[Function Description]: Get the status of a spider scan.
[Parameter Content]:
- scan_id (string) [Required] - ID of the spider scan to check""",
        )
        async def zap_spider_status_tool(random_string: str = "") -> Dict[str, Any]:
            """Wrapper: Get spider scan status
            
            The random_string parameter will be processed by the SSE server to extract
            the scan_id automatically.
            """
            raise RuntimeError("This wrapper should be called via SSE server parameter processing")

        # Register Tool: Active Scan Status
        @mcp.tool(
            "zap_active_scan_status",
            description="""[Function Description]: Get the status of an active scan.
[Parameter Content]:
- scan_id (string) [Required] - ID of the active scan to check""",
        )
        async def zap_active_scan_status_tool(random_string: str = "") -> Dict[str, Any]:
            """Wrapper: Get active scan status
            
            The random_string parameter will be processed by the SSE server to extract
            the scan_id automatically.
            """
            raise RuntimeError("This wrapper should be called via SSE server parameter processing")

        # Register Tool: Get Alerts
        @mcp.tool(
            "zap_get_alerts",
            description="""[Function Description]: Get security alerts from ZAP.
[Parameter Content]:
- risk_level (string) [Optional] - Filter by risk level (High, Medium, Low, Informational)""",
        )
        async def zap_get_alerts_tool(random_string: str = "") -> Dict[str, Any]:
            """Wrapper: Get security alerts
            
            The random_string parameter will be processed by the SSE server to extract
            the risk_level if specified.
            """
            raise RuntimeError("This wrapper should be called via SSE server parameter processing")

        # Register Tool: Generate HTML Report
        @mcp.tool(
            "zap_generate_html_report",
            description="""[Function Description]: Generate an HTML security report from ZAP.
[Parameter Content]:
- No parameters required""",
        )
        async def zap_generate_html_report_tool(random_string: str = "") -> Dict[str, Any]:
            """Wrapper: Generate HTML report"""
            return await mcp_zap_generate_html_report()

        # Register Tool: Generate JSON Report
        @mcp.tool(
            "zap_generate_json_report",
            description="""[Function Description]: Generate a JSON security report from ZAP.
[Parameter Content]:
- No parameters required""",
        )
        async def zap_generate_json_report_tool(random_string: str = "") -> Dict[str, Any]:
            """Wrapper: Generate JSON report"""
            return await mcp_zap_generate_json_report()

        # Register Tool: Clear Session
        @mcp.tool(
            "zap_clear_session",
            description="""[Function Description]: Clear ZAP session data.
[Parameter Content]:
- No parameters required""",
        )
        async def zap_clear_session_tool(random_string: str = "") -> Dict[str, Any]:
            """Wrapper: Clear ZAP session"""
            return await mcp_zap_clear_session()

        # Register Tool: Scan Summary
        @mcp.tool(
            "zap_scan_summary",
            description="""[Function Description]: Get a comprehensive scan summary for a URL.
[Parameter Content]:
- url (string) [Required] - Target URL to get summary for""",
        )
        async def zap_scan_summary_tool(random_string: str = "") -> Dict[str, Any]:
            """Wrapper: Get scan summary
            
            The random_string parameter will be processed by the SSE server to extract
            the URL automatically.
            """
            raise RuntimeError("This wrapper should be called via SSE server parameter processing")

        # Get tool count
        tools_count = len(await mcp.list_tools())
        logger.info(f"Registered all OWASP ZAP MCP tools, total {tools_count} tools")
        return True

    except Exception as e:
        logger.error(f"Error registering OWASP ZAP MCP tools: {str(e)}")
        logger.error(traceback.format_exc())
        return False
