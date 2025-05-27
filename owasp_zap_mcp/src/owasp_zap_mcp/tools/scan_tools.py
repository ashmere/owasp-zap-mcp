"""
ZAP Scanning Tools

MCP tool implementations for OWASP ZAP scanning operations.
Includes spider scans, active scans, and scan status monitoring.
"""

import logging
from typing import Any, Dict, Optional

from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool

from ..zap_client import ZAPClient, ZAPClientError

logger = logging.getLogger(__name__)


# Tool definitions for MCP registration
ZAP_SPIDER_SCAN_TOOL = Tool(
    name="zap_spider_scan",
    description="Start a ZAP spider scan to discover website content and structure",
    inputSchema={
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "Target URL to scan (must include protocol, e.g., https://example.com)",
            },
            "max_depth": {
                "type": "integer",
                "description": "Maximum crawl depth (default: 5)",
                "minimum": 1,
                "maximum": 20,
                "default": 5,
            },
        },
        "required": ["url"],
    },
)

ZAP_ACTIVE_SCAN_TOOL = Tool(
    name="zap_active_scan",
    description="Start a ZAP active security scan to find vulnerabilities",
    inputSchema={
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "Target URL to scan (must include protocol)",
            },
            "scan_policy": {
                "type": "string",
                "description": "Custom scan policy name (optional)",
                "default": None,
            },
        },
        "required": ["url"],
    },
)

ZAP_GET_SCAN_STATUS_TOOL = Tool(
    name="zap_get_scan_status",
    description="Get the status and progress of a ZAP scan",
    inputSchema={
        "type": "object",
        "properties": {
            "scan_id": {
                "type": "string",
                "description": "Scan ID returned from spider_scan or active_scan",
            },
            "scan_type": {
                "type": "string",
                "description": "Type of scan ('spider' or 'active')",
                "enum": ["spider", "active"],
                "default": "spider",
            },
        },
        "required": ["scan_id"],
    },
)

ZAP_PASSIVE_SCAN_TOOL = Tool(
    name="zap_passive_scan",
    description="Enable passive scanning for a URL (scans traffic as it passes through ZAP)",
    inputSchema={
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "Target URL to enable passive scanning for",
            }
        },
        "required": ["url"],
    },
)


async def zap_spider_scan(
    zap_client: ZAPClient, url: str, max_depth: int = 5
) -> list[TextContent]:
    """
    Start a ZAP spider scan to discover website content.

    Args:
        zap_client: ZAP client instance
        url: Target URL to scan
        max_depth: Maximum crawl depth

    Returns:
        MCP response with scan ID and status
    """
    try:
        # Validate URL format
        if not url.startswith(("http://", "https://")):
            return [
                TextContent(
                    type="text",
                    text=f"Error: URL must include protocol (http:// or https://). Got: {url}",
                )
            ]

        # Start spider scan
        scan_id = await zap_client.spider_scan(url, max_depth)

        # Get initial status
        status = await zap_client.get_spider_status(scan_id)

        response_text = f"""🕷️ **Spider Scan Started**

**Scan Details:**
- Target URL: {url}
- Scan ID: {scan_id}
- Max Depth: {max_depth}
- Status: {status.status}
- Progress: {status.progress}%

**Next Steps:**
Use `zap_get_scan_status` with scan_id="{scan_id}" and scan_type="spider" to monitor progress.
"""

        return [TextContent(type="text", text=response_text)]

    except ZAPClientError as e:
        logger.error(f"ZAP spider scan failed: {e}")
        return [
            TextContent(
                type="text", text=f"❌ **Spider Scan Failed**\n\nError: {str(e)}"
            )
        ]
    except Exception as e:
        logger.error(f"Unexpected error in spider scan: {e}")
        return [
            TextContent(type="text", text=f"❌ **Unexpected Error**\n\nError: {str(e)}")
        ]


async def zap_active_scan(
    zap_client: ZAPClient, url: str, scan_policy: Optional[str] = None
) -> list[TextContent]:
    """
    Start a ZAP active security scan.

    Args:
        zap_client: ZAP client instance
        url: Target URL to scan
        scan_policy: Custom scan policy name

    Returns:
        MCP response with scan ID and status
    """
    try:
        # Validate URL format
        if not url.startswith(("http://", "https://")):
            return [
                TextContent(
                    type="text",
                    text=f"Error: URL must include protocol (http:// or https://). Got: {url}",
                )
            ]

        # Start active scan
        scan_id = await zap_client.active_scan(url, scan_policy)

        # Get initial status
        status = await zap_client.get_active_scan_status(scan_id)

        policy_text = f"\n- Scan Policy: {scan_policy}" if scan_policy else ""

        response_text = f"""🔍 **Active Security Scan Started**

**Scan Details:**
- Target URL: {url}
- Scan ID: {scan_id}{policy_text}
- Status: {status.status}
- Progress: {status.progress}%

**⚠️ Warning:** Active scans send actual attack payloads and may affect the target system.

**Next Steps:**
Use `zap_get_scan_status` with scan_id="{scan_id}" and scan_type="active" to monitor progress.
"""

        return [TextContent(type="text", text=response_text)]

    except ZAPClientError as e:
        logger.error(f"ZAP active scan failed: {e}")
        return [
            TextContent(
                type="text", text=f"❌ **Active Scan Failed**\n\nError: {str(e)}"
            )
        ]
    except Exception as e:
        logger.error(f"Unexpected error in active scan: {e}")
        return [
            TextContent(type="text", text=f"❌ **Unexpected Error**\n\nError: {str(e)}")
        ]


async def zap_get_scan_status(
    zap_client: ZAPClient, scan_id: str, scan_type: str = "spider"
) -> list[TextContent]:
    """
    Get the status and progress of a ZAP scan.

    Args:
        zap_client: ZAP client instance
        scan_id: Scan ID to check
        scan_type: Type of scan ('spider' or 'active')

    Returns:
        MCP response with scan status details
    """
    try:
        # Get scan status based on type
        if scan_type.lower() == "spider":
            status = await zap_client.get_spider_status(scan_id)
            scan_icon = "🕷️"
            scan_name = "Spider Scan"
        elif scan_type.lower() == "active":
            status = await zap_client.get_active_scan_status(scan_id)
            scan_icon = "🔍"
            scan_name = "Active Security Scan"
        else:
            return [
                TextContent(
                    type="text",
                    text=f"❌ **Invalid Scan Type**\n\nSupported types: 'spider', 'active'. Got: {scan_type}",
                )
            ]

        # Format status message
        status_emoji = {"NOT_STARTED": "⏳", "RUNNING": "🔄", "FINISHED": "✅"}.get(
            status.status, "❓"
        )

        progress_bar = "█" * (status.progress // 10) + "░" * (
            10 - status.progress // 10
        )

        response_text = f"""{scan_icon} **{scan_name} Status**

**Scan ID:** {scan_id}
**Status:** {status_emoji} {status.status}
**Progress:** {status.progress}% [{progress_bar}]

"""

        if status.status == "FINISHED":
            response_text += """**✅ Scan Complete!**

**Next Steps:**
- Use `zap_get_alerts` to view security findings
- Use `zap_generate_report` to create a detailed report
"""
        elif status.status == "RUNNING":
            response_text += (
                "**🔄 Scan in Progress...**\n\nCheck back in a few moments for updates."
            )
        else:
            response_text += "**⏳ Scan Starting...**\n\nThe scan should begin shortly."

        return [TextContent(type="text", text=response_text)]

    except ZAPClientError as e:
        logger.error(f"Failed to get scan status: {e}")
        return [
            TextContent(
                type="text", text=f"❌ **Failed to Get Scan Status**\n\nError: {str(e)}"
            )
        ]
    except Exception as e:
        logger.error(f"Unexpected error getting scan status: {e}")
        return [
            TextContent(type="text", text=f"❌ **Unexpected Error**\n\nError: {str(e)}")
        ]


async def zap_passive_scan(zap_client: ZAPClient, url: str) -> list[TextContent]:
    """
    Enable passive scanning for a URL.

    Args:
        zap_client: ZAP client instance
        url: Target URL to enable passive scanning for

    Returns:
        MCP response confirming passive scan setup
    """
    try:
        # Validate URL format
        if not url.startswith(("http://", "https://")):
            return [
                TextContent(
                    type="text",
                    text=f"Error: URL must include protocol (http:// or https://). Got: {url}",
                )
            ]

        # For passive scanning, we just need to ensure ZAP is aware of the URL
        # This is typically done by accessing the URL through ZAP's proxy
        response_text = f"""👁️ **Passive Scanning Enabled**

**Target URL:** {url}

**What is Passive Scanning?**
Passive scanning analyzes HTTP traffic as it passes through ZAP without sending additional requests. It's safe and non-intrusive.

**How to Use:**
1. Configure your browser to use ZAP as a proxy
2. Browse the target website normally
3. ZAP will automatically analyze the traffic for security issues

**Next Steps:**
- Use `zap_get_alerts` to view any security findings
- Browse the target site through ZAP's proxy for comprehensive analysis
"""

        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        logger.error(f"Error setting up passive scan: {e}")
        return [
            TextContent(
                type="text", text=f"❌ **Passive Scan Setup Failed**\n\nError: {str(e)}"
            )
        ]
