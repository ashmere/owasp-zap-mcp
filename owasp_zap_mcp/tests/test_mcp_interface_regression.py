"""
Regression tests for MCP interface to prevent session validation issues.

These tests ensure the MCP interface continues working correctly and prevent
the "Invalid session ID" error from recurring.
"""

import asyncio
import json
import pytest
import aiohttp
from unittest.mock import AsyncMock, patch


@pytest.mark.integration
@pytest.mark.mcp
class TestMCPInterfaceRegression:
    """Regression tests for MCP interface functionality"""

    @pytest.fixture
    def mcp_base_url(self):
        """Base URL for MCP server"""
        return "http://localhost:3000"

    @pytest.fixture
    def test_session_id(self):
        """Test session ID"""
        return "test_regression_session"

    @pytest.mark.asyncio
    async def test_mcp_session_auto_creation(self, mcp_base_url, test_session_id):
        """Test that MCP interface auto-creates sessions correctly"""
        url = f"{mcp_base_url}/mcp/messages"
        params = {"session_id": test_session_id}
        
        payload = {
            "method": "tools/call",
            "params": {
                "name": "zap_health_check",
                "arguments": {}
            },
            "jsonrpc": "2.0",
            "id": 1
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, 
                params=params, 
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                # Should not return "Invalid session ID" error
                assert response.status == 200
                
                result = await response.json()
                
                # Should return success status, not error
                assert result.get("status") == "success"
                assert "Invalid session ID" not in str(result)

    @pytest.mark.asyncio
    async def test_mcp_parameter_processing(self, mcp_base_url, test_session_id):
        """Test that parameter processing works correctly with random_string"""
        url = f"{mcp_base_url}/mcp/messages"
        params = {"session_id": f"{test_session_id}_params"}
        
        payload = {
            "method": "tools/call",
            "params": {
                "name": "zap_spider_scan",
                "arguments": {
                    "random_string": "https://example.com"
                }
            },
            "jsonrpc": "2.0",
            "id": 2
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, 
                params=params, 
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                # Should successfully process the URL from random_string
                assert response.status == 200
                
                result = await response.json()
                assert result.get("status") == "success"

    @pytest.mark.asyncio
    async def test_mcp_multiple_tool_calls(self, mcp_base_url, test_session_id):
        """Test multiple tool calls in the same session"""
        url = f"{mcp_base_url}/mcp/messages"
        params = {"session_id": f"{test_session_id}_multi"}
        
        # First call - health check
        payload1 = {
            "method": "tools/call",
            "params": {
                "name": "zap_health_check",
                "arguments": {}
            },
            "jsonrpc": "2.0",
            "id": 1
        }
        
        # Second call - get alerts
        payload2 = {
            "method": "tools/call",
            "params": {
                "name": "zap_get_alerts",
                "arguments": {}
            },
            "jsonrpc": "2.0",
            "id": 2
        }
        
        async with aiohttp.ClientSession() as session:
            # First call
            async with session.post(
                url, 
                params=params, 
                json=payload1,
                headers={"Content-Type": "application/json"}
            ) as response1:
                assert response1.status == 200
                result1 = await response1.json()
                assert result1.get("status") == "success"
            
            # Second call in same session
            async with session.post(
                url, 
                params=params, 
                json=payload2,
                headers={"Content-Type": "application/json"}
            ) as response2:
                assert response2.status == 200
                result2 = await response2.json()
                assert result2.get("status") == "success"

    @pytest.mark.asyncio
    async def test_mcp_error_handling(self, mcp_base_url):
        """Test MCP error handling doesn't return generic session errors"""
        url = f"{mcp_base_url}/mcp/messages"
        params = {"session_id": "error_test_session"}
        
        # Invalid tool name
        payload = {
            "method": "tools/call",
            "params": {
                "name": "invalid_tool_name",
                "arguments": {}
            },
            "jsonrpc": "2.0",
            "id": 1
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, 
                params=params, 
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                # Should return proper error, not session validation error
                assert response.status == 200  # MCP returns 200 with error in body
                
                result = await response.json()
                # Should not be a session error
                assert "Invalid session ID" not in str(result)

    @pytest.mark.asyncio
    async def test_mcp_missing_session_id(self, mcp_base_url):
        """Test proper error when session_id is missing"""
        url = f"{mcp_base_url}/mcp/messages"
        # No session_id parameter
        
        payload = {
            "method": "tools/call",
            "params": {
                "name": "zap_health_check",
                "arguments": {}
            },
            "jsonrpc": "2.0",
            "id": 1
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, 
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                # Should return 400 with proper error message
                assert response.status == 400
                
                result = await response.json()
                assert result.get("error") == "Missing session_id parameter"

    def test_mcp_interface_documentation(self):
        """Test that MCP interface is properly documented"""
        # Ensure the development tips mention the MCP interface patterns
        import os
        
        docs_path = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "development-tips.ai.md")
        
        if os.path.exists(docs_path):
            with open(docs_path, 'r') as f:
                content = f.read()
                
            # Check for key MCP documentation
            assert "random_string" in content
            assert "parameter processing" in content.lower()
            assert "mcp" in content.lower()
        else:
            pytest.skip("Development tips documentation not found")

    @pytest.mark.asyncio
    async def test_mcp_real_world_workflow(self, mcp_base_url):
        """Test a real-world MCP workflow similar to skyral.io scan"""
        session_id = "real_world_test"
        url = f"{mcp_base_url}/mcp/messages"
        params = {"session_id": session_id}
        
        # Simulate the workflow we used for skyral.io
        workflow_steps = [
            {
                "name": "zap_health_check",
                "arguments": {},
                "description": "Health check"
            },
            {
                "name": "zap_spider_scan", 
                "arguments": {"random_string": "https://httpbin.org"},
                "description": "Spider scan with URL in random_string"
            },
            {
                "name": "zap_get_alerts",
                "arguments": {},
                "description": "Get all alerts"
            }
        ]
        
        async with aiohttp.ClientSession() as session:
            for i, step in enumerate(workflow_steps, 1):
                payload = {
                    "method": "tools/call",
                    "params": step,
                    "jsonrpc": "2.0",
                    "id": i
                }
                
                async with session.post(
                    url,
                    params=params,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    assert response.status == 200, f"Step {step['description']} failed"
                    
                    result = await response.json()
                    assert result.get("status") == "success", f"Step {step['description']} returned error: {result}"
                    assert "Invalid session ID" not in str(result) 
