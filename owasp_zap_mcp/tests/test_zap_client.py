"""
Tests for ZAP Client

Basic tests to verify ZAP client functionality and API integration.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from owasp_zap_mcp.zap_client import ZAPAlert, ZAPClient, ZAPScanStatus


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
        with patch("owasp_zap_mcp.zap_client.ZAPv2") as mock_zapv2:
            mock_zap_instance = MagicMock()
            mock_zapv2.return_value = mock_zap_instance

            await zap_client.connect()

            assert zap_client.zap is not None
            mock_zapv2.assert_called_once_with(apikey="test-key", proxies=None)
            assert zap_client.zap._ZAPv2__base == "http://localhost:8080"

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
            assert status.status == "RUNNING"
            assert status.progress == 50

    @pytest.mark.asyncio
    async def test_get_spider_status_finished(self, zap_client, mock_zap):
        """Test getting spider scan status - finished."""
        zap_client.zap = mock_zap

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_executor = AsyncMock()
            mock_executor.return_value = "100"
            mock_loop.return_value.run_in_executor = mock_executor

            status = await zap_client.get_spider_status("123")

            assert status.status == "FINISHED"
            assert status.progress == 100

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
            assert status.status == "RUNNING"
            assert status.progress == 75

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
                {
                    "name": "SQL Injection",
                    "risk": "High",
                    "confidence": "High",
                    "description": "SQL injection vulnerability",
                    "url": "https://example.com/login",
                    "solution": "Use parameterized queries",
                }
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


class TestZAPScanStatus:
    """Test cases for ZAP scan status model."""

    def test_scan_status_creation(self):
        """Test creating a scan status object."""
        status = ZAPScanStatus(status="RUNNING", progress=75)

        assert status.status == "RUNNING"
        assert status.progress == 75


class TestZAPAlert:
    """Test cases for ZAP alert model."""

    def test_alert_creation(self):
        """Test creating an alert object."""
        alert_data = {
            "name": "XSS Vulnerability",
            "risk": "Medium",
            "confidence": "High",
            "description": "Cross-site scripting vulnerability",
            "url": "https://example.com/search",
            "solution": "Encode user input",
        }

        alert = ZAPAlert(alert_data)

        assert alert.name == "XSS Vulnerability"
        assert alert.risk == "Medium"
        assert alert.confidence == "High"
        assert alert.url == "https://example.com/search"
        assert alert.description == "Cross-site scripting vulnerability"
        assert alert.solution == "Encode user input"

    def test_alert_creation_with_missing_fields(self):
        """Test creating an alert object with missing fields."""
        alert_data = {"name": "Test Alert"}

        alert = ZAPAlert(alert_data)

        assert alert.name == "Test Alert"
        assert alert.risk == "Unknown"
        assert alert.confidence == "Unknown"
        assert alert.url == ""
        assert alert.description == ""
        assert alert.solution == ""
