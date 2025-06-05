"""
Error Scenario Tests for OWASP ZAP MCP

Tests covering various error conditions, edge cases, and failure scenarios.
"""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.owasp_zap_mcp.tools.zap_tools import (
    mcp_zap_active_scan,
    mcp_zap_active_scan_status,
    mcp_zap_clear_session,
    mcp_zap_generate_html_report,
    mcp_zap_generate_json_report,
    mcp_zap_get_alerts,
    mcp_zap_health_check,
    mcp_zap_scan_summary,
    mcp_zap_spider_scan,
    mcp_zap_spider_status,
    normalize_url,
)
from src.owasp_zap_mcp.zap_client import ZAPAlert, ZAPScanStatus


class TestConnectionErrorScenarios:
    """Test error scenarios related to ZAP connection issues."""

    @pytest.fixture
    def mock_zap_client_connection_error(self):
        """Create a mock ZAP client that raises connection errors."""
        with patch("src.owasp_zap_mcp.tools.zap_tools.ZAPClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.health_check.side_effect = ConnectionError("ZAP is not running")
            mock_client_class.return_value.__aenter__.return_value = mock_client
            yield mock_client

    @pytest.mark.asyncio
    async def test_health_check_connection_refused(
        self, mock_zap_client_connection_error
    ):
        """Test health check when ZAP is not running."""
        result = await mcp_zap_health_check()

        response_data = json.loads(result["content"][0]["text"])
        assert response_data["success"] is False
        assert "ZAP is not running" in response_data["error"]

    @pytest.mark.asyncio
    async def test_spider_scan_connection_error(self, mock_zap_client_connection_error):
        """Test spider scan when ZAP connection fails."""
        mock_zap_client_connection_error.spider_scan.side_effect = ConnectionError(
            "Connection refused"
        )

        result = await mcp_zap_spider_scan("example.com")

        response_data = json.loads(result["content"][0]["text"])
        assert response_data["success"] is False
        assert "Connection refused" in response_data["error"]

    @pytest.mark.asyncio
    async def test_active_scan_connection_error(self, mock_zap_client_connection_error):
        """Test active scan when ZAP connection fails."""
        mock_zap_client_connection_error.active_scan.side_effect = ConnectionError(
            "Connection refused"
        )

        result = await mcp_zap_active_scan("example.com")

        response_data = json.loads(result["content"][0]["text"])
        assert response_data["success"] is False
        assert "Connection refused" in response_data["error"]

    @pytest.mark.asyncio
    async def test_get_alerts_connection_error(self, mock_zap_client_connection_error):
        """Test getting alerts when ZAP connection fails."""
        mock_zap_client_connection_error.get_alerts.side_effect = ConnectionError(
            "Connection refused"
        )

        result = await mcp_zap_get_alerts()

        response_data = json.loads(result["content"][0]["text"])
        assert response_data["success"] is False
        assert "Connection refused" in response_data["error"]


class TestInputValidationErrors:
    """Test error scenarios related to invalid input parameters."""

    @pytest.fixture
    def mock_zap_client(self):
        """Create a mock ZAP client for input validation tests."""
        with patch("src.owasp_zap_mcp.tools.zap_tools.ZAPClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            yield mock_client

    @pytest.mark.asyncio
    async def test_spider_scan_empty_url(self, mock_zap_client):
        """Test spider scan with empty URL."""
        result = await mcp_zap_spider_scan("")

        response_data = json.loads(result["content"][0]["text"])
        assert response_data["success"] is False
        assert "Missing url parameter" in response_data["error"]

    @pytest.mark.asyncio
    async def test_spider_scan_none_url(self, mock_zap_client):
        """Test spider scan with None URL."""
        result = await mcp_zap_spider_scan(None)

        response_data = json.loads(result["content"][0]["text"])
        assert response_data["success"] is False
        assert "Missing url parameter" in response_data["error"]

    @pytest.mark.asyncio
    async def test_active_scan_empty_url(self, mock_zap_client):
        """Test active scan with empty URL."""
        result = await mcp_zap_active_scan("")

        response_data = json.loads(result["content"][0]["text"])
        assert response_data["success"] is False
        assert "Missing url parameter" in response_data["error"]

    @pytest.mark.asyncio
    async def test_spider_status_empty_scan_id(self, mock_zap_client):
        """Test spider status with empty scan ID."""
        result = await mcp_zap_spider_status("")

        response_data = json.loads(result["content"][0]["text"])
        assert response_data["success"] is False
        assert "Missing scan_id parameter" in response_data["error"]

    @pytest.mark.asyncio
    async def test_active_scan_status_empty_scan_id(self, mock_zap_client):
        """Test active scan status with empty scan ID."""
        result = await mcp_zap_active_scan_status("")

        response_data = json.loads(result["content"][0]["text"])
        assert response_data["success"] is False
        assert "Missing scan_id parameter" in response_data["error"]

    @pytest.mark.asyncio
    async def test_scan_summary_empty_url(self, mock_zap_client):
        """Test scan summary with empty URL."""
        result = await mcp_zap_scan_summary("")

        response_data = json.loads(result["content"][0]["text"])
        assert response_data["success"] is False
        assert "Missing url parameter" in response_data["error"]


class TestZAPAPIErrors:
    """Test error scenarios from ZAP API responses."""

    @pytest.fixture
    def mock_zap_client_api_errors(self):
        """Create a mock ZAP client that simulates API errors."""
        with patch("src.owasp_zap_mcp.tools.zap_tools.ZAPClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            yield mock_client

    @pytest.mark.asyncio
    async def test_spider_scan_api_error(self, mock_zap_client_api_errors):
        """Test spider scan when ZAP API returns error."""
        mock_zap_client_api_errors.spider_scan.side_effect = RuntimeError(
            "ZAP API error: Invalid URL format"
        )

        result = await mcp_zap_spider_scan("example.com")

        response_data = json.loads(result["content"][0]["text"])
        assert response_data["success"] is False
        assert "ZAP API error" in response_data["error"]

    @pytest.mark.asyncio
    async def test_active_scan_api_error(self, mock_zap_client_api_errors):
        """Test active scan when ZAP API returns error."""
        mock_zap_client_api_errors.active_scan.side_effect = RuntimeError(
            "ZAP API error: Scan not allowed"
        )

        result = await mcp_zap_active_scan("example.com")

        response_data = json.loads(result["content"][0]["text"])
        assert response_data["success"] is False
        assert "ZAP API error" in response_data["error"]

    @pytest.mark.asyncio
    async def test_get_spider_status_invalid_scan_id(self, mock_zap_client_api_errors):
        """Test spider status with invalid scan ID."""
        mock_zap_client_api_errors.get_spider_status.side_effect = RuntimeError(
            "Invalid scan ID: 999"
        )

        result = await mcp_zap_spider_status("999")

        response_data = json.loads(result["content"][0]["text"])
        assert response_data["success"] is False
        assert "Invalid scan ID" in response_data["error"]

    @pytest.mark.asyncio
    async def test_get_active_scan_status_invalid_scan_id(
        self, mock_zap_client_api_errors
    ):
        """Test active scan status with invalid scan ID."""
        mock_zap_client_api_errors.get_active_scan_status.side_effect = RuntimeError(
            "Invalid scan ID: 999"
        )

        result = await mcp_zap_active_scan_status("999")

        response_data = json.loads(result["content"][0]["text"])
        assert response_data["success"] is False
        assert "Invalid scan ID" in response_data["error"]

    @pytest.mark.asyncio
    async def test_generate_html_report_api_error(self, mock_zap_client_api_errors):
        """Test HTML report generation when ZAP API fails."""
        mock_zap_client_api_errors.generate_html_report.side_effect = RuntimeError(
            "Report generation failed"
        )

        result = await mcp_zap_generate_html_report()
        # Should be a string error message or None
        error_text = result["content"][0]["text"] if "content" in result else None
        assert error_text is not None
        assert "Report generation failed" in error_text

    @pytest.mark.asyncio
    async def test_generate_json_report_api_error(self, mock_zap_client_api_errors):
        """Test JSON report generation when ZAP API fails."""
        mock_zap_client_api_errors.generate_json_report.side_effect = RuntimeError(
            "Report generation failed"
        )

        result = await mcp_zap_generate_json_report()
        # Should be a string error message or None
        error_text = result["content"][0]["text"] if "content" in result else None
        assert error_text is not None
        assert "Report generation failed" in error_text

    @pytest.mark.asyncio
    async def test_clear_session_api_error(self, mock_zap_client_api_errors):
        """Test session clearing when ZAP API fails."""
        mock_zap_client_api_errors.clear_session.side_effect = RuntimeError(
            "Session clear failed"
        )

        result = await mcp_zap_clear_session()

        response_data = json.loads(result["content"][0]["text"])
        assert response_data["success"] is False
        assert "Session clear failed" in response_data["error"]


class TestTimeoutScenarios:
    """Test timeout and performance-related error scenarios."""

    @pytest.fixture
    def mock_zap_client_timeout(self):
        """Create a mock ZAP client that simulates timeouts."""
        with patch("src.owasp_zap_mcp.tools.zap_tools.ZAPClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            yield mock_client

    @pytest.mark.asyncio
    async def test_spider_scan_timeout(self, mock_zap_client_timeout):
        """Test spider scan timeout scenario."""
        mock_zap_client_timeout.spider_scan.side_effect = asyncio.TimeoutError(
            "Spider scan timeout"
        )

        result = await mcp_zap_spider_scan("example.com")

        response_data = json.loads(result["content"][0]["text"])
        assert response_data["success"] is False
        assert "timeout" in response_data["error"].lower()

    @pytest.mark.asyncio
    async def test_active_scan_timeout(self, mock_zap_client_timeout):
        """Test active scan timeout scenario."""
        mock_zap_client_timeout.active_scan.side_effect = asyncio.TimeoutError(
            "Active scan timeout"
        )

        result = await mcp_zap_active_scan("example.com")

        response_data = json.loads(result["content"][0]["text"])
        assert response_data["success"] is False
        assert "timeout" in response_data["error"].lower()

    @pytest.mark.asyncio
    async def test_get_alerts_timeout(self, mock_zap_client_timeout):
        """Test getting alerts timeout scenario."""
        mock_zap_client_timeout.get_alerts.side_effect = asyncio.TimeoutError(
            "Get alerts timeout"
        )

        result = await mcp_zap_get_alerts()

        response_data = json.loads(result["content"][0]["text"])
        assert response_data["success"] is False
        assert "timeout" in response_data["error"].lower()

    @pytest.mark.asyncio
    async def test_health_check_timeout(self, mock_zap_client_timeout):
        """Test health check timeout scenario."""
        mock_zap_client_timeout.health_check.side_effect = asyncio.TimeoutError(
            "Health check timeout"
        )

        result = await mcp_zap_health_check()

        response_data = json.loads(result["content"][0]["text"])
        assert response_data["success"] is False
        assert "timeout" in response_data["error"].lower()


class TestURLNormalizationEdgeCases:
    """Test edge cases in URL normalization."""

    def test_normalize_url_invalid_formats(self):
        """Test URL normalization with invalid formats."""
        invalid_urls = [
            "invalid-url-format",
            "ftp://example.com",  # Non-HTTP protocol
            "example.",  # Incomplete domain
            "www.",  # Incomplete domain
            ".com",  # Invalid domain
            "http://",  # Incomplete URL
            "https://",  # Incomplete URL
        ]

        for invalid_url in invalid_urls:
            result = normalize_url(invalid_url)
            # Should handle gracefully without crashing
            assert isinstance(result, str)

    def test_normalize_url_edge_cases(self):
        """Test URL normalization edge cases."""
        edge_cases = [
            ("localhost", "localhost"),  # No dot, should not be normalized
            (
                "localhost.localdomain",
                "https://localhost.localdomain",
            ),  # Has dot, should be normalized
            ("127.0.0.1", "https://127.0.0.1"),  # IP with dots
            ("::1", "::1"),  # IPv6, no dots
            ("a.b", "https://a.b"),  # Minimal domain with dot
            ("example.com.", "https://example.com."),  # Trailing dot
        ]

        for input_url, expected in edge_cases:
            result = normalize_url(input_url)
            assert (
                result == expected
            ), f"Failed for {input_url}: got {result}, expected {expected}"

    def test_normalize_url_special_characters(self):
        """Test URL normalization with special characters."""
        special_cases = [
            # URLs with spaces are not normalized (they contain spaces)
            ("example.com/path with spaces", "example.com/path with spaces"),
            ("example.com/path?query=value", "https://example.com/path?query=value"),
            ("example.com/path#fragment", "https://example.com/path#fragment"),
            ("example.com:8080/path", "https://example.com:8080/path"),
        ]

        for input_url, expected in special_cases:
            result = normalize_url(input_url)
            assert (
                result == expected
            ), f"Failed for {input_url}: got {result}, expected {expected}"


class TestDataCorruptionScenarios:
    """Test scenarios where data might be corrupted or malformed."""

    @pytest.fixture
    def mock_zap_client_malformed_data(self):
        """Create a mock ZAP client that returns malformed data."""
        with patch("src.owasp_zap_mcp.tools.zap_tools.ZAPClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            yield mock_client

    @pytest.mark.asyncio
    async def test_malformed_alerts_data(self, mock_zap_client_malformed_data):
        """Test handling of malformed alerts data."""
        # Create alerts with missing or corrupted data
        malformed_alerts = [
            ZAPAlert(
                alert_id="0",
                name="",
                risk="",
                confidence="",
                url="",
                description="",
                solution="",
                reference="",
                plugin_id="",
            ),  # Empty alert data
            ZAPAlert(
                alert_id="1",
                name=None,
                risk="",
                confidence="",
                url="",
                description="",
                solution="",
                reference="",
                plugin_id="",
            ),  # None name
            ZAPAlert(
                alert_id="2",
                name="Test",
                risk=None,
                confidence="",
                url="",
                description="",
                solution="",
                reference="",
                plugin_id="",
            ),  # None risk
        ]
        mock_zap_client_malformed_data.get_alerts.return_value = malformed_alerts

        result = await mcp_zap_get_alerts()

        response_data = json.loads(result["content"][0]["text"])
        # Should handle gracefully without crashing
        assert response_data["success"] is True
        assert response_data["total_alerts"] == 3

    @pytest.mark.asyncio
    async def test_malformed_scan_status(self, mock_zap_client_malformed_data):
        """Test handling of malformed scan status data."""
        # Mock malformed status
        malformed_status = ZAPScanStatus.UNKNOWN
        mock_zap_client_malformed_data.get_spider_status.return_value = malformed_status

        result = await mcp_zap_spider_status("123")

        response_data = json.loads(result["content"][0]["text"])
        # Should fail gracefully when ZAPScanStatus is returned instead of a status object
        assert response_data["success"] is False  # This is expected for now

    @pytest.mark.asyncio
    async def test_malformed_report_data(self, mock_zap_client_malformed_data):
        """Test handling of malformed report data."""
        # Mock corrupted HTML report
        mock_zap_client_malformed_data.generate_html_report.return_value = None

        result = await mcp_zap_generate_html_report()
        # Should return error message when report generation fails
        text = result["content"][0]["text"] if "content" in result else None
        assert text is not None
        assert "Failed to generate HTML report" in text

    @pytest.mark.asyncio
    async def test_malformed_json_report_data(self, mock_zap_client_malformed_data):
        """Test handling of malformed JSON report data."""
        # Mock corrupted JSON report
        mock_zap_client_malformed_data.generate_json_report.return_value = None

        result = await mcp_zap_generate_json_report()
        # Should return error message when report generation fails
        text = result["content"][0]["text"] if "content" in result else None
        assert text is not None
        assert "Failed to generate JSON report" in text
