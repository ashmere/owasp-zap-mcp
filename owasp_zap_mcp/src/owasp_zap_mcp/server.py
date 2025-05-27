"""
DEPRECATED: Legacy server implementation

This file is deprecated. Please use the new modular structure:

For stdio mode:
- Use: owasp-zap-mcp (CLI command from pyproject.toml)
- Or: python -m owasp_zap_mcp.mcp_core

For SSE/HTTP mode:
- Use: python -m owasp_zap_mcp.main --sse

The new implementation follows Apache Doris MCP server patterns with:
- Modular architecture (tools/, config.py, mcp_core.py)
- Proper tool registration through tool_initializer.py
- Environment-based configuration
- Better error handling and logging
- Support for both stdio and SSE transports
"""

import logging
import warnings

logger = logging.getLogger(__name__)


def deprecated_warning():
    """Show deprecation warning."""
    warnings.warn(
        "This server.py file is deprecated. Use 'owasp-zap-mcp' command or the new modular structure.",
        DeprecationWarning,
        stacklevel=2,
    )
    logger.warning("DEPRECATED: Use 'owasp-zap-mcp' command or new modular structure")


# Show warning when imported
deprecated_warning()

# For backward compatibility, import the new implementation
try:
    from .mcp_core import stdio_mcp as mcp

    logger.info("Loaded new MCP implementation for backward compatibility")
except ImportError as e:
    logger.error(f"Failed to load new MCP implementation: {e}")
    raise

import asyncio
import os
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from .zap_client import ZAPAlert, ZAPClient, ZAPScanStatus

# Configure logging
logging.basicConfig(level=logging.INFO)

# ZAP connection settings
ZAP_BASE_URL = os.getenv("ZAP_BASE_URL", "http://zap:8080")
ZAP_API_KEY = os.getenv("ZAP_API_KEY")


@mcp.tool()
async def zap_health_check() -> str:
    """Check if ZAP is running and accessible."""
    try:
        async with ZAPClient(base_url=ZAP_BASE_URL, api_key=ZAP_API_KEY) as client:
            is_healthy = await client.health_check()
            if is_healthy:
                return "✅ ZAP is running and accessible"
            else:
                return "❌ ZAP is not responding"
    except Exception as e:
        return f"❌ ZAP health check failed: {str(e)}"


@mcp.tool()
async def zap_spider_scan(url: str, max_depth: int = 5) -> str:
    """
    Start a spider scan to discover content on a target URL.

    Args:
        url: Target URL to scan
        max_depth: Maximum crawl depth (default: 5)
    """
    try:
        async with ZAPClient(base_url=ZAP_BASE_URL, api_key=ZAP_API_KEY) as client:
            scan_id = await client.spider_scan(url, max_depth)
            return f"✅ Spider scan started for {url} with scan ID: {scan_id}"
    except Exception as e:
        return f"❌ Failed to start spider scan: {str(e)}"


@mcp.tool()
async def zap_active_scan(url: str, scan_policy: Optional[str] = None) -> str:
    """
    Start an active security scan on a target URL.

    Args:
        url: Target URL to scan
        scan_policy: Custom scan policy name (optional)
    """
    try:
        async with ZAPClient(base_url=ZAP_BASE_URL, api_key=ZAP_API_KEY) as client:
            scan_id = await client.active_scan(url, scan_policy)
            return f"✅ Active scan started for {url} with scan ID: {scan_id}"
    except Exception as e:
        return f"❌ Failed to start active scan: {str(e)}"


@mcp.tool()
async def zap_spider_status(scan_id: str) -> str:
    """
    Get the status of a spider scan.

    Args:
        scan_id: ID of the spider scan to check
    """
    try:
        async with ZAPClient(base_url=ZAP_BASE_URL, api_key=ZAP_API_KEY) as client:
            status = await client.get_spider_status(scan_id)
            return (
                f"Spider scan {scan_id}: {status.status} ({status.progress}% complete)"
            )
    except Exception as e:
        return f"❌ Failed to get spider scan status: {str(e)}"


@mcp.tool()
async def zap_active_scan_status(scan_id: str) -> str:
    """
    Get the status of an active scan.

    Args:
        scan_id: ID of the active scan to check
    """
    try:
        async with ZAPClient(base_url=ZAP_BASE_URL, api_key=ZAP_API_KEY) as client:
            status = await client.get_active_scan_status(scan_id)
            return (
                f"Active scan {scan_id}: {status.status} ({status.progress}% complete)"
            )
    except Exception as e:
        return f"❌ Failed to get active scan status: {str(e)}"


@mcp.tool()
async def zap_get_alerts(risk_level: Optional[str] = None) -> str:
    """
    Get security alerts from ZAP.

    Args:
        risk_level: Filter by risk level (High, Medium, Low, Informational)
    """
    try:
        async with ZAPClient(base_url=ZAP_BASE_URL, api_key=ZAP_API_KEY) as client:
            alerts = await client.get_alerts(risk_level)

            if not alerts:
                return "✅ No security alerts found"

            result = f"🚨 Found {len(alerts)} security alerts:\n\n"
            for i, alert in enumerate(alerts[:10], 1):  # Limit to first 10
                result += f"{i}. {alert.name}\n"
                result += f"   Risk: {alert.risk} | Confidence: {alert.confidence}\n"
                result += f"   URL: {alert.url}\n"
                result += f"   Description: {alert.description[:100]}...\n\n"

            if len(alerts) > 10:
                result += f"... and {len(alerts) - 10} more alerts"

            return result
    except Exception as e:
        return f"❌ Failed to get alerts: {str(e)}"


@mcp.tool()
async def zap_generate_html_report() -> str:
    """Generate an HTML security report from ZAP."""
    try:
        async with ZAPClient(base_url=ZAP_BASE_URL, api_key=ZAP_API_KEY) as client:
            report = await client.generate_html_report()
            return f"✅ HTML report generated successfully (length: {len(report)} characters)"
    except Exception as e:
        return f"❌ Failed to generate HTML report: {str(e)}"


@mcp.tool()
async def zap_generate_json_report() -> str:
    """Generate a JSON security report from ZAP."""
    try:
        async with ZAPClient(base_url=ZAP_BASE_URL, api_key=ZAP_API_KEY) as client:
            report = await client.generate_json_report()
            return f"✅ JSON report generated with {report['total_alerts']} alerts"
    except Exception as e:
        return f"❌ Failed to generate JSON report: {str(e)}"


@mcp.tool()
async def zap_clear_session() -> str:
    """Clear ZAP session data."""
    try:
        async with ZAPClient(base_url=ZAP_BASE_URL, api_key=ZAP_API_KEY) as client:
            success = await client.clear_session()
            if success:
                return "✅ ZAP session cleared successfully"
            else:
                return "❌ Failed to clear ZAP session"
    except Exception as e:
        return f"❌ Failed to clear session: {str(e)}"


@mcp.tool()
async def zap_passive_scan_status() -> str:
    """Get the status of passive scanning."""
    try:
        async with ZAPClient(base_url=ZAP_BASE_URL, api_key=ZAP_API_KEY) as client:
            # For passive scan, we'll check if there are any alerts
            alerts = await client.get_alerts()
            return f"✅ Passive scanning active - {len(alerts)} alerts found so far"
    except Exception as e:
        return f"❌ Failed to get passive scan status: {str(e)}"


@mcp.tool()
async def zap_scan_summary(url: str) -> str:
    """
    Get a comprehensive scan summary for a URL.

    Args:
        url: Target URL to get summary for
    """
    try:
        async with ZAPClient(base_url=ZAP_BASE_URL, api_key=ZAP_API_KEY) as client:
            alerts = await client.get_alerts()

            # Filter alerts for the specific URL
            url_alerts = [alert for alert in alerts if url in alert.url]

            if not url_alerts:
                return f"✅ No security issues found for {url}"

            # Count by risk level
            risk_counts = {"High": 0, "Medium": 0, "Low": 0, "Informational": 0}
            for alert in url_alerts:
                if alert.risk in risk_counts:
                    risk_counts[alert.risk] += 1

            summary = f"🔍 Security Summary for {url}:\n\n"
            summary += f"Total Issues: {len(url_alerts)}\n"
            summary += f"High Risk: {risk_counts['High']}\n"
            summary += f"Medium Risk: {risk_counts['Medium']}\n"
            summary += f"Low Risk: {risk_counts['Low']}\n"
            summary += f"Informational: {risk_counts['Informational']}\n"

            return summary
    except Exception as e:
        return f"❌ Failed to get scan summary: {str(e)}"


if __name__ == "__main__":
    # Run the server
    mcp.run()
