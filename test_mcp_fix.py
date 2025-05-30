#!/usr/bin/env python3
"""
Test MCP SSE Server Parameter Processing Fixes
"""

import asyncio
import aiohttp
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:3000"
SESSION_ID = "test_fix_session"

async def test_mcp_tool(session, tool_name, arguments=None):
    """Test calling an MCP tool"""
    if arguments is None:
        arguments = {}
    
    url = f"{BASE_URL}/mcp/messages"
    params = {"session_id": SESSION_ID}
    
    payload = {
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        },
        "jsonrpc": "2.0",
        "id": 1
    }
    
    logger.info(f"Testing tool: {tool_name} with arguments: {arguments}")
    
    try:
        async with session.post(url, params=params, json=payload) as response:
            result = await response.json()
            logger.info(f"Response: {json.dumps(result, indent=2)}")
            return result
    except Exception as e:
        logger.error(f"Error calling {tool_name}: {e}")
        return None

async def test_health_endpoint(session):
    """Test the health endpoint"""
    try:
        async with session.get(f"{BASE_URL}/health") as response:
            result = await response.json()
            logger.info(f"Health check: {result}")
            return result.get("status") == "healthy"
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False

async def main():
    """Main test function"""
    logger.info("🧪 Testing MCP SSE Server Parameter Processing Fixes")
    logger.info("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Health endpoint
        logger.info("\n1️⃣ Testing health endpoint...")
        healthy = await test_health_endpoint(session)
        if not healthy:
            logger.error("❌ Health check failed!")
            return
        
        # Test 2: ZAP Health Check (no parameters)
        logger.info("\n2️⃣ Testing zap_health_check...")
        await test_mcp_tool(session, "zap_health_check", {})
        
        # Test 3: Spider Scan with random_string parameter
        logger.info("\n3️⃣ Testing zap_spider_scan with random_string...")
        await test_mcp_tool(session, "zap_spider_scan", {"random_string": "skyral.io"})
        
        # Test 4: Active Scan with random_string parameter
        logger.info("\n4️⃣ Testing zap_active_scan with random_string...")
        await test_mcp_tool(session, "zap_active_scan", {"random_string": "skyral.io"})
        
        # Test 5: Get Alerts (no parameters)
        logger.info("\n5️⃣ Testing zap_get_alerts...")
        await test_mcp_tool(session, "zap_get_alerts", {})
        
        # Test 6: Scan Summary with random_string parameter
        logger.info("\n6️⃣ Testing zap_scan_summary with random_string...")
        await test_mcp_tool(session, "zap_scan_summary", {"random_string": "skyral.io"})
    
    logger.info("\n🎉 MCP testing completed!")

if __name__ == "__main__":
    asyncio.run(main()) 
