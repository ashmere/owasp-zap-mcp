#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool Initialization Module

Centralized initialization of all OWASP ZAP tools, ensuring they are correctly registered with MCP
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
        async def zap_health_check_tool() -> Dict[str, Any]:
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
        async def zap_spider_scan_tool(url: str, max_depth: int = 5) -> Dict[str, Any]:
            """Wrapper: Start spider scan"""
            return await mcp_zap_spider_scan(url=url, max_depth=max_depth)

        # Register Tool: Active Scan
        @mcp.tool(
            "zap_active_scan",
            description="""[Function Description]: Start an active security scan on a target URL.
[Parameter Content]:
- url (string) [Required] - Target URL to scan
- scan_policy (string) [Optional] - Custom scan policy name""",
        )
        async def zap_active_scan_tool(
            url: str, scan_policy: Optional[str] = None
        ) -> Dict[str, Any]:
            """Wrapper: Start active security scan"""
            return await mcp_zap_active_scan(url=url, scan_policy=scan_policy)

        # Register Tool: Spider Status
        @mcp.tool(
            "zap_spider_status",
            description="""[Function Description]: Get the status of a spider scan.
[Parameter Content]:
- scan_id (string) [Required] - ID of the spider scan to check""",
        )
        async def zap_spider_status_tool(scan_id: str) -> Dict[str, Any]:
            """Wrapper: Get spider scan status"""
            return await mcp_zap_spider_status(scan_id=scan_id)

        # Register Tool: Active Scan Status
        @mcp.tool(
            "zap_active_scan_status",
            description="""[Function Description]: Get the status of an active scan.
[Parameter Content]:
- scan_id (string) [Required] - ID of the active scan to check""",
        )
        async def zap_active_scan_status_tool(scan_id: str) -> Dict[str, Any]:
            """Wrapper: Get active scan status"""
            return await mcp_zap_active_scan_status(scan_id=scan_id)

        # Register Tool: Get Alerts
        @mcp.tool(
            "zap_get_alerts",
            description="""[Function Description]: Get security alerts from ZAP.
[Parameter Content]:
- risk_level (string) [Optional] - Filter by risk level (High, Medium, Low, Informational)""",
        )
        async def zap_get_alerts_tool(
            risk_level: Optional[str] = None,
        ) -> Dict[str, Any]:
            """Wrapper: Get security alerts"""
            return await mcp_zap_get_alerts(risk_level=risk_level)

        # Register Tool: Generate HTML Report
        @mcp.tool(
            "zap_generate_html_report",
            description="""[Function Description]: Generate an HTML security report from ZAP.
[Parameter Content]:
- No parameters required""",
        )
        async def zap_generate_html_report_tool() -> Dict[str, Any]:
            """Wrapper: Generate HTML report"""
            return await mcp_zap_generate_html_report()

        # Register Tool: Generate JSON Report
        @mcp.tool(
            "zap_generate_json_report",
            description="""[Function Description]: Generate a JSON security report from ZAP.
[Parameter Content]:
- No parameters required""",
        )
        async def zap_generate_json_report_tool() -> Dict[str, Any]:
            """Wrapper: Generate JSON report"""
            return await mcp_zap_generate_json_report()

        # Register Tool: Clear Session
        @mcp.tool(
            "zap_clear_session",
            description="""[Function Description]: Clear ZAP session data.
[Parameter Content]:
- No parameters required""",
        )
        async def zap_clear_session_tool() -> Dict[str, Any]:
            """Wrapper: Clear ZAP session"""
            return await mcp_zap_clear_session()

        # Register Tool: Scan Summary
        @mcp.tool(
            "zap_scan_summary",
            description="""[Function Description]: Get a comprehensive scan summary for a URL.
[Parameter Content]:
- url (string) [Required] - Target URL to get summary for""",
        )
        async def zap_scan_summary_tool(url: str) -> Dict[str, Any]:
            """Wrapper: Get scan summary"""
            return await mcp_zap_scan_summary(url=url)

        # Get tool count
        tools_count = len(await mcp.list_tools())
        logger.info(f"Registered all OWASP ZAP MCP tools, total {tools_count} tools")
        return True

    except Exception as e:
        logger.error(f"Error registering OWASP ZAP MCP tools: {str(e)}")
        logger.error(traceback.format_exc())
        return False
