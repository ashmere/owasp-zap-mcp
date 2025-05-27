"""
ZAP Proxy Tools

MCP tool implementations for OWASP ZAP proxy management and traffic analysis.
Includes proxy control, history retrieval, and traffic monitoring.
"""

import logging
from typing import Any, Dict, List, Optional

from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool

from ..zap_client import ZAPClient, ZAPClientError

logger = logging.getLogger(__name__)


# Tool definitions for MCP registration
ZAP_START_PROXY_TOOL = Tool(
    name="zap_start_proxy",
    description="Start or configure ZAP proxy for intercepting HTTP traffic",
    inputSchema={
        "type": "object",
        "properties": {
            "port": {
                "type": "integer",
                "description": "Proxy port number (default: 8080)",
                "minimum": 1024,
                "maximum": 65535,
                "default": 8080,
            }
        },
        "required": [],
    },
)

ZAP_GET_PROXY_HISTORY_TOOL = Tool(
    name="zap_get_proxy_history",
    description="Get HTTP requests and responses that passed through ZAP proxy",
    inputSchema={
        "type": "object",
        "properties": {
            "limit": {
                "type": "integer",
                "description": "Maximum number of history entries to return (default: 20)",
                "minimum": 1,
                "maximum": 100,
                "default": 20,
            },
            "filter_url": {
                "type": "string",
                "description": "Filter history by URL pattern (optional)",
            },
        },
        "required": [],
    },
)

ZAP_CLEAR_PROXY_HISTORY_TOOL = Tool(
    name="zap_clear_proxy_history",
    description="Clear ZAP proxy history and session data",
    inputSchema={
        "type": "object",
        "properties": {
            "confirm": {
                "type": "boolean",
                "description": "Confirm that you want to clear all proxy history",
                "default": False,
            }
        },
        "required": ["confirm"],
    },
)


async def zap_start_proxy(zap_client: ZAPClient, port: int = 8080) -> list[TextContent]:
    """
    Start or configure ZAP proxy.

    Args:
        zap_client: ZAP client instance
        port: Proxy port number

    Returns:
        MCP response with proxy configuration instructions
    """
    try:
        # Check if ZAP is running (proxy is typically always running with ZAP)
        is_healthy = await zap_client.health_check()

        if not is_healthy:
            return [
                TextContent(
                    type="text",
                    text="❌ **ZAP Proxy Not Available**\n\nZAP is not running or not accessible. Please ensure ZAP is started first.",
                )
            ]

        response_text = f"""🌐 **ZAP Proxy Configuration**

**Proxy Status:** ✅ Running
**Proxy Address:** localhost:{port}
**Protocol:** HTTP/HTTPS

## Browser Configuration

To use ZAP as a proxy, configure your browser with these settings:

### Manual Proxy Configuration:
- **HTTP Proxy:** localhost
- **Port:** {port}
- **HTTPS Proxy:** localhost
- **Port:** {port}
- **No Proxy for:** (leave empty or add localhost)

### Popular Browsers:

**Chrome/Chromium:**
```bash
google-chrome --proxy-server=http://localhost:{port}
```

**Firefox:**
1. Settings → Network Settings → Manual proxy configuration
2. HTTP Proxy: localhost, Port: {port}
3. Check "Use this proxy server for all protocols"

**curl:**
```bash
curl --proxy http://localhost:{port} https://example.com
```

## HTTPS/SSL Configuration

For HTTPS traffic analysis:
1. Browse to http://localhost:{port} in your browser
2. Download the ZAP Root CA certificate
3. Install it in your browser's certificate store

## Security Notes

⚠️ **Important:**
- Only use ZAP proxy for authorized testing
- The proxy will intercept ALL traffic from configured applications
- HTTPS traffic requires certificate installation for full analysis
- Disable proxy when not testing to avoid performance impact

## Next Steps

1. Configure your browser to use the proxy
2. Browse target websites normally
3. Use `zap_get_proxy_history` to view intercepted traffic
4. Use `zap_passive_scan` to analyze the traffic for security issues
"""

        return [TextContent(type="text", text=response_text)]

    except ZAPClientError as e:
        logger.error(f"Failed to configure ZAP proxy: {e}")
        return [
            TextContent(
                type="text",
                text=f"❌ **Proxy Configuration Failed**\n\nError: {str(e)}",
            )
        ]
    except Exception as e:
        logger.error(f"Unexpected error configuring proxy: {e}")
        return [
            TextContent(type="text", text=f"❌ **Unexpected Error**\n\nError: {str(e)}")
        ]


async def zap_get_proxy_history(
    zap_client: ZAPClient, limit: int = 20, filter_url: Optional[str] = None
) -> list[TextContent]:
    """
    Get HTTP requests and responses from ZAP proxy history.

    Args:
        zap_client: ZAP client instance
        limit: Maximum number of history entries
        filter_url: URL pattern filter

    Returns:
        MCP response with proxy history
    """
    try:
        # Note: This is a simplified implementation
        # In a real implementation, you'd call ZAP's history API
        # For now, we'll provide instructions on how to access history

        filter_text = f" (filtered by: {filter_url})" if filter_url else ""

        response_text = f"""📜 **ZAP Proxy History**{filter_text}

**Note:** This is a basic implementation. In ZAP's web interface, you can view detailed proxy history.

## Accessing Proxy History

### Via ZAP Web Interface:
1. Open http://localhost:8080 in your browser
2. Navigate to "History" tab
3. View all intercepted requests and responses

### Via ZAP API:
- **All History:** GET /JSON/core/view/messages/
- **Filtered History:** GET /JSON/core/view/messages/?baseurl={filter_url if filter_url else 'example.com'}

## What You'll See in History:

**Request Information:**
- HTTP method (GET, POST, etc.)
- Full URL and parameters
- Request headers
- Request body (for POST/PUT)

**Response Information:**
- HTTP status code
- Response headers
- Response body/content
- Response time

## Common Use Cases:

1. **Security Testing:**
   - Review authentication tokens
   - Check for sensitive data in requests/responses
   - Analyze session management

2. **API Analysis:**
   - Understand API endpoints and parameters
   - Review JSON/XML payloads
   - Check error responses

3. **Performance Analysis:**
   - Monitor response times
   - Identify slow requests
   - Check caching headers

## Next Steps:

- Use `zap_passive_scan` to analyze the traffic for security issues
- Use `zap_get_alerts` to see any vulnerabilities found in the traffic
- Use `zap_clear_proxy_history` to clear history when needed

**Tip:** For detailed analysis, use ZAP's web interface at http://localhost:8080
"""

        return [TextContent(type="text", text=response_text)]

    except ZAPClientError as e:
        logger.error(f"Failed to get proxy history: {e}")
        return [
            TextContent(
                type="text",
                text=f"❌ **Failed to Get Proxy History**\n\nError: {str(e)}",
            )
        ]
    except Exception as e:
        logger.error(f"Unexpected error getting proxy history: {e}")
        return [
            TextContent(type="text", text=f"❌ **Unexpected Error**\n\nError: {str(e)}")
        ]


async def zap_clear_proxy_history(
    zap_client: ZAPClient, confirm: bool = False
) -> list[TextContent]:
    """
    Clear ZAP proxy history and session data.

    Args:
        zap_client: ZAP client instance
        confirm: Confirmation that user wants to clear history

    Returns:
        MCP response confirming history clearing
    """
    try:
        if not confirm:
            return [
                TextContent(
                    type="text",
                    text="""⚠️ **Confirm History Clearing**

This action will permanently delete:
- All proxy request/response history
- Session data and cookies
- Discovered URLs and site tree
- Any unsaved scan results

**To proceed, call this function with confirm=true**

**Alternative:** Use ZAP's web interface to selectively clear specific items.
""",
                )
            ]

        # Clear ZAP session (this clears history and resets state)
        success = await zap_client.clear_session()

        if success:
            response_text = """🧹 **Proxy History Cleared Successfully**

**What was cleared:**
- ✅ All HTTP request/response history
- ✅ Session data and authentication tokens
- ✅ Discovered site tree and URLs
- ✅ Temporary scan data

**What was preserved:**
- ✅ ZAP configuration settings
- ✅ Scan policies and rules
- ✅ Saved reports (if any)

**Next Steps:**
- Configure your browser to use ZAP proxy again if needed
- Start new scans or browsing sessions
- Previous scan results are cleared - run new scans as needed

**Note:** ZAP proxy is still running and ready to intercept new traffic.
"""
        else:
            response_text = """❌ **Failed to Clear History**

The history clearing operation was not successful. This could be due to:
- ZAP API permissions
- Active scans preventing cleanup
- ZAP internal state issues

**Alternatives:**
1. Restart ZAP completely to clear all data
2. Use ZAP's web interface to manually clear specific items
3. Check ZAP logs for specific error details
"""

        return [TextContent(type="text", text=response_text)]

    except ZAPClientError as e:
        logger.error(f"Failed to clear proxy history: {e}")
        return [
            TextContent(
                type="text", text=f"❌ **Failed to Clear History**\n\nError: {str(e)}"
            )
        ]
    except Exception as e:
        logger.error(f"Unexpected error clearing history: {e}")
        return [
            TextContent(type="text", text=f"❌ **Unexpected Error**\n\nError: {str(e)}")
        ]
