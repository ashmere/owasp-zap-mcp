#!/usr/bin/env python3
"""
Test script for MCP parameter processing
"""
import asyncio
import sys

sys.path.append("/app")

from owasp_zap_mcp.tools.zap_tools import (
    mcp_zap_clear_session,
    mcp_zap_health_check,
    mcp_zap_spider_scan,
)


async def test_mcp_tools():
    print("=== Testing MCP Tools with Parameter Processing ===")

    # Test 1: Health check (no parameters needed)
    print("\n1. Testing health check...")
    try:
        result = await mcp_zap_health_check()
        print(f"✅ Health check: {result}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")

    # Test 2: Clear session (no parameters needed)
    print("\n2. Testing clear session...")
    try:
        result = await mcp_zap_clear_session()
        print(f"✅ Clear session: {result}")
    except Exception as e:
        print(f"❌ Clear session failed: {e}")

    # Test 3: Spider scan with URL parameter
    print("\n3. Testing spider scan with URL parameter...")
    try:
        result = await mcp_zap_spider_scan(url="https://skyral.io")
        print(f"✅ Spider scan started: {result}")
    except Exception as e:
        print(f"❌ Spider scan failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_mcp_tools())
