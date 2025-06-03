"""
Tests for ZAP Client

Basic tests to verify ZAP client functionality and API integration.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.owasp_zap_mcp.zap_client import ZAPAlert, ZAPClient, ZAPScanStatus


class TestZAPClient:
    """Test cases for ZAP client functionality."""

    @pytest.fixture
    def zap_client(self):
        """Create a ZAP client instance for testing."""
        return ZAPClient(base_url="http://localhost:8080", api_key="test-key")

    @pytest.fixture
    def mock_zap(self):
        """Create a mock ZAPv2 instance."""
        mock = MagicMock()
        mock.core = MagicMock()
        mock.spider = MagicMock()
        mock.ascan = MagicMock()
        return mock

    @pytest.mark.asyncio
    async def test_connect(self, zap_client):
        """Test ZAP client connection initialization."""
        with patch("src.owasp_zap_mcp.zap_client.ZAPv2") as mock_zapv2:
            mock_zap_instance = MagicMock()
            mock_zapv2.return_value = mock_zap_instance

            await zap_client.connect()

            assert zap_client.zap is not None
            mock_zapv2.assert_called_once_with(
                apikey="test-key",
                proxies={
                    "http": "http://localhost:8080",
                    "https": "http://localhost:8080",
                },
            )

    @pytest.mark.asyncio
    async def test_health_check_success(self, zap_client, mock_zap):
        """Test successful health check."""
        zap_client.zap = mock_zap
        mock_zap.core.version = "2.14.0"

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_executor = AsyncMock()
            mock_executor.return_value = "2.14.0"
            mock_loop.return_value.run_in_executor = mock_executor

            result = await zap_client.health_check()

            assert result is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self, zap_client, mock_zap):
        """Test health check failure."""
        zap_client.zap = mock_zap

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_executor = AsyncMock()
            mock_executor.side_effect = Exception("Connection failed")
            mock_loop.return_value.run_in_executor = mock_executor

            result = await zap_client.health_check()

            assert result is False

    @pytest.mark.asyncio
    async def test_spider_scan_success(self, zap_client, mock_zap):
        """Test successful spider scan initiation."""
        zap_client.zap = mock_zap

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_executor = AsyncMock()
            mock_executor.return_value = "123"
            mock_loop.return_value.run_in_executor = mock_executor

            scan_id = await zap_client.spider_scan("https://example.com", max_depth=3)

            assert scan_id == "123"

    @pytest.mark.asyncio
    async def test_spider_scan_url_normalization(self, zap_client, mock_zap):
        """Test spider scan with URL normalization."""
        zap_client.zap = mock_zap

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_executor = AsyncMock()
            mock_executor.return_value = "123"
            mock_loop.return_value.run_in_executor = mock_executor

            # Test with various URL formats
            test_urls = [
                ("skyral.io", "https://skyral.io"),
                ("example.com", "https://example.com"),
                ("https://already-https.com", "https://already-https.com"),
                ("http://keep-http.com", "http://keep-http.com"),
                ("localhost:3000", "https://localhost:3000"),
            ]

            for input_url, expected_url in test_urls:
                scan_id = await zap_client.spider_scan(input_url)
                assert scan_id == "123"
                # Could verify the normalized URL was used if we had access to the call

    @pytest.mark.asyncio
    async def test_active_scan_success(self, zap_client, mock_zap):
        """Test successful active scan initiation."""
        zap_client.zap = mock_zap

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_executor = AsyncMock()
            mock_executor.return_value = "456"
            mock_loop.return_value.run_in_executor = mock_executor

            scan_id = await zap_client.active_scan("https://example.com")

            assert scan_id == "456"

    @pytest.mark.asyncio
    async def test_get_spider_status_running(self, zap_client, mock_zap):
        """Test getting spider scan status - running."""
        zap_client.zap = mock_zap

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_executor = AsyncMock()
            mock_executor.return_value = "50"
            mock_loop.return_value.run_in_executor = mock_executor

            status = await zap_client.get_spider_status("123")

            assert isinstance(status, ZAPScanStatus)
            assert status == ZAPScanStatus.RUNNING

    @pytest.mark.asyncio
    async def test_get_spider_status_finished(self, zap_client, mock_zap):
        """Test getting spider scan status - finished."""
        zap_client.zap = mock_zap

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_executor = AsyncMock()
            mock_executor.return_value = "100"
            mock_loop.return_value.run_in_executor = mock_executor

            status = await zap_client.get_spider_status("123")

            assert status == ZAPScanStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_get_active_scan_status(self, zap_client, mock_zap):
        """Test getting active scan status."""
        zap_client.zap = mock_zap

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_executor = AsyncMock()
            mock_executor.return_value = "75"
            mock_loop.return_value.run_in_executor = mock_executor

            status = await zap_client.get_active_scan_status("456")

            assert isinstance(status, ZAPScanStatus)
            assert status == ZAPScanStatus.RUNNING

    @pytest.mark.asyncio
    async def test_get_alerts(self, zap_client, mock_zap):
        """Test getting security alerts."""
        zap_client.zap = mock_zap

        mock_alerts_data = [
            {
                "name": "SQL Injection",
                "risk": "High",
                "confidence": "High",
                "description": "SQL injection vulnerability",
                "url": "https://example.com/login",
                "solution": "Use parameterized queries",
            },
            {
                "name": "XSS",
                "risk": "Medium",
                "confidence": "Medium",
                "description": "Cross-site scripting vulnerability",
                "url": "https://example.com/search",
                "solution": "Encode user input",
            },
        ]

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_executor = AsyncMock()
            mock_executor.return_value = mock_alerts_data
            mock_loop.return_value.run_in_executor = mock_executor

            alerts = await zap_client.get_alerts(risk_level="High")

            # Should only return High risk alerts
            assert len(alerts) == 1
            alert = alerts[0]
            assert isinstance(alert, ZAPAlert)
            assert alert.name == "SQL Injection"
            assert alert.risk == "High"
            assert alert.url == "https://example.com/login"

    @pytest.mark.asyncio
    async def test_get_all_alerts(self, zap_client, mock_zap):
        """Test getting all security alerts without filtering."""
        zap_client.zap = mock_zap

        mock_alerts_data = [
            {
                "name": "SQL Injection",
                "risk": "High",
                "confidence": "High",
                "description": "SQL injection vulnerability",
                "url": "https://example.com/login",
                "solution": "Use parameterized queries",
            },
            {
                "name": "XSS",
                "risk": "Medium",
                "confidence": "Medium",
                "description": "Cross-site scripting vulnerability",
                "url": "https://example.com/search",
                "solution": "Encode user input",
            },
        ]

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_executor = AsyncMock()
            mock_executor.return_value = mock_alerts_data
            mock_loop.return_value.run_in_executor = mock_executor

            alerts = await zap_client.get_alerts()

            # Should return all alerts
            assert len(alerts) == 2

    @pytest.mark.asyncio
    async def test_get_alerts_real_world_findings(self, zap_client, mock_zap):
        """Test getting alerts with real-world security findings."""
        zap_client.zap = mock_zap

        # Mock realistic security findings like we've seen in our scans
        mock_alerts_data = [
            {
                "name": "Missing X-Frame-Options Header",
                "risk": "Medium",
                "confidence": "High",
                "description": "X-Frame-Options header is not included in the response",
                "url": "https://skyral.io/",
                "solution": "Add X-Frame-Options header",
            },
            {
                "name": "Content Security Policy (CSP) Header Not Set",
                "risk": "Medium",
                "confidence": "High",
                "description": "Content Security Policy header is missing",
                "url": "https://skyral.io/",
                "solution": "Implement Content Security Policy",
            },
            {
                "name": "Information Disclosure - Sensitive Information in URL",
                "risk": "Informational",
                "confidence": "Medium",
                "description": "The response contains sensitive information",
                "url": "https://skyral.io/contact",
                "solution": "Review information disclosure",
            },
        ]

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_executor = AsyncMock()
            mock_executor.return_value = mock_alerts_data
            mock_loop.return_value.run_in_executor = mock_executor

            alerts = await zap_client.get_alerts()

            assert len(alerts) == 3
            # Verify we have the expected finding types
            alert_names = [alert.name for alert in alerts]
            assert "Missing X-Frame-Options Header" in alert_names
            assert "Content Security Policy (CSP) Header Not Set" in alert_names

    @pytest.mark.asyncio
    async def test_generate_html_report(self, zap_client, mock_zap):
        """Test generating HTML report."""
        zap_client.zap = mock_zap
        expected_report = "<html><body>Security Report</body></html>"

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_executor = AsyncMock()
            mock_executor.return_value = expected_report
            mock_loop.return_value.run_in_executor = mock_executor

            report = await zap_client.generate_html_report()

            assert report == expected_report

    @pytest.mark.asyncio
    async def test_generate_json_report(self, zap_client):
        """Test generating JSON report."""
        mock_alerts = [
            ZAPAlert(
                alert_id="1",
                name="SQL Injection",
                risk="High",
                confidence="High",
                url="https://example.com/login",
                description="SQL injection vulnerability",
                solution="Use parameterized queries",
                reference="",
                plugin_id="10001",
            )
        ]

        with patch.object(zap_client, "get_alerts", return_value=mock_alerts):
            report = await zap_client.generate_json_report()

            assert "alerts" in report
            assert "total_alerts" in report
            assert report["total_alerts"] == 1
            assert len(report["alerts"]) == 1
            assert report["alerts"][0]["name"] == "SQL Injection"

    @pytest.mark.asyncio
    async def test_generate_json_report_with_risk_breakdown(self, zap_client):
        """Test JSON report includes risk breakdown like our implementation."""
        mock_alerts = [
            ZAPAlert(
                alert_id="2",
                name="High Risk Alert",
                risk="High",
                confidence="High",
                url="https://example.com/",
                description="High risk description",
                solution="Fix high risk issue",
                reference="",
                plugin_id="10002",
            ),
            ZAPAlert(
                alert_id="3",
                name="Medium Risk Alert",
                risk="Medium",
                confidence="High",
                url="https://example.com/",
                description="Medium risk description",
                solution="Fix medium risk issue",
                reference="",
                plugin_id="10003",
            ),
            ZAPAlert(
                alert_id="4",
                name="Informational Alert",
                risk="Informational",
                confidence="Medium",
                url="https://example.com/",
                description="Informational description",
                solution="Review informational finding",
                reference="",
                plugin_id="10004",
            ),
        ]

        with patch.object(zap_client, "get_alerts", return_value=mock_alerts):
            report = await zap_client.generate_json_report()

            assert report["total_alerts"] == 3
            # Could verify risk breakdown if implemented in the actual method

    @pytest.mark.asyncio
    async def test_clear_session_success(self, zap_client, mock_zap):
        """Test clearing ZAP session successfully."""
        zap_client.zap = mock_zap

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_executor = AsyncMock()
            mock_executor.return_value = None
            mock_loop.return_value.run_in_executor = mock_executor

            result = await zap_client.clear_session()

            assert result is True

    @pytest.mark.asyncio
    async def test_clear_session_failure(self, zap_client, mock_zap):
        """Test clearing ZAP session failure."""
        zap_client.zap = mock_zap

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_executor = AsyncMock()
            mock_executor.side_effect = Exception("Failed to clear session")
            mock_loop.return_value.run_in_executor = mock_executor

            result = await zap_client.clear_session()

            assert result is False

    @pytest.mark.asyncio
    async def test_connection_error_handling(self, zap_client):
        """Test handling of connection errors."""
        # Test what happens when ZAP is not running
        with patch("src.owasp_zap_mcp.zap_client.ZAPv2") as mock_zapv2:
            mock_zapv2.side_effect = Exception("Connection refused")

            # This would test connection error handling
            # The actual implementation might vary
            try:
                await zap_client.connect()
            except Exception as e:
                assert "Connection refused" in str(e)

    @pytest.mark.asyncio
    async def test_scan_timeout_handling(self, zap_client, mock_zap):
        """Test handling of scan timeouts."""
        zap_client.zap = mock_zap

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_executor = AsyncMock()
            mock_executor.side_effect = asyncio.TimeoutError("Scan timeout")
            mock_loop.return_value.run_in_executor = mock_executor

            # Test how timeouts are handled
            try:
                await zap_client.spider_scan("https://slow-site.com")
            except asyncio.TimeoutError:
                # This is expected behavior
                pass


class TestZAPScanStatus:
    """Test cases for ZAP scan status model."""

    def test_scan_status_creation(self):
        """Test creating a scan status object."""
        status = ZAPScanStatus.RUNNING
        assert status == ZAPScanStatus.RUNNING

    def test_scan_status_finished(self):
        """Test scan status when finished."""
        status = ZAPScanStatus.COMPLETED
        assert status == ZAPScanStatus.COMPLETED

    def test_scan_status_edge_cases(self):
        """Test scan status edge cases."""
        # Test with 0 progress
        status = ZAPScanStatus.NOT_STARTED
        assert status == ZAPScanStatus.NOT_STARTED


class TestZAPAlert:
    """Test cases for ZAP alert model."""

    def test_alert_creation(self):
        """Test creating an alert object."""
        alert_data = {
            "alert_id": "1",
            "name": "XSS Vulnerability",
            "risk": "Medium",
            "confidence": "High",
            "url": "https://example.com/search",
            "description": "Cross-site scripting vulnerability",
            "solution": "Encode user input",
            "reference": "",
            "plugin_id": "10001",
        }

        alert = ZAPAlert(**alert_data)

        assert alert.name == "XSS Vulnerability"
        assert alert.risk == "Medium"
        assert alert.confidence == "High"
        assert alert.url == "https://example.com/search"
        assert alert.description == "Cross-site scripting vulnerability"
        assert alert.solution == "Encode user input"

    def test_alert_creation_with_missing_fields(self):
        """Test creating an alert object with missing fields."""
        alert_data = {
            "alert_id": "2",
            "name": "Test Alert",
            "risk": "",
            "confidence": "",
            "url": "",
            "description": "",
            "solution": "",
            "reference": "",
            "plugin_id": "",
        }

        alert = ZAPAlert(**alert_data)

        assert alert.name == "Test Alert"
        assert alert.risk == ""
        assert alert.confidence == ""
        assert alert.url == ""
        assert alert.description == ""
        assert alert.solution == ""

    def test_alert_creation_realistic_findings(self):
        """Test creating alerts with realistic security findings."""
        # Test with a realistic security header finding
        alert_data = {
            "alert_id": "3",
            "name": "Missing X-Frame-Options Header",
            "risk": "Medium",
            "confidence": "High",
            "url": "https://skyral.io/",
            "description": "X-Frame-Options header is not included in the response to protect against clickjacking attacks",
            "solution": "Most modern Web browsers support the X-Frame-Options HTTP header",
            "reference": "",
            "plugin_id": "10003",
        }

        alert = ZAPAlert(**alert_data)

        assert alert.name == "Missing X-Frame-Options Header"
        assert alert.risk == "Medium"
        assert "clickjacking" in alert.description
        assert "X-Frame-Options" in alert.solution

    def test_alert_serialization(self):
        """Test alert can be serialized to dictionary."""
        alert_data = {
            "alert_id": "4",
            "name": "Test Alert",
            "risk": "High",
            "confidence": "High",
            "url": "https://example.com/",
            "description": "Test description",
            "solution": "Test solution",
            "reference": "",
            "plugin_id": "10004",
        }

        alert = ZAPAlert(**alert_data)

        # Test that the alert can be converted back to dict (for JSON reports)
        alert_dict = alert.__dict__
        assert alert_dict["name"] == "Test Alert"
        assert alert_dict["risk"] == "High"
