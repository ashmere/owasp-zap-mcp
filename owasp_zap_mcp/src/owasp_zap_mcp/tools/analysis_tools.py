"""
ZAP Analysis Tools

MCP tool implementations for OWASP ZAP security analysis and reporting.
Includes alert retrieval, scan results, and report generation.
"""

import logging
from typing import Any, Dict, List, Optional

from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool

from ..zap_client import ZAPAlert, ZAPClient

logger = logging.getLogger(__name__)


# Tool definitions for MCP registration
ZAP_GET_ALERTS_TOOL = Tool(
    name="zap_get_alerts",
    description="Get security alerts from ZAP scans, optionally filtered by risk level",
    inputSchema={
        "type": "object",
        "properties": {
            "risk_level": {
                "type": "string",
                "description": "Filter alerts by risk level (optional)",
                "enum": ["High", "Medium", "Low", "Informational"],
                "default": None,
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of alerts to return (default: 50)",
                "minimum": 1,
                "maximum": 500,
                "default": 50,
            },
        },
        "required": [],
    },
)

ZAP_GET_SCAN_RESULTS_TOOL = Tool(
    name="zap_get_scan_results",
    description="Get detailed results from a completed ZAP scan",
    inputSchema={
        "type": "object",
        "properties": {
            "scan_id": {
                "type": "string",
                "description": "Scan ID to get results for (optional - gets all results if not provided)",
            },
            "include_details": {
                "type": "boolean",
                "description": "Include detailed vulnerability information (default: true)",
                "default": True,
            },
        },
        "required": [],
    },
)

ZAP_GENERATE_REPORT_TOOL = Tool(
    name="zap_generate_report",
    description="Generate a security report from ZAP scan results",
    inputSchema={
        "type": "object",
        "properties": {
            "format": {
                "type": "string",
                "description": "Report format",
                "enum": ["html", "json", "summary"],
                "default": "summary",
            },
            "scan_id": {
                "type": "string",
                "description": "Specific scan ID to report on (optional)",
            },
        },
        "required": [],
    },
)


async def zap_get_alerts(
    zap_client: ZAPClient, risk_level: Optional[str] = None, limit: int = 50
) -> list[TextContent]:
    """
    Get security alerts from ZAP scans.

    Args:
        zap_client: ZAP client instance
        risk_level: Filter by risk level ('High', 'Medium', 'Low', 'Informational')
        limit: Maximum number of alerts to return

    Returns:
        MCP response with security alerts
    """
    try:
        # Get alerts from ZAP
        alerts = await zap_client.get_alerts(risk_level)

        if not alerts:
            filter_text = f" (filtered by {risk_level} risk)" if risk_level else ""
            return [
                TextContent(
                    type="text",
                    text=f"🔍 **No Security Alerts Found**{filter_text}\n\nThis could mean:\n- No scans have been completed yet\n- No vulnerabilities were detected\n- The risk level filter excluded all results",
                )
            ]

        # Limit results
        alerts = alerts[:limit]

        # Group alerts by risk level
        risk_groups = {"High": [], "Medium": [], "Low": [], "Informational": []}

        for alert in alerts:
            risk = alert.risk
            if risk in risk_groups:
                risk_groups[risk].append(alert)

        # Build response
        filter_text = f" (filtered by {risk_level} risk)" if risk_level else ""
        response_text = f"🚨 **Security Alerts Summary**{filter_text}\n\n"

        # Add summary counts
        total_alerts = len(alerts)
        high_count = len(risk_groups["High"])
        medium_count = len(risk_groups["Medium"])
        low_count = len(risk_groups["Low"])
        info_count = len(risk_groups["Informational"])

        response_text += f"""**Alert Counts:**
🔴 High: {high_count}
🟡 Medium: {medium_count}
🟢 Low: {low_count}
🔵 Informational: {info_count}
**Total: {total_alerts}**

"""

        # Add detailed alerts for each risk level
        risk_emojis = {"High": "🔴", "Medium": "🟡", "Low": "🟢", "Informational": "🔵"}

        for risk in ["High", "Medium", "Low", "Informational"]:
            if risk_groups[risk]:
                response_text += f"\n## {risk_emojis[risk]} {risk} Risk Alerts\n\n"

                for i, alert in enumerate(
                    risk_groups[risk][:10], 1
                ):  # Limit to 10 per risk level
                    response_text += f"""**{i}. {alert.name}**
- **URL:** {alert.url}
- **Confidence:** {alert.confidence}
- **Description:** {alert.description[:200]}{'...' if len(alert.description) > 200 else ''}
"""
                    if alert.solution:
                        response_text += f"- **Solution:** {alert.solution[:150]}{'...' if len(alert.solution) > 150 else ''}\n"
                    response_text += "\n"

                if len(risk_groups[risk]) > 10:
                    response_text += f"*... and {len(risk_groups[risk]) - 10} more {risk.lower()} risk alerts*\n\n"

        if total_alerts >= limit:
            response_text += f"\n*Showing first {limit} alerts. Use the limit parameter to see more.*"

        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        logger.error(f"Unexpected error getting alerts: {e}")
        return [
            TextContent(type="text", text=f"❌ **Unexpected Error**\n\nError: {str(e)}")
        ]


async def zap_get_scan_results(
    zap_client: ZAPClient, scan_id: Optional[str] = None, include_details: bool = True
) -> list[TextContent]:
    """
    Get detailed results from ZAP scans.

    Args:
        zap_client: ZAP client instance
        scan_id: Specific scan ID (optional)
        include_details: Include detailed vulnerability information

    Returns:
        MCP response with scan results
    """
    try:
        # Get alerts (which represent scan results)
        alerts = await zap_client.get_alerts()

        if not alerts:
            return [
                TextContent(
                    type="text",
                    text="📊 **No Scan Results Available**\n\nNo completed scans found. Run a spider or active scan first.",
                )
            ]

        # Analyze results
        total_alerts = len(alerts)
        unique_urls = len(set(alert.url for alert in alerts))

        # Risk level analysis
        risk_counts = {"High": 0, "Medium": 0, "Low": 0, "Informational": 0}
        vulnerability_types = {}

        for alert in alerts:
            risk_counts[alert.risk] = risk_counts.get(alert.risk, 0) + 1
            vuln_type = alert.name
            vulnerability_types[vuln_type] = vulnerability_types.get(vuln_type, 0) + 1

        # Build response
        scan_text = f" for scan {scan_id}" if scan_id else ""
        response_text = f"""📊 **Scan Results Summary**{scan_text}

**Overview:**
- **Total Vulnerabilities:** {total_alerts}
- **Affected URLs:** {unique_urls}
- **Risk Distribution:**
  - 🔴 High: {risk_counts['High']}
  - 🟡 Medium: {risk_counts['Medium']}
  - 🟢 Low: {risk_counts['Low']}
  - 🔵 Informational: {risk_counts['Informational']}

"""

        # Top vulnerability types
        if vulnerability_types:
            sorted_vulns = sorted(
                vulnerability_types.items(), key=lambda x: x[1], reverse=True
            )
            response_text += "**Top Vulnerability Types:**\n"
            for vuln_type, count in sorted_vulns[:5]:
                response_text += f"- {vuln_type}: {count} instances\n"
            response_text += "\n"

        # Security recommendations
        if risk_counts["High"] > 0:
            response_text += """🚨 **Critical Action Required:**
High-risk vulnerabilities detected! These should be addressed immediately.

"""
        elif risk_counts["Medium"] > 0:
            response_text += """⚠️ **Action Recommended:**
Medium-risk vulnerabilities found. Plan remediation soon.

"""
        else:
            response_text += """✅ **Good Security Posture:**
No high or medium risk vulnerabilities detected.

"""

        # Detailed findings (if requested)
        if include_details and alerts:
            response_text += "**Sample Findings:**\n\n"

            # Show top 3 highest risk alerts
            high_risk_alerts = [a for a in alerts if a.risk == "High"][:3]
            medium_risk_alerts = [a for a in alerts if a.risk == "Medium"][:3]

            sample_alerts = high_risk_alerts + medium_risk_alerts
            if not sample_alerts:
                sample_alerts = alerts[:3]

            for i, alert in enumerate(sample_alerts, 1):
                risk_emoji = {
                    "High": "🔴",
                    "Medium": "🟡",
                    "Low": "🟢",
                    "Informational": "🔵",
                }.get(alert.risk, "❓")
                response_text += f"""**{i}. {risk_emoji} {alert.name}**
- **Risk:** {alert.risk}
- **URL:** {alert.url}
- **Description:** {alert.description[:300]}{'...' if len(alert.description) > 300 else ''}

"""

        response_text += """**Next Steps:**
- Use `zap_generate_report` to create a detailed report
- Use `zap_get_alerts` with specific risk levels for focused analysis
"""

        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        logger.error(f"Unexpected error getting scan results: {e}")
        return [
            TextContent(type="text", text=f"❌ **Unexpected Error**\n\nError: {str(e)}")
        ]


async def zap_generate_report(
    zap_client: ZAPClient, format: str = "summary", scan_id: Optional[str] = None
) -> list[TextContent]:
    """
    Generate a security report from ZAP scan results.

    Args:
        zap_client: ZAP client instance
        format: Report format ('html', 'json', 'summary')
        scan_id: Specific scan ID (optional)

    Returns:
        MCP response with generated report
    """
    try:
        if format.lower() == "html":
            # Generate HTML report
            html_report = await zap_client.generate_html_report()

            # Return truncated HTML with instructions
            preview = html_report[:1000] if len(html_report) > 1000 else html_report
            response_text = f"""📄 **HTML Report Generated**

**Report Preview:**
```html
{preview}
{'...' if len(html_report) > 1000 else ''}
```

**Full Report Size:** {len(html_report)} characters

**Note:** The complete HTML report is available. In a production environment, this would be saved to a file or served via a web interface.
"""

        elif format.lower() == "json":
            # Generate JSON report
            json_report = await zap_client.generate_json_report()

            response_text = f"""📋 **JSON Report Generated**

**Report Data:**
```json
{str(json_report)[:1500]}
{'...' if len(str(json_report)) > 1500 else ''}
```

**Note:** The complete JSON report contains structured data suitable for integration with other security tools.
"""

        else:  # summary format
            # Generate summary report
            alerts = await zap_client.get_alerts()

            if not alerts:
                return [
                    TextContent(
                        type="text",
                        text="📄 **Security Report**\n\nNo scan data available. Run a scan first to generate a report.",
                    )
                ]

            # Calculate metrics
            total_alerts = len(alerts)
            risk_counts = {"High": 0, "Medium": 0, "Low": 0, "Informational": 0}
            unique_urls = len(set(alert.url for alert in alerts))

            for alert in alerts:
                risk_counts[alert.risk] = risk_counts.get(alert.risk, 0) + 1

            # Calculate risk score (weighted)
            risk_score = (
                risk_counts["High"] * 10
                + risk_counts["Medium"] * 5
                + risk_counts["Low"] * 2
                + risk_counts["Informational"] * 1
            )

            # Determine overall security rating
            if risk_counts["High"] > 0:
                rating = "🔴 CRITICAL"
            elif risk_counts["Medium"] > 5:
                rating = "🟠 HIGH RISK"
            elif risk_counts["Medium"] > 0:
                rating = "🟡 MEDIUM RISK"
            elif risk_counts["Low"] > 10:
                rating = "🟢 LOW RISK"
            else:
                rating = "✅ SECURE"

            scan_text = f" (Scan ID: {scan_id})" if scan_id else ""

            response_text = f"""📄 **Security Assessment Report**{scan_text}

## Executive Summary

**Overall Security Rating:** {rating}
**Risk Score:** {risk_score}/100

## Vulnerability Overview

**Total Issues Found:** {total_alerts}
**URLs Affected:** {unique_urls}

**Risk Breakdown:**
- 🔴 **Critical/High:** {risk_counts['High']} issues
- 🟡 **Medium:** {risk_counts['Medium']} issues
- 🟢 **Low:** {risk_counts['Low']} issues
- 🔵 **Informational:** {risk_counts['Informational']} issues

## Key Findings

"""

            # Add top vulnerabilities
            high_risk = [a for a in alerts if a.risk == "High"]
            if high_risk:
                response_text += (
                    "### 🔴 Critical Issues Requiring Immediate Attention:\n\n"
                )
                for i, alert in enumerate(high_risk[:3], 1):
                    response_text += f"{i}. **{alert.name}** - {alert.url}\n"
                response_text += "\n"

            medium_risk = [a for a in alerts if a.risk == "Medium"]
            if medium_risk:
                response_text += "### 🟡 Medium Priority Issues:\n\n"
                for i, alert in enumerate(medium_risk[:3], 1):
                    response_text += f"{i}. **{alert.name}** - {alert.url}\n"
                response_text += "\n"

            # Recommendations
            response_text += """## Recommendations

"""
            if risk_counts["High"] > 0:
                response_text += (
                    "1. **URGENT:** Address all high-risk vulnerabilities immediately\n"
                )
            if risk_counts["Medium"] > 0:
                response_text += (
                    "2. Plan remediation for medium-risk issues within 30 days\n"
                )
            if risk_counts["Low"] > 0:
                response_text += (
                    "3. Review and address low-risk findings as time permits\n"
                )

            response_text += """
## Next Steps

- Review detailed findings with `zap_get_alerts`
- Generate technical reports with `zap_generate_report format=html`
- Implement security fixes based on priority
- Re-scan after remediation to verify fixes
"""

        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        logger.error(f"Unexpected error generating report: {e}")
        return [
            TextContent(type="text", text=f"❌ **Unexpected Error**\n\nError: {str(e)}")
        ]
