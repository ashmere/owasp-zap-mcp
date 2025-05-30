#!/usr/bin/env python3
"""
Manual Integration Test for OWASP ZAP MCP

This script performs manual integration testing of the MCP SSE Server
when the full environment is running. Use this for debugging and
manual verification of the MCP interface.

Prerequisites:
- ZAP container running on localhost:8080
- MCP server running on localhost:3000
- Both containers healthy and accessible

Usage:
    python scripts/manual-integration-test.py

To start the environment:
    ./scripts/start.sh
"""

import asyncio
import aiohttp
import json
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
BASE_URL = "http://localhost:3000"
SESSION_ID = f"manual_test_session_{int(asyncio.get_event_loop().time())}"

# Test targets (using realistic examples from our test suite)
TEST_TARGETS = [
    "httpbin.org",          # Known working test target
    "example.com",          # Simple test domain
    "api.github.com",       # API endpoint example
]


async def test_health_endpoint(session):
    """Test the health endpoint"""
    try:
        url = f"{BASE_URL}/health"
        logger.info(f"Testing health endpoint: {url}")

        async with session.get(url) as response:
            if response.status != 200:
                logger.error(f"Health endpoint returned {response.status}")
                return False

            result = await response.json()
            logger.info(f"Health check response: {json.dumps(result, indent=2)}")

            if result.get("status") == "healthy":
                logger.info("✅ Health endpoint is working")
                return True
            else:
                logger.error("❌ Health endpoint reports unhealthy status")
                return False

    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return False


async def test_status_endpoint(session):
    """Test the status endpoint and tool availability"""
    try:
        url = f"{BASE_URL}/status"
        logger.info(f"Testing status endpoint: {url}")

        async with session.get(url) as response:
            if response.status != 200:
                logger.error(f"Status endpoint returned {response.status}")
                return False

            result = await response.json()
            logger.info(f"Status response: {json.dumps(result, indent=2)}")

            tools = result.get("tools", [])
            if "zap_health_check" in tools:
                logger.info(f"✅ Found {len(tools)} tools including zap_health_check")
                return True
            else:
                logger.error("❌ zap_health_check tool not found in available tools")
                return False

    except Exception as e:
        logger.error(f"❌ Status check failed: {e}")
        return False


async def test_mcp_tool(session, tool_name, arguments=None):
    """Test calling an MCP tool via the /mcp/messages endpoint"""
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

    logger.info(f"🔧 Testing tool: {tool_name}")
    logger.info(f"   Arguments: {arguments}")

    try:
        async with session.post(url, params=params, json=payload) as response:
            if response.status != 200:
                logger.error(f"   ❌ HTTP {response.status}")
                return False

            result = await response.json()

            # Check for MCP success response
            if "result" in result:
                logger.info(f"   ✅ Tool executed successfully")

                # Parse the tool response if it's JSON
                try:
                    if "content" in result["result"]:
                        content = result["result"]["content"][0]["text"]
                        parsed_content = json.loads(content)
                        success = parsed_content.get("success", False)

                        if success:
                            logger.info(f"   ✅ Tool reports success")
                        else:
                            error = parsed_content.get("error", "Unknown error")
                            logger.warning(f"   ⚠️  Tool reports failure: {error}")

                except (json.JSONDecodeError, KeyError, IndexError):
                    logger.info(f"   ✅ Tool executed (content not JSON)")

                return True

            elif "error" in result:
                error_msg = result["error"].get("message", "Unknown error")
                logger.error(f"   ❌ MCP error: {error_msg}")
                return False

            else:
                logger.error(f"   ❌ Unexpected response format")
                logger.debug(f"   Response: {json.dumps(result, indent=2)}")
                return False

    except Exception as e:
        logger.error(f"   ❌ Exception: {e}")
        return False


async def run_comprehensive_test():
    """Run a comprehensive test of the MCP interface"""

    logger.info("🧪 Starting Manual Integration Test for OWASP ZAP MCP")
    logger.info("=" * 70)

    # Test configuration
    connector = aiohttp.TCPConnector(limit=10)
    timeout = aiohttp.ClientTimeout(total=30)

    async with aiohttp.ClientSession(
        connector=connector,
        timeout=timeout
    ) as session:

        test_results = []

        # Test 1: Health endpoint
        logger.info("\n1️⃣ Testing Health Endpoint")
        logger.info("-" * 40)
        health_ok = await test_health_endpoint(session)
        test_results.append(("Health Endpoint", health_ok))

        if not health_ok:
            logger.error("❌ Health check failed - stopping tests")
            return False

        # Test 2: Status endpoint
        logger.info("\n2️⃣ Testing Status Endpoint")
        logger.info("-" * 40)
        status_ok = await test_status_endpoint(session)
        test_results.append(("Status Endpoint", status_ok))

        if not status_ok:
            logger.error("❌ Status check failed - stopping tests")
            return False

        # Test 3: Basic MCP tool (no parameters)
        logger.info("\n3️⃣ Testing Basic MCP Tool")
        logger.info("-" * 40)
        basic_ok = await test_mcp_tool(session, "zap_health_check", {})
        test_results.append(("ZAP Health Check", basic_ok))

        # Test 4: MCP tools with URL normalization
        logger.info("\n4️⃣ Testing URL Normalization")
        logger.info("-" * 40)

        url_tests = []
        for target in TEST_TARGETS:
            logger.info(f"\n   Testing with target: {target}")

            # Test spider scan with random_string
            spider_ok = await test_mcp_tool(
                session,
                "zap_spider_scan",
                {"random_string": target}
            )
            url_tests.append(spider_ok)

            # Small delay between tests
            await asyncio.sleep(1)

        url_normalization_ok = all(url_tests)
        test_results.append(("URL Normalization", url_normalization_ok))

        # Test 5: Error handling
        logger.info("\n5️⃣ Testing Error Handling")
        logger.info("-" * 40)

        # Test with invalid tool name
        invalid_tool_ok = not await test_mcp_tool(
            session,
            "non_existent_tool",
            {}
        )  # Should fail, so we invert the result
        test_results.append(("Error Handling", invalid_tool_ok))

        # Test 6: Parameter processing
        logger.info("\n6️⃣ Testing Parameter Processing")
        logger.info("-" * 40)

        param_tests = []

        # Test scan summary with URL
        summary_ok = await test_mcp_tool(
            session,
            "zap_scan_summary",
            {"random_string": "httpbin.org"}
        )
        param_tests.append(summary_ok)

        # Test get alerts (no params needed)
        alerts_ok = await test_mcp_tool(session, "zap_get_alerts", {})
        param_tests.append(alerts_ok)

        param_processing_ok = all(param_tests)
        test_results.append(("Parameter Processing", param_processing_ok))

        # Print summary
        logger.info("\n🏁 Test Summary")
        logger.info("=" * 70)

        total_tests = len(test_results)
        passed_tests = sum(1 for _, result in test_results if result)

        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"   {test_name:<25} {status}")

        logger.info(f"\nResults: {passed_tests}/{total_tests} tests passed")

        if passed_tests == total_tests:
            logger.info("🎉 All tests passed! MCP integration is working correctly.")
            return True
        else:
            logger.error(f"❌ {total_tests - passed_tests} test(s) failed.")
            return False


async def main():
    """Main function"""

    # Check if script is being run from the right location
    script_path = Path(__file__)
    if script_path.parent.name != "scripts":
        logger.warning("⚠️  Script should be run from project root: python scripts/manual-integration-test.py")

    try:
        success = await run_comprehensive_test()

        if success:
            logger.info("\n✅ Manual integration test completed successfully!")
            sys.exit(0)
        else:
            logger.error("\n❌ Manual integration test failed!")
            logger.info("\n🔍 Troubleshooting:")
            logger.info("   1. Ensure ZAP container is running: docker compose ps")
            logger.info("   2. Ensure MCP server is running: curl http://localhost:3000/health")
            logger.info("   3. Check container logs: docker compose logs")
            logger.info("   4. Restart environment: ./scripts/rebuild.sh")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n💥 Unexpected error: {e}")
        logger.exception("Exception details:")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
