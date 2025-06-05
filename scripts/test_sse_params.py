#!/usr/bin/env python3
"""
Test script for SSE server parameter processing with random_string fallback
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../owasp_zap_mcp/src')))
# The above ensures imports work with src layout, regardless of CWD.

from fastapi import FastAPI, Request

from owasp_zap_mcp.mcp_core import stdio_mcp
from owasp_zap_mcp.sse_server import ZAPMCPSseServer


class MockRequest:
    """Mock request object for testing"""

    def __init__(self, body_data=None):
        self._body = body_data
        self._json = {}
        self.headers = {}
        self.query_params = {}


async def test_sse_parameter_processing():
    print("=== Testing SSE Server Parameter Processing ===")

    # Register tools first
    from owasp_zap_mcp.tools.tool_initializer import register_mcp_tools

    await register_mcp_tools(stdio_mcp)

    # Create mock FastAPI app and SSE server
    mock_app = FastAPI()
    sse_server = ZAPMCPSseServer(stdio_mcp, mock_app)

    # Test 1: Health check with random_string (should work)
    print("\n1. Testing health check with random_string...")
    try:
        mock_request = MockRequest()
        result = await sse_server.call_tool(
            "zap_health_check", {"random_string": "test"}, mock_request
        )
        print(f"✅ Health check: {result}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")

    # Test 2: Clear session with random_string (should work)
    print("\n2. Testing clear session with random_string...")
    try:
        mock_request = MockRequest()
        result = await sse_server.call_tool(
            "zap_clear_session", {"random_string": "test"}, mock_request
        )
        print(f"✅ Clear session: {result}")
    except Exception as e:
        print(f"❌ Clear session failed: {e}")

    # Test 3: Spider scan with URL in random_string (should extract URL)
    print("\n3. Testing spider scan with URL in random_string...")
    try:
        mock_request = MockRequest()
        result = await sse_server.call_tool(
            "zap_spider_scan", {"random_string": "https://example.com"}, mock_request
        )
        print(f"✅ Spider scan with URL extraction: {result}")
    except Exception as e:
        print(f"❌ Spider scan failed: {e}")

    # Test 4: Spider scan with domain in random_string (should add https://)
    print("\n4. Testing spider scan with domain in random_string...")
    try:
        mock_request = MockRequest()
        result = await sse_server.call_tool(
            "zap_spider_scan", {"random_string": "example.com"}, mock_request
        )
        print(f"✅ Spider scan with domain conversion: {result}")
    except Exception as e:
        print(f"❌ Spider scan failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_sse_parameter_processing())
