#!/usr/bin/env python3
"""
Test OWASP ZAP MCP Tools via SSE Interface
Demonstrates URL normalization and comprehensive security scanning
"""

import asyncio
import json
import logging
import os
import sys
import time
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
    mcp_zap_scan_summary,
    normalize_url,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_url_normalization():
    """Test URL normalization with various formats"""
    logger.info("🔧 Testing URL Normalization")
    logger.info("=" * 50)
    
    test_cases = [
        "httpbin.org",
        "https://httpbin.org", 
        "http://httpbin.org",
        "httpbin.org/get",
        "https://httpbin.org/get",
        "skyral.io",
        "example.com",
        "https://example.com/path",
    ]
    
    for url in test_cases:
        normalized = normalize_url(url)
        status = "✅ NORMALIZED" if url != normalized else "➡️  UNCHANGED"
        logger.info(f"{status}: {url} → {normalized}")
    
    logger.info("")

async def test_comprehensive_scan(target_url: str):
    """Perform a comprehensive security scan of a target URL"""
    logger.info(f"🎯 Starting Comprehensive Security Scan for: {target_url}")
    logger.info("=" * 70)
    
    # 1. Health Check
    logger.info("1️⃣  ZAP Health Check...")
    health_result = await mcp_zap_health_check()
    health_data = json.loads(health_result['content'][0]['text'])
    if not health_data.get('success'):
        logger.error("❌ ZAP health check failed!")
        return False
    logger.info(f"✅ {health_data['message']}")
    
    # 2. Spider Scan
    logger.info(f"\n2️⃣  Starting Spider Scan for {target_url}...")
    spider_result = await mcp_zap_spider_scan(target_url, max_depth=3)
    spider_data = json.loads(spider_result['content'][0]['text'])
    
    if not spider_data.get('success'):
        logger.error(f"❌ Spider scan failed: {spider_data.get('error')}")
        return False
    
    spider_scan_id = spider_data['scan_id']
    normalized_url = spider_data['url']
    original_url = spider_data.get('original_url')
    
    if original_url:
        logger.info(f"🔄 URL normalized: {original_url} → {normalized_url}")
    
    logger.info(f"✅ Spider scan started with ID: {spider_scan_id}")
    
    # 3. Monitor Spider Scan Progress
    logger.info(f"\n3️⃣  Monitoring Spider Scan Progress...")
    max_wait = 30  # seconds
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        status_result = await mcp_zap_spider_status(spider_scan_id)
        status_data = json.loads(status_result['content'][0]['text'])
        
        if status_data.get('success'):
            progress = status_data['progress']
            status = status_data['status']
            logger.info(f"🕷️  Spider Scan: {status} ({progress}% complete)")
            
            if status == "FINISHED":
                logger.info("✅ Spider scan completed!")
                break
        
        await asyncio.sleep(3)
    
    # 4. Active Scan
    logger.info(f"\n4️⃣  Starting Active Security Scan for {normalized_url}...")
    active_result = await mcp_zap_active_scan(normalized_url)
    active_data = json.loads(active_result['content'][0]['text'])
    
    if not active_data.get('success'):
        logger.error(f"❌ Active scan failed: {active_data.get('error')}")
    else:
        active_scan_id = active_data['scan_id']
        logger.info(f"✅ Active scan started with ID: {active_scan_id}")
        
        # Brief status check
        await asyncio.sleep(5)
        active_status_result = await mcp_zap_active_scan_status(active_scan_id)
        active_status_data = json.loads(active_status_result['content'][0]['text'])
        if active_status_data.get('success'):
            logger.info(f"🔍 Active Scan: {active_status_data['status']} ({active_status_data['progress']}% complete)")
    
    # 5. Get Security Alerts
    logger.info(f"\n5️⃣  Retrieving Security Alerts...")
    alerts_result = await mcp_zap_get_alerts()
    alerts_data = json.loads(alerts_result['content'][0]['text'])
    
    if alerts_data.get('success'):
        total_alerts = alerts_data['total_alerts']
        displayed_alerts = alerts_data['displayed_alerts']
        logger.info(f"🚨 Found {total_alerts} total security alerts (showing {displayed_alerts})")
        
        # Show top 3 alerts
        for i, alert in enumerate(alerts_data['alerts'][:3], 1):
            logger.info(f"   {i}. {alert['name']} ({alert['risk']} risk)")
            logger.info(f"      URL: {alert['url']}")
    
    # 6. Scan Summary
    logger.info(f"\n6️⃣  Generating Scan Summary...")
    summary_result = await mcp_zap_scan_summary(target_url)
    summary_data = json.loads(summary_result['content'][0]['text'])
    
    if summary_data.get('success'):
        risk_summary = summary_data['risk_summary']
        total_issues = summary_data['total_issues']
        logger.info(f"📊 Security Summary for {summary_data['url']}:")
        logger.info(f"   Total Issues: {total_issues}")
        logger.info(f"   High Risk: {risk_summary['High']}")
        logger.info(f"   Medium Risk: {risk_summary['Medium']}")
        logger.info(f"   Low Risk: {risk_summary['Low']}")
        logger.info(f"   Informational: {risk_summary['Informational']}")
    
    logger.info(f"\n✅ Comprehensive scan completed for {target_url}")
    return True

async def main():
    """Main test function"""
    logger.info("🚀 OWASP ZAP MCP Tools - Comprehensive Test Suite")
    logger.info("=" * 70)
    
    # Set environment variables
    os.environ['ZAP_BASE_URL'] = 'http://localhost:8080'
    os.environ['ZAP_API_KEY'] = ''
    
    # Test URL normalization
    await test_url_normalization()
    
    # Test different URL formats
    test_targets = [
        "httpbin.org",
        "httpbin.org/get",
    ]
    
    for target in test_targets:
        try:
            await test_comprehensive_scan(target)
            logger.info("\n" + "=" * 70 + "\n")
        except Exception as e:
            logger.error(f"❌ Test failed for {target}: {e}")
    
    logger.info("🎉 All tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 
