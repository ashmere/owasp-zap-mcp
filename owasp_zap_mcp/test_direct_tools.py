#!/usr/bin/env python3
"""
Direct test of OWASP ZAP MCP tools
Test the tools directly without SSE server complexity
"""

import asyncio
import logging
import os
import sys
from urllib.parse import urlparse

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from owasp_zap_mcp.tools.zap_tools import (
    mcp_zap_health_check,
    mcp_zap_spider_scan,
    mcp_zap_active_scan,
    mcp_zap_spider_status,
    mcp_zap_active_scan_status,
    mcp_zap_get_alerts,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def normalize_url(url_input: str) -> str:
    """
    Normalize URL to ensure it has proper protocol
    
    Args:
        url_input: URL in various formats (httpbin.org, https://httpbin.org, etc.)
        
    Returns:
        Normalized URL with protocol
    """
    if not url_input:
        return url_input
    
    url_input = url_input.strip()
    
    # If it already has a protocol, return as-is
    if url_input.startswith(('http://', 'https://')):
        return url_input
    
    # If it looks like a domain (contains . and no spaces), add https://
    if '.' in url_input and ' ' not in url_input and not url_input.startswith('/'):
        return f"https://{url_input}"
    
    # Otherwise, return as-is (might be invalid, but let ZAP handle it)
    return url_input

async def test_health_check():
    """Test ZAP health check"""
    logger.info("Testing ZAP health check...")
    try:
        result = await mcp_zap_health_check()
        logger.info(f"Health check result: {result}")
        return result
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return None

async def test_spider_scan(url: str):
    """Test spider scan with URL normalization"""
    normalized_url = normalize_url(url)
    logger.info(f"Testing spider scan for: {url} -> {normalized_url}")
    
    try:
        result = await mcp_zap_spider_scan(normalized_url, max_depth=3)
        logger.info(f"Spider scan result: {result}")
        return result
    except Exception as e:
        logger.error(f"Spider scan failed: {e}")
        return None

async def test_active_scan(url: str):
    """Test active scan with URL normalization"""
    normalized_url = normalize_url(url)
    logger.info(f"Testing active scan for: {url} -> {normalized_url}")
    
    try:
        result = await mcp_zap_active_scan(normalized_url)
        logger.info(f"Active scan result: {result}")
        return result
    except Exception as e:
        logger.error(f"Active scan failed: {e}")
        return None

async def test_scan_status(scan_id: str, scan_type: str = "spider"):
    """Test scan status check"""
    logger.info(f"Testing {scan_type} scan status for ID: {scan_id}")
    
    try:
        if scan_type == "spider":
            result = await mcp_zap_spider_status(scan_id)
        else:
            result = await mcp_zap_active_scan_status(scan_id)
        logger.info(f"Scan status result: {result}")
        return result
    except Exception as e:
        logger.error(f"Scan status check failed: {e}")
        return None

async def test_get_alerts():
    """Test getting alerts"""
    logger.info("Testing get alerts...")
    
    try:
        result = await mcp_zap_get_alerts()
        logger.info(f"Get alerts result: {result}")
        return result
    except Exception as e:
        logger.error(f"Get alerts failed: {e}")
        return None

async def main():
    """Main test function"""
    logger.info("Starting OWASP ZAP MCP Tools Direct Test")
    
    # Test different URL formats
    test_urls = [
        "httpbin.org",
        "https://httpbin.org",
        "http://httpbin.org",
        "httpbin.org/get",
        "https://httpbin.org/get"
    ]
    
    # 1. Test health check first
    health_result = await test_health_check()
    if not health_result:
        logger.error("ZAP health check failed - cannot proceed with tests")
        return
    
    # 2. Test URL normalization and spider scans
    logger.info("\n" + "="*50)
    logger.info("Testing URL normalization and spider scans")
    logger.info("="*50)
    
    spider_scan_ids = []
    for url in test_urls:
        logger.info(f"\nTesting URL: {url}")
        result = await test_spider_scan(url)
        if result and result.get('content'):
            try:
                import json
                content = json.loads(result['content'][0]['text'])
                if content.get('success') and content.get('scan_id'):
                    spider_scan_ids.append(content['scan_id'])
                    logger.info(f"Spider scan started with ID: {content['scan_id']}")
            except:
                pass
    
    # 3. Wait a bit and check scan statuses
    if spider_scan_ids:
        logger.info("\n" + "="*50)
        logger.info("Checking spider scan statuses")
        logger.info("="*50)
        
        await asyncio.sleep(5)  # Wait for scans to start
        
        for scan_id in spider_scan_ids:
            await test_scan_status(scan_id, "spider")
    
    # 4. Test active scan on one URL
    logger.info("\n" + "="*50)
    logger.info("Testing active scan")
    logger.info("="*50)
    
    test_url = "httpbin.org"
    active_result = await test_active_scan(test_url)
    active_scan_id = None
    
    if active_result and active_result.get('content'):
        try:
            import json
            content = json.loads(active_result['content'][0]['text'])
            if content.get('success') and content.get('scan_id'):
                active_scan_id = content['scan_id']
                logger.info(f"Active scan started with ID: {active_scan_id}")
        except:
            pass
    
    # 5. Check active scan status
    if active_scan_id:
        await asyncio.sleep(3)
        await test_scan_status(active_scan_id, "active")
    
    # 6. Test getting alerts
    logger.info("\n" + "="*50)
    logger.info("Testing get alerts")
    logger.info("="*50)
    
    await test_get_alerts()
    
    logger.info("\n" + "="*50)
    logger.info("Test completed!")
    logger.info("="*50)

if __name__ == "__main__":
    # Set environment variables for testing
    os.environ['ZAP_BASE_URL'] = 'http://localhost:8080'
    os.environ['ZAP_API_KEY'] = ''  # No API key for local testing
    
    asyncio.run(main()) 
