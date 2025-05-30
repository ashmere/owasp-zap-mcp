"""
Pytest configuration and shared fixtures for OWASP ZAP MCP tests.
"""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_zap_client_factory():
    """Factory for creating mock ZAP clients with different configurations."""
    def _create_mock_client(
        health_status=True,
        spider_scan_id="123",
        active_scan_id="456",
        alerts=None,
        html_report="<html>Test Report</html>",
        json_report=None
    ):
        mock_client = AsyncMock()
        
        # Basic responses
        mock_client.health_check.return_value = health_status
        mock_client.clear_session.return_value = True
        mock_client.spider_scan.return_value = spider_scan_id
        mock_client.active_scan.return_value = active_scan_id
        
        # Alerts
        if alerts is None:
            from src.owasp_zap_mcp.zap_client import ZAPAlert
            alerts = [
                ZAPAlert({
                    "name": "Test Alert",
                    "risk": "Medium",
                    "confidence": "High",
                    "description": "Test description",
                    "url": "https://example.com/",
                    "solution": "Test solution",
                }),
            ]
        mock_client.get_alerts.return_value = alerts
        
        # Reports
        mock_client.generate_html_report.return_value = html_report
        
        if json_report is None:
            json_report = {
                "alerts": [alert.__dict__ for alert in alerts],
                "total_alerts": len(alerts),
                "timestamp": "2025-05-30T16:19:30Z"
            }
        mock_client.generate_json_report.return_value = json_report
        
        # Scan status
        from src.owasp_zap_mcp.zap_client import ZAPScanStatus
        mock_client.get_spider_status.return_value = ZAPScanStatus(status="FINISHED", progress=100)
        mock_client.get_active_scan_status.return_value = ZAPScanStatus(status="FINISHED", progress=100)
        
        return mock_client
    
    return _create_mock_client


@pytest.fixture
def temp_reports_directory():
    """Create a temporary directory for test reports."""
    with tempfile.TemporaryDirectory() as temp_dir:
        reports_dir = Path(temp_dir) / "test_reports"
        reports_dir.mkdir(exist_ok=True)
        yield reports_dir


@pytest.fixture
def sample_security_alerts():
    """Provide sample security alerts for testing."""
    from src.owasp_zap_mcp.zap_client import ZAPAlert
    
    return [
        ZAPAlert({
            "name": "Missing X-Frame-Options Header",
            "risk": "Medium",
            "confidence": "High",
            "description": "X-Frame-Options header is not included in the response",
            "url": "https://skyral.io/",
            "solution": "Add X-Frame-Options header",
        }),
        ZAPAlert({
            "name": "Content Security Policy (CSP) Header Not Set",
            "risk": "Medium",
            "confidence": "High",
            "description": "Content Security Policy header is missing",
            "url": "https://skyral.io/",
            "solution": "Implement Content Security Policy",
        }),
        ZAPAlert({
            "name": "Information Disclosure - Sensitive Information in URL",
            "risk": "Informational",
            "confidence": "Medium",
            "description": "The response contains sensitive information",
            "url": "https://skyral.io/contact",
            "solution": "Review information disclosure",
        }),
        ZAPAlert({
            "name": "Strict-Transport-Security Header Not Set",
            "risk": "Low",
            "confidence": "High",
            "description": "HSTS header is missing",
            "url": "https://skyral.io/",
            "solution": "Implement HSTS header",
        }),
    ]


@pytest.fixture
def url_normalization_test_cases():
    """Provide test cases for URL normalization."""
    return [
        ("skyral.io", "https://skyral.io"),
        ("httpbin.org", "https://httpbin.org"),
        ("api.example.com", "https://api.example.com"),
        ("localhost:3000", "https://localhost:3000"),
        ("127.0.0.1:8080", "https://127.0.0.1:8080"),
        ("example.com/api/v1", "https://example.com/api/v1"),
        ("https://already-https.com", "https://already-https.com"),
        ("http://keep-http.com", "http://keep-http.com"),
        ("", ""),
        (None, ""),
    ]


@pytest.fixture
def mock_mcp_server():
    """Create a mock MCP server for testing."""
    mock_server = MagicMock()
    mock_server.name = "owasp-zap-mcp"
    
    # Mock tools
    mock_tool = MagicMock()
    mock_tool.name = "zap_health_check"
    mock_tool.description = "Check ZAP health"
    mock_tool.parameters = {"type": "object", "properties": {}, "required": []}
    
    mock_server.list_tools = AsyncMock(return_value=[mock_tool])
    return mock_server


@pytest.fixture
def realistic_scan_results():
    """Provide realistic scan results based on our skyral.io testing."""
    return {
        "target_url": "skyral.io",
        "normalized_url": "https://skyral.io",
        "spider_scan_id": "123",
        "active_scan_id": "456",
        "total_alerts": 3,
        "risk_breakdown": {
            "High": 0,
            "Medium": 2,
            "Low": 0,
            "Informational": 1
        },
        "scan_duration_minutes": 7,
        "common_findings": [
            "Missing X-Frame-Options Header",
            "Content Security Policy (CSP) Header Not Set",
            "Information Disclosure"
        ]
    }


# Test markers for categorizing tests
pytest_plugins = []

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "mcp: mark test as testing MCP functionality"
    )
    config.addinivalue_line(
        "markers", "sse: mark test as testing SSE server functionality"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "real_world: mark test as testing real-world scenarios"
    ) 
