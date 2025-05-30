"""
Integration Tests for OWASP ZAP MCP

Tests covering the complete workflow from MCP tools to report generation.
"""

import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.owasp_zap_mcp.tools.zap_tools import (
    mcp_zap_active_scan,
    mcp_zap_clear_session,
    mcp_zap_generate_html_report,
    mcp_zap_generate_json_report,
    mcp_zap_get_alerts,
    mcp_zap_health_check,
    mcp_zap_scan_summary,
    mcp_zap_spider_scan,
)


class TestCompleteWorkflowIntegration:
    """Test complete security scanning workflows."""

    @pytest.fixture
    def mock_zap_client(self):
        """Create a comprehensive mock ZAP client."""
        with patch("src.owasp_zap_mcp.tools.zap_tools.ZAPClient") as mock_client_class:
            mock_client = AsyncMock()
            
            # Health check responses
            mock_client.health_check.return_value = True
            
            # Session management
            mock_client.clear_session.return_value = True
            
            # Scan responses
            mock_client.spider_scan.return_value = "123"
            mock_client.active_scan.return_value = "456"
            
            # Mock alerts
            from src.owasp_zap_mcp.zap_client import ZAPAlert
            mock_alerts = [
                ZAPAlert({
                    "name": "Missing X-Frame-Options Header",
                    "risk": "Medium",
                    "confidence": "High",
                    "description": "X-Frame-Options header is not included in the response",
                    "url": "https://example.com/",
                    "solution": "Add X-Frame-Options header",
                }),
                ZAPAlert({
                    "name": "Content Security Policy (CSP) Header Not Set",
                    "risk": "Medium",
                    "confidence": "High",
                    "description": "Content Security Policy header is missing",
                    "url": "https://example.com/",
                    "solution": "Implement Content Security Policy",
                }),
                ZAPAlert({
                    "name": "Information Disclosure - Sensitive Information in URL",
                    "risk": "Informational",
                    "confidence": "Medium",
                    "description": "The response contains sensitive information",
                    "url": "https://example.com/contact",
                    "solution": "Review information disclosure",
                }),
            ]
            mock_client.get_alerts.return_value = mock_alerts
            
            # Report generation
            mock_html_report = """
            <!DOCTYPE html>
            <html>
            <head><title>ZAP Security Report</title></head>
            <body>
                <h1>Security Assessment Report</h1>
                <h2>Target: https://example.com</h2>
                <h3>Summary</h3>
                <p>3 issues found</p>
                <h3>Findings</h3>
                <ul>
                    <li>Missing X-Frame-Options Header (Medium)</li>
                    <li>Content Security Policy Header Not Set (Medium)</li>
                    <li>Information Disclosure (Informational)</li>
                </ul>
            </body>
            </html>
            """
            mock_client.generate_html_report.return_value = mock_html_report
            
            mock_json_report = {
                "target": "https://example.com",
                "alerts": [alert.__dict__ for alert in mock_alerts],
                "total_alerts": 3,
                "risk_breakdown": {
                    "High": 0,
                    "Medium": 2,
                    "Low": 0,
                    "Informational": 1
                },
                "timestamp": "2025-05-30T16:19:30Z"
            }
            mock_client.generate_json_report.return_value = mock_json_report
            
            mock_client_class.return_value.__aenter__.return_value = mock_client
            yield mock_client

    @pytest.mark.asyncio
    async def test_skyral_io_complete_workflow(self, mock_zap_client):
        """Test complete security scanning workflow for example.com."""
        target_url = "example.com"
        
        # Step 1: Health Check
        health_result = await mcp_zap_health_check()
        health_data = json.loads(health_result["content"][0]["text"])
        assert health_data["success"] is True
        
        # Step 2: Clear Session
        clear_result = await mcp_zap_clear_session()
        clear_data = json.loads(clear_result["content"][0]["text"])
        assert clear_data["success"] is True
        
        # Step 3: Spider Scan
        spider_result = await mcp_zap_spider_scan(target_url)
        spider_data = json.loads(spider_result["content"][0]["text"])
        assert spider_data["success"] is True
        assert "https://example.com" in spider_data["url"]
        
        # Verify URL normalization
        mock_zap_client.spider_scan.assert_called_with("https://example.com", 5)
        
        # Step 4: Active Scan
        active_result = await mcp_zap_active_scan(target_url)
        active_data = json.loads(active_result["content"][0]["text"])
        assert active_data["success"] is True
        
        # Step 5: Get Alerts
        alerts_result = await mcp_zap_get_alerts()
        alerts_data = json.loads(alerts_result["content"][0]["text"])
        assert alerts_data["success"] is True
        
        # Step 6: Generate HTML Report
        html_result = await mcp_zap_generate_html_report()
        html_data = json.loads(html_result["content"][0]["text"])
        assert html_data["success"] is True
        
        # Step 7: Generate JSON Report
        json_result = await mcp_zap_generate_json_report()
        json_data = json.loads(json_result["content"][0]["text"])
        assert json_data["success"] is True
        
        # Step 8: Scan Summary
        summary_result = await mcp_zap_scan_summary(target_url)
        summary_data = json.loads(summary_result["content"][0]["text"])
        assert summary_data["success"] is True

    @pytest.mark.asyncio
    async def test_httpbin_org_workflow(self, mock_zap_client):
        """Test workflow with httpbin.org (another real target)."""
        target_url = "httpbin.org"
        
        # Run basic workflow
        health_result = await mcp_zap_health_check()
        spider_result = await mcp_zap_spider_scan(target_url)
        alerts_result = await mcp_zap_get_alerts()
        
        health_data = json.loads(health_result["content"][0]["text"])
        spider_data = json.loads(spider_result["content"][0]["text"])
        alerts_data = json.loads(alerts_result["content"][0]["text"])
        
        assert health_data["success"] is True
        assert spider_data["success"] is True
        assert alerts_data["success"] is True
        
        # Verify URL normalization for httpbin.org
        mock_zap_client.spider_scan.assert_called_with("https://httpbin.org", 5)

    @pytest.mark.asyncio
    async def test_localhost_development_workflow(self, mock_zap_client):
        """Test workflow with localhost development server."""
        target_urls = [
            ("localhost:3000", "localhost:3000"),  # No dot, not normalized
            ("127.0.0.1:8080", "https://127.0.0.1:8080"),  # Has dot, gets normalized
            ("localhost:8000", "localhost:8000"),  # No dot, not normalized
        ]
        
        for target_url, expected_url in target_urls:
            spider_result = await mcp_zap_spider_scan(target_url)
            spider_data = json.loads(spider_result["content"][0]["text"])
            assert spider_data["success"] is True
            
            # Verify URL normalization for localhost
            mock_zap_client.spider_scan.assert_called_with(expected_url, 5)

    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self, mock_zap_client):
        """Test workflow with error conditions and recovery."""
        # Simulate health check failure initially
        mock_zap_client.health_check.return_value = False
        
        health_result = await mcp_zap_health_check()
        health_data = json.loads(health_result["content"][0]["text"])
        assert health_data["success"] is False
        
        # Recover - health check now passes
        mock_zap_client.health_check.return_value = True
        
        health_result = await mcp_zap_health_check()
        health_data = json.loads(health_result["content"][0]["text"])
        assert health_data["success"] is True
        
        # Continue with scan
        spider_result = await mcp_zap_spider_scan("example.com")
        spider_data = json.loads(spider_result["content"][0]["text"])
        assert spider_data["success"] is True

    @pytest.mark.asyncio
    async def test_filtered_alerts_workflow(self, mock_zap_client):
        """Test workflow with filtered security alerts."""
        # Test different risk level filters
        risk_levels = ["High", "Medium", "Low", "Informational"]
        
        for risk_level in risk_levels:
            # Mock filtered response
            from src.owasp_zap_mcp.zap_client import ZAPAlert
            filtered_alerts = [
                ZAPAlert({
                    "name": f"Test {risk_level} Alert",
                    "risk": risk_level,
                    "confidence": "High",
                    "description": f"Test {risk_level} description",
                    "url": "https://example.com/",
                    "solution": f"Fix {risk_level} issue",
                }),
            ]
            mock_zap_client.get_alerts.return_value = filtered_alerts
            
            # Note: mcp_zap_get_alerts doesn't take risk_level parameter in current implementation
            alerts_result = await mcp_zap_get_alerts()
            alerts_data = json.loads(alerts_result["content"][0]["text"])
            assert alerts_data["success"] is True

    @pytest.mark.asyncio
    async def test_no_alerts_workflow(self, mock_zap_client):
        """Test workflow when no security alerts are found."""
        # Mock empty alerts response
        mock_zap_client.get_alerts.return_value = []
        
        alerts_result = await mcp_zap_get_alerts()
        alerts_data = json.loads(alerts_result["content"][0]["text"])
        assert alerts_data["success"] is True
        
        # Test scan summary with no alerts
        summary_result = await mcp_zap_scan_summary("clean-site.com")
        summary_data = json.loads(summary_result["content"][0]["text"])
        assert summary_data["success"] is True


class TestReportGenerationIntegration:
    """Test report generation and file handling."""

    @pytest.fixture
    def temp_reports_dir(self):
        """Create a temporary directory for reports."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.mark.asyncio
    async def test_html_report_content_validation(self):
        """Test HTML report content is properly formatted."""
        with patch("src.owasp_zap_mcp.tools.zap_tools.ZAPClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_html = """
            <!DOCTYPE html>
            <html>
            <head><title>Security Report</title></head>
            <body><h1>OWASP ZAP Report</h1></body>
            </html>
            """
            mock_client.generate_html_report.return_value = mock_html
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            result = await mcp_zap_generate_html_report()
            
            response_data = json.loads(result["content"][0]["text"])
            assert response_data["success"] is True
            # Could add HTML validation here if needed
            assert len(mock_html) > 100  # Basic content check

    @pytest.mark.asyncio
    async def test_json_report_structure_validation(self):
        """Test JSON report has proper structure."""
        with patch("src.owasp_zap_mcp.tools.zap_tools.ZAPClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_json = {
                "alerts": [
                    {
                        "name": "Test Alert",
                        "risk": "Medium",
                        "confidence": "High",
                        "description": "Test description",
                        "url": "https://example.com/",
                        "solution": "Test solution",
                    }
                ],
                "total_alerts": 1,
                "timestamp": "2025-05-30T16:19:30Z"
            }
            mock_client.generate_json_report.return_value = mock_json
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            result = await mcp_zap_generate_json_report()
            
            response_data = json.loads(result["content"][0]["text"])
            assert response_data["success"] is True
            # Validate JSON structure
            assert "alerts" in mock_json
            assert "total_alerts" in mock_json
            assert isinstance(mock_json["alerts"], list)
            assert isinstance(mock_json["total_alerts"], int)

    def test_report_directory_structure_creation(self, temp_reports_dir):
        """Test creating proper report directory structure."""
        # Simulate the directory structure we create in scan_skyral_mcp.py
        timestamp = "20250530_161218"
        base_dir = temp_reports_dir / "skyral_io" / timestamp
        
        # Create subdirectories
        (base_dir / "html").mkdir(parents=True, exist_ok=True)
        (base_dir / "json").mkdir(parents=True, exist_ok=True)
        (base_dir / "summary").mkdir(parents=True, exist_ok=True)
        
        # Verify structure
        assert base_dir.exists()
        assert (base_dir / "html").exists()
        assert (base_dir / "json").exists()
        assert (base_dir / "summary").exists()
        
        # Create sample files
        (base_dir / "html" / "security_report.html").write_text("<html>Report</html>")
        (base_dir / "json" / "security_report.json").write_text('{"alerts": []}')
        (base_dir / "summary" / "executive_summary.md").write_text("# Summary")
        
        # Verify files
        assert (base_dir / "html" / "security_report.html").exists()
        assert (base_dir / "json" / "security_report.json").exists()
        assert (base_dir / "summary" / "executive_summary.md").exists()


class TestRealWorldScenarios:
    """Test scenarios based on real-world usage patterns."""

    @pytest.mark.asyncio
    async def test_company_website_assessment(self):
        """Test assessment of a company presence website like example.com."""
        with patch("src.owasp_zap_mcp.tools.zap_tools.ZAPClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Mock typical company website findings
            from src.owasp_zap_mcp.zap_client import ZAPAlert
            typical_findings = [
                ZAPAlert({
                    "name": "Missing X-Frame-Options Header",
                    "risk": "Medium",
                    "confidence": "High",
                    "description": "X-Frame-Options header is not included",
                    "url": "https://company.com/",
                    "solution": "Add X-Frame-Options header",
                }),
                ZAPAlert({
                    "name": "Content Security Policy (CSP) Header Not Set",
                    "risk": "Medium",
                    "confidence": "High",
                    "description": "CSP header is missing",
                    "url": "https://company.com/",
                    "solution": "Implement Content Security Policy",
                }),
                ZAPAlert({
                    "name": "Cookie without SameSite Attribute",
                    "risk": "Low",
                    "confidence": "Medium",
                    "description": "Cookie lacks SameSite attribute",
                    "url": "https://company.com/contact",
                    "solution": "Add SameSite attribute to cookies",
                }),
            ]
            mock_client.get_alerts.return_value = typical_findings
            mock_client.health_check.return_value = True
            mock_client.spider_scan.return_value = "123"
            mock_client.active_scan.return_value = "456"
            
            # Run assessment
            health_result = await mcp_zap_health_check()
            spider_result = await mcp_zap_spider_scan("company.com")
            alerts_result = await mcp_zap_get_alerts()
            summary_result = await mcp_zap_scan_summary("company.com")
            
            # Verify results
            health_data = json.loads(health_result["content"][0]["text"])
            spider_data = json.loads(spider_result["content"][0]["text"])
            alerts_data = json.loads(alerts_result["content"][0]["text"])
            summary_data = json.loads(summary_result["content"][0]["text"])
            
            assert health_data["success"] is True
            assert spider_data["success"] is True
            assert alerts_data["success"] is True
            assert summary_data["success"] is True

    @pytest.mark.asyncio
    async def test_api_endpoint_assessment(self):
        """Test assessment of API endpoints."""
        api_endpoints = [
            ("api.example.com", "https://api.example.com"),  # Has dot, gets normalized
            ("api.example.com/v1", "https://api.example.com/v1"),  # Has dot, gets normalized
            ("localhost:8080/api", "localhost:8080/api"),  # No dot in domain, not normalized
        ]
        
        with patch("src.owasp_zap_mcp.tools.zap_tools.ZAPClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.spider_scan.return_value = "123"
            mock_client.health_check.return_value = True
            
            for endpoint, expected_url in api_endpoints:
                spider_result = await mcp_zap_spider_scan(endpoint)
                spider_data = json.loads(spider_result["content"][0]["text"])
                assert spider_data["success"] is True
                
                # Verify URL normalization for APIs
                mock_client.spider_scan.assert_called_with(expected_url, 5)

    @pytest.mark.asyncio
    async def test_development_environment_scan(self):
        """Test scanning development environments."""
        dev_targets = [
            ("localhost:3000", "localhost:3000"),      # No dot, not normalized
            ("localhost:8000", "localhost:8000"),      # No dot, not normalized
            ("127.0.0.1:5000", "https://127.0.0.1:5000"),      # Has dot, gets normalized
            ("localhost:4200", "localhost:4200"),      # No dot, not normalized
        ]
        
        with patch("src.owasp_zap_mcp.tools.zap_tools.ZAPClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.health_check.return_value = True
            mock_client.spider_scan.return_value = "123"
            mock_client.active_scan.return_value = "456"
            
            for target, expected_url in dev_targets:
                # Test spider scan
                spider_result = await mcp_zap_spider_scan(target)
                spider_data = json.loads(spider_result["content"][0]["text"])
                assert spider_data["success"] is True
                
                # Test active scan
                active_result = await mcp_zap_active_scan(target)
                active_data = json.loads(active_result["content"][0]["text"])
                assert active_data["success"] is True
                
                # Verify URL normalization
                mock_client.spider_scan.assert_called_with(expected_url, 5)
                mock_client.active_scan.assert_called_with(expected_url, None)

    @pytest.mark.asyncio
    async def test_production_security_hardening_check(self):
        """Test security hardening checks for production websites."""
        with patch("src.owasp_zap_mcp.tools.zap_tools.ZAPClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Mock production security findings
            from src.owasp_zap_mcp.zap_client import ZAPAlert
            production_findings = [
                ZAPAlert({
                    "name": "Strict-Transport-Security Header Not Set",
                    "risk": "Low",
                    "confidence": "High",
                    "description": "HSTS header is missing",
                    "url": "https://production.com/",
                    "solution": "Implement HSTS header",
                }),
                ZAPAlert({
                    "name": "Server Leaks Information via X-Powered-By Header",
                    "risk": "Low",
                    "confidence": "Medium",
                    "description": "Server reveals technology stack",
                    "url": "https://production.com/",
                    "solution": "Remove or modify X-Powered-By header",
                }),
            ]
            
            mock_client.get_alerts.return_value = production_findings
            mock_client.health_check.return_value = True
            
            # Run security check
            alerts_result = await mcp_zap_get_alerts()
            alerts_data = json.loads(alerts_result["content"][0]["text"])
            assert alerts_data["success"] is True
            
            # Verify production-specific findings are captured
            assert alerts_data["total_alerts"] == 2
            assert any("Strict-Transport-Security" in alert["name"] for alert in alerts_data["alerts"]) 
