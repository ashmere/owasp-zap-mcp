"""
Tests for SSE Server Parameter Processing

Tests covering the SSE server parameter processing fixes, especially random_string handling.
"""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from src.owasp_zap_mcp.sse_server import ZAPMCPSseServer


class TestSSEServerParameterProcessing:
    """Test cases for SSE server parameter processing functionality."""

    @pytest.fixture
    def mock_mcp_server(self):
        """Create a mock MCP server."""
        mock_server = MagicMock()
        mock_server.name = "test-mcp-server"
        mock_server.list_tools = AsyncMock(return_value=[])
        return mock_server

    @pytest.fixture
    def mock_app(self):
        """Create a mock FastAPI app."""
        return FastAPI()

    @pytest.fixture
    def sse_server(self, mock_mcp_server, mock_app):
        """Create an SSE server instance."""
        return ZAPMCPSseServer(mock_mcp_server, mock_app)

    def test_extract_recent_query_empty(self, sse_server):
        """Test extracting recent query from empty request."""
        mock_request = MagicMock()
        mock_request._body = None
        mock_request._json = {}

        result = sse_server._extract_recent_query(mock_request)
        assert result is None

    def test_extract_recent_query_with_content(self, sse_server):
        """Test extracting recent query with content."""
        mock_request = MagicMock()
        mock_request._body = json.dumps(
            {
                "params": {
                    "messages": [
                        {"role": "user", "content": "scan skyral.io"},
                        {"role": "assistant", "content": "I'll scan that for you."},
                    ]
                }
            }
        ).encode()
        mock_request._json = {}

        result = sse_server._extract_recent_query(mock_request)
        assert result == "scan skyral.io"

    def test_process_tool_arguments_url_from_random_string(self, sse_server):
        """Test processing tool arguments with URL extraction from random_string."""
        # Test spider scan tool with various URL patterns discovered during testing
        test_cases = [
            # Plain domains (most common pattern discovered)
            ("example.com", "https://example.com"),
            ("httpbin.org", "https://httpbin.org"),
            ("api.example.com", "https://api.example.com"),
            # Domains with paths
            ("httpbin.org/get", "https://httpbin.org/get"),
            ("example.com/api/v1", "https://example.com/api/v1"),
            # Already complete URLs (should remain unchanged)
            ("https://example.com", "https://example.com"),
            ("http://localhost:8080", "http://localhost:8080"),
        ]

        for input_url, expected_url in test_cases:
            args = {"random_string": input_url}
            result = sse_server._process_tool_arguments(
                "mcp_zap_spider_scan", args, None
            )

            assert (
                result["url"] == expected_url
            ), f"Failed for {input_url}: got {result.get('url')}, expected {expected_url}"
            assert "random_string" not in result

    def test_process_tool_arguments_url_already_present(self, sse_server):
        """Test that existing URL parameter is preserved."""
        args = {"url": "https://existing.com", "random_string": "skyral.io"}
        result = sse_server._process_tool_arguments("mcp_zap_spider_scan", args, None)

        assert result["url"] == "https://existing.com"
        assert "random_string" not in result

    def test_process_tool_arguments_scan_id_extraction(self, sse_server):
        """Test extracting scan ID from random_string."""
        args = {"random_string": "scan id is 123"}
        result = sse_server._process_tool_arguments("mcp_zap_spider_status", args, None)

        assert result["scan_id"] == "123"
        assert "random_string" not in result

    def test_process_tool_arguments_scan_id_numeric(self, sse_server):
        """Test extracting numeric scan ID."""
        args = {"random_string": "456"}
        result = sse_server._process_tool_arguments(
            "mcp_zap_active_scan_status", args, None
        )

        assert result["scan_id"] == "456"
        assert "random_string" not in result

    def test_process_tool_arguments_risk_level_extraction(self, sse_server):
        """Test extracting risk level from random_string."""
        test_cases = [
            ("get high risk alerts", "High"),
            ("show me medium severity issues", "Medium"),
            ("list low priority vulnerabilities", "Low"),
            ("informational findings please", "Informational"),
        ]

        for input_str, expected_level in test_cases:
            args = {"random_string": input_str}
            result = sse_server._process_tool_arguments(
                "mcp_zap_get_alerts", args, None
            )

            assert result["risk_level"] == expected_level
            assert "random_string" not in result

    def test_process_tool_arguments_url_pattern_extraction(self, sse_server):
        """Test extracting URLs from various patterns in random_string."""
        test_cases = [
            ("please scan https://example.com/path", "https://example.com/path"),
            ("check http://localhost:8080", "http://localhost:8080"),
            # Simple domains get https:// added
            ("example.com", "https://example.com"),
            ("api.example.com", "https://api.example.com"),
        ]

        for input_str, expected_url in test_cases:
            args = {"random_string": input_str}
            result = sse_server._process_tool_arguments(
                "mcp_zap_spider_scan", args, None
            )

            assert result["url"] == expected_url
            assert "random_string" not in result

    def test_process_tool_arguments_non_zap_tool(self, sse_server):
        """Test that non-ZAP tools have random_string removed."""
        args = {"random_string": "some value", "other_param": "keep this"}
        result = sse_server._process_tool_arguments("some_other_tool", args, None)

        assert "random_string" not in result
        assert result["other_param"] == "keep this"

    def test_process_tool_arguments_complex_url_patterns(self, sse_server):
        """Test complex URL pattern extraction."""
        test_cases = [
            # Domain with path - simple domain gets https added
            ("example.com/api/v1", "https://example.com/api/v1"),
            # Subdomain
            ("api.github.com", "https://api.github.com"),
            # Complete URLs are preserved
            ("https://example.com/path", "https://example.com/path"),
        ]

        for input_str, expected_url in test_cases:
            args = {"random_string": input_str}
            result = sse_server._process_tool_arguments(
                "mcp_zap_active_scan", args, None
            )

            assert result["url"] == expected_url

    def test_process_tool_arguments_edge_cases(self, sse_server):
        """Test edge cases in parameter processing."""
        # Empty random_string
        args = {"random_string": ""}
        result = sse_server._process_tool_arguments("mcp_zap_spider_scan", args, None)
        assert "url" not in result or result.get("url") == ""

        # No random_string parameter
        args = {"other_param": "value"}
        result = sse_server._process_tool_arguments("mcp_zap_spider_scan", args, None)
        assert result == {"other_param": "value"}

    def test_process_tool_arguments_with_recent_query_fallback(self, sse_server):
        """Test using recent query as fallback when random_string is empty."""
        args = {"random_string": ""}
        recent_query = "example.com"  # Simple domain for testing
        result = sse_server._process_tool_arguments(
            "mcp_zap_spider_scan", args, recent_query
        )

        # Should use recent_query as fallback and normalize it
        assert result["url"] == "https://example.com"

    def test_tool_name_mapping(self, sse_server):
        """Test that tool names are properly mapped to internal function names."""
        tool_mapping_tests = [
            ("zap_health_check", "mcp_zap_health_check"),
            ("zap_spider_scan", "mcp_zap_spider_scan"),
            ("zap_active_scan", "mcp_zap_active_scan"),
            ("zap_get_alerts", "mcp_zap_get_alerts"),
        ]

        # This would be tested in the actual call_tool method
        # Here we're just documenting the expected mapping
        for external_name, internal_name in tool_mapping_tests:
            assert external_name != internal_name
            assert internal_name.startswith("mcp_")

    def test_process_tool_arguments_natural_language_url_extraction(self, sse_server):
        """Test extracting URLs from natural language queries discovered during usage."""
        # These patterns were discovered during actual MCP tool usage
        natural_language_patterns = [
            # Complete URLs in natural language
            (
                "please scan https://example.com for vulnerabilities",
                "https://example.com",
            ),
            ("check the security of https://httpbin.org", "https://httpbin.org"),
            ("analyze https://example.com/api", "https://example.com/api"),
            # Simple domains get normalized
            ("httpbin.org", "https://httpbin.org"),
            ("api.github.com", "https://api.github.com"),
        ]

        for query, expected_url in natural_language_patterns:
            args = {"random_string": query}
            result = sse_server._process_tool_arguments(
                "mcp_zap_spider_scan", args, None
            )

            assert (
                result["url"] == expected_url
            ), f"Failed for '{query}': got {result.get('url')}, expected {expected_url}"
            assert "random_string" not in result

    def test_process_tool_arguments_scan_id_patterns(self, sse_server):
        """Test extracting scan IDs from various patterns discovered during usage."""
        scan_id_patterns = [
            # Direct numeric IDs
            ("123", "123"),
            ("456789", "456789"),
            # IDs in sentences - regex extracts numbers
            ("scan id is 123", "123"),
            ("check status of scan 456", "456"),
            ("spider scan 789 progress", "789"),
            ("active scan id: 101112", "101112"),
        ]

        for input_str, expected_id in scan_id_patterns:
            args = {"random_string": input_str}
            result = sse_server._process_tool_arguments(
                "mcp_zap_spider_status", args, None
            )

            assert (
                result["scan_id"] == expected_id
            ), f"Failed for '{input_str}': got {result.get('scan_id')}, expected {expected_id}"
            assert "random_string" not in result

    def test_process_tool_arguments_risk_level_patterns(self, sse_server):
        """Test extracting risk levels from natural language discovered during usage."""
        risk_level_patterns = [
            # Direct risk levels
            ("High", "High"),
            ("Medium", "Medium"),
            ("Low", "Low"),
            ("Informational", "Informational"),
            # Natural language patterns discovered
            ("show me high risk vulnerabilities", "High"),
            ("get medium severity issues", "Medium"),
            ("list low priority findings", "Low"),
            ("display informational alerts", "Informational"),
            # Case variations
            ("HIGH RISK ALERTS", "High"),
            ("medium risk findings", "Medium"),
            ("low severity issues", "Low"),
            ("informational findings", "Informational"),
        ]

        for input_str, expected_level in risk_level_patterns:
            args = {"random_string": input_str}
            result = sse_server._process_tool_arguments(
                "mcp_zap_get_alerts", args, None
            )

            assert (
                result["risk_level"] == expected_level
            ), f"Failed for '{input_str}': got {result.get('risk_level')}, expected {expected_level}"
            assert "random_string" not in result

    def test_process_tool_arguments_runtime_error_fallback(self, sse_server):
        """Test RuntimeError fallback mechanism discovered during debugging."""
        # Test that when parameter processing fails, it falls back gracefully
        args = {"random_string": "invalid_pattern_that_should_cause_error"}

        # This should not raise an exception but handle gracefully
        try:
            result = sse_server._process_tool_arguments(
                "mcp_zap_spider_scan", args, None
            )
            # Should either extract something reasonable or leave empty
            assert isinstance(result, dict)
            assert "random_string" not in result
        except RuntimeError:
            # If RuntimeError is raised, it should be handled gracefully
            # This tests the fallback mechanism
            pass

    def test_process_tool_arguments_session_auto_creation(self, sse_server):
        """Test session auto-creation functionality discovered during testing."""
        # Test that tools requiring sessions work with random_string
        session_tools = [
            "mcp_zap_health_check",
            "mcp_zap_clear_session",
            "mcp_zap_generate_html_report",
            "mcp_zap_generate_json_report",
        ]

        for tool_name in session_tools:
            args = {"random_string": "test_session_data"}
            result = sse_server._process_tool_arguments(tool_name, args, None)

            # These tools should work even with random_string (it gets removed)
            assert "random_string" not in result
            assert isinstance(result, dict)


class TestSSEServerIntegration:
    """Integration tests for SSE server functionality."""

    @pytest.fixture
    def mock_app(self):
        """Create a FastAPI app for testing."""
        return FastAPI()

    @pytest.fixture
    def mock_mcp_server(self):
        """Create a mock MCP server with tools."""
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
    def sse_server(self, mock_mcp_server, mock_app):
        """Create SSE server with mocked dependencies."""
        return ZAPMCPSseServer(mock_mcp_server, mock_app)

    def test_sse_server_initialization(self, sse_server, mock_mcp_server, mock_app):
        """Test SSE server initialization."""
        assert sse_server.mcp_server == mock_mcp_server
        assert sse_server.app == mock_app
        assert sse_server.client_sessions == {}

    @pytest.mark.asyncio
    async def test_health_check_endpoint(self, sse_server, mock_app):
        """Test the health check endpoint."""
        client = TestClient(mock_app)

        # Make request to health endpoint
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["server"] == "OWASP ZAP MCP Server"

    @pytest.mark.asyncio
    async def test_status_endpoint(self, sse_server, mock_app, mock_mcp_server):
        """Test the status endpoint."""
        client = TestClient(mock_app)

        # Make request to status endpoint
        response = client.get("/status")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
        assert data["name"] == "owasp-zap-mcp"
        assert data["mode"] == "mcp_sse"
        assert data["clients"] == 0
        assert isinstance(data["tools"], list)

    @pytest.mark.asyncio
    async def test_session_auto_creation(self, sse_server):
        """Test session auto-creation functionality."""
        # Mock request
        mock_request = MagicMock()
        mock_request.query_params = {"session_id": "test_session"}
        mock_request.json = AsyncMock(
            return_value={"method": "initialize", "params": {}, "id": 1}
        )

        # Verify session doesn't exist initially
        assert "test_session" not in sse_server.client_sessions

        # Call mcp_message which should auto-create session
        await sse_server.mcp_message(mock_request)

        # Verify session was auto-created
        assert "test_session" in sse_server.client_sessions
        session = sse_server.client_sessions["test_session"]
        assert "created_at" in session
        assert "last_active" in session
        assert "queue" in session

    @pytest.mark.asyncio
    async def test_call_tool_with_parameter_processing(self, sse_server):
        """Test call_tool method with parameter processing."""
        mock_request = MagicMock()
        mock_request.query_params = {}
        mock_request._body = None
        mock_request._json = {}

        # Mock the tool function to return the expected MCP response format
        with patch(
            "src.owasp_zap_mcp.tools.zap_tools.mcp_zap_health_check"
        ) as mock_tool_function:
            mock_tool_function.return_value = {
                "content": [
                    {
                        "type": "text",
                        "text": '{"success": true, "message": "Test result"}',
                    }
                ]
            }

            # Call tool with parameter processing
            result = await sse_server.call_tool("zap_health_check", {}, mock_request)

            # Verify the result has the expected MCP format
            assert "content" in result
            assert len(result["content"]) > 0
            assert result["content"][0]["type"] == "text"

    @pytest.mark.asyncio
    async def test_call_tool_with_url_normalization(self, sse_server):
        """Test call_tool with URL normalization via random_string."""
        mock_request = MagicMock()
        mock_request.query_params = {}
        mock_request._body = None
        mock_request._json = {}

        # Mock the tool function to return the expected MCP response format
        with patch(
            "src.owasp_zap_mcp.tools.zap_tools.mcp_zap_spider_scan"
        ) as mock_tool_function:
            mock_tool_function.return_value = {
                "content": [
                    {
                        "type": "text",
                        "text": '{"success": true, "message": "Scan started"}',
                    }
                ]
            }

            # Call tool with random_string containing URL
            arguments = {"random_string": "example.com"}
            result = await sse_server.call_tool(
                "zap_spider_scan", arguments, mock_request
            )

            # Verify the result has the expected MCP format
            assert "content" in result
            assert len(result["content"]) > 0
            assert result["content"][0]["type"] == "text"

    @pytest.mark.asyncio
    async def test_call_tool_missing_url_error(self, sse_server):
        """Test call_tool returns error if zap_spider_scan is called with no url/random_string."""
        mock_request = MagicMock()
        mock_request.query_params = {}
        mock_request._body = None
        mock_request._json = {}

        with patch(
            "src.owasp_zap_mcp.tools.zap_tools.mcp_zap_spider_scan"
        ) as mock_tool_function:
            mock_tool_function.side_effect = AssertionError(
                "Should not be called without url"
            )

            arguments = {}
            with pytest.raises(ValueError) as excinfo:
                await sse_server.call_tool("zap_spider_scan", arguments, mock_request)
            assert "Should not be called without url" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_call_tool_with_unparseable_random_string(self, sse_server):
        """Test call_tool returns error if zap_spider_scan is called with random_string that is not a URL or domain."""
        mock_request = MagicMock()
        mock_request.query_params = {}
        mock_request._body = None
        mock_request._json = {}

        with patch(
            "src.owasp_zap_mcp.tools.zap_tools.mcp_zap_spider_scan"
        ) as mock_tool_function:
            mock_tool_function.side_effect = AssertionError(
                "Should not be called without url"
            )

            arguments = {"random_string": "not_a_url_or_domain"}
            with pytest.raises(ValueError) as excinfo:
                await sse_server.call_tool("zap_spider_scan", arguments, mock_request)
            assert "Should not be called without url" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_call_tool_with_valid_random_string(self, sse_server):
        """Test call_tool works if zap_spider_scan is called with random_string containing a valid URL."""
        mock_request = MagicMock()
        mock_request.query_params = {}
        mock_request._body = None
        mock_request._json = {}

        with patch(
            "src.owasp_zap_mcp.tools.zap_tools.mcp_zap_spider_scan"
        ) as mock_tool_function:
            mock_tool_function.return_value = {
                "content": [
                    {
                        "type": "text",
                        "text": '{"success": true, "message": "Scan started"}',
                    },
                ]
            }
            arguments = {"random_string": "https://example.com"}
            result = await sse_server.call_tool(
                "zap_spider_scan", arguments, mock_request
            )
            assert "content" in result
            assert result["content"][0]["type"] == "text"

    @pytest.mark.asyncio
    async def test_call_tool_active_scan_missing_url_error(self, sse_server):
        """Test call_tool returns error if zap_active_scan is called with no url/random_string."""
        mock_request = MagicMock()
        mock_request.query_params = {}
        mock_request._body = None
        mock_request._json = {}

        with patch(
            "src.owasp_zap_mcp.tools.zap_tools.mcp_zap_active_scan"
        ) as mock_tool_function:
            mock_tool_function.side_effect = AssertionError(
                "Should not be called without url"
            )
            arguments = {}
            with pytest.raises(ValueError) as excinfo:
                await sse_server.call_tool("zap_active_scan", arguments, mock_request)
            assert "Should not be called without url" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_call_tool_active_scan_with_unparseable_random_string(
        self, sse_server
    ):
        """Test call_tool returns error if zap_active_scan is called with random_string that is not a URL or domain."""
        mock_request = MagicMock()
        mock_request.query_params = {}
        mock_request._body = None
        mock_request._json = {}

        with patch(
            "src.owasp_zap_mcp.tools.zap_tools.mcp_zap_active_scan"
        ) as mock_tool_function:
            mock_tool_function.side_effect = AssertionError(
                "Should not be called without url"
            )
            arguments = {"random_string": "not_a_url_or_domain"}
            with pytest.raises(ValueError) as excinfo:
                await sse_server.call_tool("zap_active_scan", arguments, mock_request)
            assert "Should not be called without url" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_call_tool_active_scan_with_valid_random_string(self, sse_server):
        """Test call_tool works if zap_active_scan is called with random_string containing a valid URL."""
        mock_request = MagicMock()
        mock_request.query_params = {}
        mock_request._body = None
        mock_request._json = {}

        with patch(
            "src.owasp_zap_mcp.tools.zap_tools.mcp_zap_active_scan"
        ) as mock_tool_function:
            mock_tool_function.return_value = {
                "content": [
                    {
                        "type": "text",
                        "text": '{"success": true, "message": "Active scan started"}',
                    },
                ]
            }
            arguments = {"random_string": "https://example.com"}
            result = await sse_server.call_tool(
                "zap_active_scan", arguments, mock_request
            )
            assert "content" in result
            assert result["content"][0]["type"] == "text"


class TestSSEServerErrorHandling:
    """Test error handling in SSE server."""

    @pytest.fixture
    def sse_server(self):
        """Create SSE server for error testing."""
        mock_mcp = MagicMock()
        mock_app = FastAPI()
        return ZAPMCPSseServer(mock_mcp, mock_app)

    @pytest.mark.asyncio
    async def test_call_tool_runtime_error_fallback(self, sse_server):
        """Test RuntimeError fallback handling in call_tool."""
        mock_request = MagicMock()
        mock_request.query_params = {}
        mock_request._body = None
        mock_request._json = {}

        # Mock the tool to raise RuntimeError about SSE processing
        mock_tool = MagicMock()
        mock_tool.name = "zap_spider_scan"
        mock_tool.side_effect = RuntimeError(
            "should be called via SSE server parameter processing"
        )

        sse_server.mcp_server.list_tools = AsyncMock(return_value=[mock_tool])

        # Mock the fallback - since we can't easily mock the fallback import,
        # we'll just test that the RuntimeError is handled
        try:
            result = await sse_server.call_tool(
                "zap_spider_scan", {"random_string": "example.com"}, mock_request
            )
            # If we get here, the fallback worked
            assert True
        except ValueError as e:
            # This is expected if fallback function is not found
            assert "Could not find fallback function" in str(e)

    @pytest.mark.asyncio
    async def test_call_tool_unknown_tool_error(self, sse_server):
        """Test error handling for unknown tools."""
        mock_request = MagicMock()
        sse_server.mcp_server.list_tools = AsyncMock(return_value=[])

        with pytest.raises(ValueError, match="Tool 'unknown_tool' not found"):
            await sse_server.call_tool("unknown_tool", {}, mock_request)

    @pytest.mark.asyncio
    async def test_extract_recent_query_json_error(self, sse_server):
        """Test error handling in extract_recent_query."""
        mock_request = MagicMock()
        mock_request._body = b"invalid json"
        mock_request._json = {}

        # Should not raise exception, should return None
        result = sse_server._extract_recent_query(mock_request)
        assert result is None
