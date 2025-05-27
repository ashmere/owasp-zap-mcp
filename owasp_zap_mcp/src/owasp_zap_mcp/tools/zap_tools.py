#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
OWASP ZAP MCP Tools Implementation

Core tool implementations for OWASP ZAP security scanning operations.
These functions are called by the MCP tool wrappers.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from ..config import ZAP_API_KEY, ZAP_BASE_URL
from ..zap_client import ZAPAlert, ZAPClient, ZAPScanStatus

logger = logging.getLogger("owasp-zap-tools")


async def mcp_zap_health_check() -> Dict[str, Any]:
    """Check if ZAP is running and accessible."""
    try:
        async with ZAPClient(base_url=ZAP_BASE_URL, api_key=ZAP_API_KEY) as client:
            is_healthy = await client.health_check()
            if is_healthy:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                {
                                    "success": True,
                                    "message": "✅ ZAP is running and accessible",
                                    "status": "healthy",
                                }
                            ),
                        }
                    ]
                }
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                {
                                    "success": False,
                                    "error": "❌ ZAP is not responding",
                                    "status": "unhealthy",
                                }
                            ),
                        }
                    ]
                }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(
                        {
                            "success": False,
                            "error": f"❌ ZAP health check failed: {str(e)}",
                            "status": "error",
                        }
                    ),
                }
            ]
        }


async def mcp_zap_spider_scan(url: str, max_depth: int = 5) -> Dict[str, Any]:
    """Start a spider scan to discover content on a target URL."""
    try:
        if not url:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            {"success": False, "error": "Missing url parameter"}
                        ),
                    }
                ]
            }

        async with ZAPClient(base_url=ZAP_BASE_URL, api_key=ZAP_API_KEY) as client:
            scan_id = await client.spider_scan(url, max_depth)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            {
                                "success": True,
                                "message": f"✅ Spider scan started for {url}",
                                "scan_id": scan_id,
                                "url": url,
                                "max_depth": max_depth,
                            }
                        ),
                    }
                ]
            }
    except Exception as e:
        logger.error(f"Spider scan failed: {e}")
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(
                        {
                            "success": False,
                            "error": f"❌ Failed to start spider scan: {str(e)}",
                        }
                    ),
                }
            ]
        }


async def mcp_zap_active_scan(
    url: str, scan_policy: Optional[str] = None
) -> Dict[str, Any]:
    """Start an active security scan on a target URL."""
    try:
        if not url:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            {"success": False, "error": "Missing url parameter"}
                        ),
                    }
                ]
            }

        async with ZAPClient(base_url=ZAP_BASE_URL, api_key=ZAP_API_KEY) as client:
            scan_id = await client.active_scan(url, scan_policy)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            {
                                "success": True,
                                "message": f"✅ Active scan started for {url}",
                                "scan_id": scan_id,
                                "url": url,
                                "scan_policy": scan_policy,
                            }
                        ),
                    }
                ]
            }
    except Exception as e:
        logger.error(f"Active scan failed: {e}")
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(
                        {
                            "success": False,
                            "error": f"❌ Failed to start active scan: {str(e)}",
                        }
                    ),
                }
            ]
        }


async def mcp_zap_spider_status(scan_id: str) -> Dict[str, Any]:
    """Get the status of a spider scan."""
    try:
        if not scan_id:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            {"success": False, "error": "Missing scan_id parameter"}
                        ),
                    }
                ]
            }

        async with ZAPClient(base_url=ZAP_BASE_URL, api_key=ZAP_API_KEY) as client:
            status = await client.get_spider_status(scan_id)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            {
                                "success": True,
                                "scan_id": scan_id,
                                "status": status.status,
                                "progress": status.progress,
                                "message": f"Spider scan {scan_id}: {status.status} ({status.progress}% complete)",
                            }
                        ),
                    }
                ]
            }
    except Exception as e:
        logger.error(f"Failed to get spider status: {e}")
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(
                        {
                            "success": False,
                            "error": f"❌ Failed to get spider scan status: {str(e)}",
                        }
                    ),
                }
            ]
        }


async def mcp_zap_active_scan_status(scan_id: str) -> Dict[str, Any]:
    """Get the status of an active scan."""
    try:
        if not scan_id:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            {"success": False, "error": "Missing scan_id parameter"}
                        ),
                    }
                ]
            }

        async with ZAPClient(base_url=ZAP_BASE_URL, api_key=ZAP_API_KEY) as client:
            status = await client.get_active_scan_status(scan_id)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            {
                                "success": True,
                                "scan_id": scan_id,
                                "status": status.status,
                                "progress": status.progress,
                                "message": f"Active scan {scan_id}: {status.status} ({status.progress}% complete)",
                            }
                        ),
                    }
                ]
            }
    except Exception as e:
        logger.error(f"Failed to get active scan status: {e}")
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(
                        {
                            "success": False,
                            "error": f"❌ Failed to get active scan status: {str(e)}",
                        }
                    ),
                }
            ]
        }


async def mcp_zap_get_alerts(risk_level: Optional[str] = None) -> Dict[str, Any]:
    """Get security alerts from ZAP."""
    try:
        async with ZAPClient(base_url=ZAP_BASE_URL, api_key=ZAP_API_KEY) as client:
            alerts = await client.get_alerts(risk_level)

            if not alerts:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                {
                                    "success": True,
                                    "message": "✅ No security alerts found",
                                    "total_alerts": 0,
                                    "alerts": [],
                                }
                            ),
                        }
                    ]
                }

            # Convert alerts to serializable format
            alert_data = []
            for alert in alerts[:10]:  # Limit to first 10
                alert_data.append(
                    {
                        "name": alert.name,
                        "risk": alert.risk,
                        "confidence": alert.confidence,
                        "url": alert.url,
                        "description": (
                            alert.description[:200] + "..."
                            if len(alert.description) > 200
                            else alert.description
                        ),
                        "solution": (
                            alert.solution[:200] + "..."
                            if len(alert.solution) > 200
                            else alert.solution
                        ),
                    }
                )

            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            {
                                "success": True,
                                "total_alerts": len(alerts),
                                "displayed_alerts": len(alert_data),
                                "risk_filter": risk_level,
                                "alerts": alert_data,
                                "message": f"🚨 Found {len(alerts)} security alerts"
                                + (f" (showing first 10)" if len(alerts) > 10 else ""),
                            }
                        ),
                    }
                ]
            }
    except Exception as e:
        logger.error(f"Failed to get alerts: {e}")
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(
                        {
                            "success": False,
                            "error": f"❌ Failed to get alerts: {str(e)}",
                        }
                    ),
                }
            ]
        }


async def mcp_zap_generate_html_report() -> Dict[str, Any]:
    """Generate an HTML security report from ZAP."""
    try:
        async with ZAPClient(base_url=ZAP_BASE_URL, api_key=ZAP_API_KEY) as client:
            report = await client.generate_html_report()
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            {
                                "success": True,
                                "message": f"✅ HTML report generated successfully",
                                "report_length": len(report),
                                "report_preview": (
                                    report[:500] + "..."
                                    if len(report) > 500
                                    else report
                                ),
                            }
                        ),
                    }
                ]
            }
    except Exception as e:
        logger.error(f"Failed to generate HTML report: {e}")
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(
                        {
                            "success": False,
                            "error": f"❌ Failed to generate HTML report: {str(e)}",
                        }
                    ),
                }
            ]
        }


async def mcp_zap_generate_json_report() -> Dict[str, Any]:
    """Generate a JSON security report from ZAP."""
    try:
        async with ZAPClient(base_url=ZAP_BASE_URL, api_key=ZAP_API_KEY) as client:
            report = await client.generate_json_report()
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            {
                                "success": True,
                                "message": f"✅ JSON report generated with {report['total_alerts']} alerts",
                                "report": report,
                            }
                        ),
                    }
                ]
            }
    except Exception as e:
        logger.error(f"Failed to generate JSON report: {e}")
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(
                        {
                            "success": False,
                            "error": f"❌ Failed to generate JSON report: {str(e)}",
                        }
                    ),
                }
            ]
        }


async def mcp_zap_clear_session() -> Dict[str, Any]:
    """Clear ZAP session data."""
    try:
        async with ZAPClient(base_url=ZAP_BASE_URL, api_key=ZAP_API_KEY) as client:
            success = await client.clear_session()
            if success:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                {
                                    "success": True,
                                    "message": "✅ ZAP session cleared successfully",
                                }
                            ),
                        }
                    ]
                }
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                {
                                    "success": False,
                                    "error": "❌ Failed to clear ZAP session",
                                }
                            ),
                        }
                    ]
                }
    except Exception as e:
        logger.error(f"Failed to clear session: {e}")
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(
                        {
                            "success": False,
                            "error": f"❌ Failed to clear session: {str(e)}",
                        }
                    ),
                }
            ]
        }


async def mcp_zap_scan_summary(url: str) -> Dict[str, Any]:
    """Get a comprehensive scan summary for a URL."""
    try:
        if not url:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            {"success": False, "error": "Missing url parameter"}
                        ),
                    }
                ]
            }

        async with ZAPClient(base_url=ZAP_BASE_URL, api_key=ZAP_API_KEY) as client:
            alerts = await client.get_alerts()

            # Filter alerts for the specific URL
            url_alerts = [alert for alert in alerts if url in alert.url]

            if not url_alerts:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                {
                                    "success": True,
                                    "url": url,
                                    "total_issues": 0,
                                    "risk_summary": {
                                        "High": 0,
                                        "Medium": 0,
                                        "Low": 0,
                                        "Informational": 0,
                                    },
                                    "message": f"✅ No security issues found for {url}",
                                }
                            ),
                        }
                    ]
                }

            # Count by risk level
            risk_counts = {"High": 0, "Medium": 0, "Low": 0, "Informational": 0}
            for alert in url_alerts:
                if alert.risk in risk_counts:
                    risk_counts[alert.risk] += 1

            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            {
                                "success": True,
                                "url": url,
                                "total_issues": len(url_alerts),
                                "risk_summary": risk_counts,
                                "message": f"🔍 Security Summary for {url}: {len(url_alerts)} total issues",
                            }
                        ),
                    }
                ]
            }
    except Exception as e:
        logger.error(f"Failed to get scan summary: {e}")
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(
                        {
                            "success": False,
                            "error": f"❌ Failed to get scan summary: {str(e)}",
                        }
                    ),
                }
            ]
        }
