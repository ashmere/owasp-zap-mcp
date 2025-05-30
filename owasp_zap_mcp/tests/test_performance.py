"""
Performance Tests for OWASP ZAP MCP

Tests covering performance characteristics, concurrent operations, and load scenarios.
"""

import asyncio
import time
from unittest.mock import AsyncMock, patch
import json

import pytest

from src.owasp_zap_mcp.tools.zap_tools import (
    mcp_zap_active_scan,
    mcp_zap_get_alerts,
    mcp_zap_health_check,
    mcp_zap_spider_scan,
    normalize_url,
)


class TestConcurrentOperations:
    """Test concurrent execution of MCP tools."""

    @pytest.fixture
    def mock_zap_client_performance(self):
        """Create a mock ZAP client optimized for performance testing."""
        with patch("src.owasp_zap_mcp.tools.zap_tools.ZAPClient") as mock_client_class:
            mock_client = AsyncMock()
            
            # Fast responses for performance testing
            mock_client.health_check.return_value = True
            mock_client.spider_scan.return_value = "123"
            mock_client.active_scan.return_value = "456"
            mock_client.get_alerts.return_value = []
            
            mock_client_class.return_value.__aenter__.return_value = mock_client
            yield mock_client

    @pytest.mark.asyncio
    async def test_concurrent_health_checks(self, mock_zap_client_performance):
        """Test concurrent health check operations."""
        start_time = time.time()
        
        # Run 10 concurrent health checks
        tasks = [mcp_zap_health_check() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # All should succeed
        assert len(results) == 10
        for result in results:
            assert result["content"][0]["text"]
        
        # Should complete reasonably quickly (adjust threshold as needed)
        assert execution_time < 5.0, f"Concurrent health checks took {execution_time:.2f}s"

    @pytest.mark.asyncio
    async def test_concurrent_spider_scans(self, mock_zap_client_performance):
        """Test concurrent spider scan operations."""
        start_time = time.time()
        
        # Run 5 concurrent spider scans for different URLs
        urls = ["example.com", "test.com", "demo.com", "sample.com", "website.com"]
        tasks = [mcp_zap_spider_scan(url) for url in urls]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # All should succeed
        assert len(results) == 5
        for result in results:
            assert result["content"][0]["text"]
        
        # Should complete reasonably quickly
        assert execution_time < 10.0, f"Concurrent spider scans took {execution_time:.2f}s"

    @pytest.mark.asyncio
    async def test_mixed_concurrent_operations(self, mock_zap_client_performance):
        """Test mixed concurrent operations (health checks, scans, alerts)."""
        start_time = time.time()
        
        # Mix of different operations
        tasks = [
            mcp_zap_health_check(),
            mcp_zap_spider_scan("example.com"),
            mcp_zap_active_scan("test.com"),
            mcp_zap_get_alerts(),
            mcp_zap_health_check(),
        ]
        
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # All should succeed
        assert len(results) == 5
        for result in results:
            assert result["content"][0]["text"]
        
        # Should complete reasonably quickly
        assert execution_time < 8.0, f"Mixed concurrent operations took {execution_time:.2f}s"


class TestURLNormalizationPerformance:
    """Test performance characteristics of URL normalization."""

    def test_url_normalization_batch_performance(self):
        """Test URL normalization performance with batch processing."""
        # Generate a large batch of URLs to normalize
        test_urls = [
            "example.com",
            "test.org",
            "demo.net",
            "sample.io",
            "localhost:3000",
            "127.0.0.1:8080",
            "api.service.com",
            "subdomain.example.com/path",
        ] * 100  # 800 URLs total
        
        start_time = time.time()
        
        # Normalize all URLs
        normalized_urls = [normalize_url(url) for url in test_urls]
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete quickly
        assert len(normalized_urls) == 800
        assert execution_time < 1.0, f"URL normalization took {execution_time:.3f}s for 800 URLs"
        
        # Verify some normalizations
        assert normalized_urls[0] == "https://example.com"
        assert normalized_urls[4] == "localhost:3000"  # No dot, not normalized

    def test_url_normalization_edge_case_performance(self):
        """Test URL normalization performance with edge cases."""
        edge_case_urls = [
            "",  # Empty
            None,  # None
            "a" * 1000,  # Very long string
            "invalid-format" * 50,  # Long invalid format
            "." * 100,  # Many dots
            "localhost" * 100,  # Long localhost
        ]
        
        start_time = time.time()
        
        # Should handle edge cases gracefully
        for url in edge_case_urls:
            try:
                result = normalize_url(url)
                assert isinstance(result, (str, type(None)))
            except Exception as e:
                # Should not crash on edge cases
                pytest.fail(f"URL normalization crashed on edge case '{url}': {e}")
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete quickly even with edge cases
        assert execution_time < 0.5, f"Edge case normalization took {execution_time:.3f}s"


class TestMemoryUsageScenarios:
    """Test memory usage patterns and cleanup."""

    @pytest.fixture
    def mock_zap_client_large_data(self):
        """Create a mock ZAP client that returns large datasets."""
        with patch("src.owasp_zap_mcp.tools.zap_tools.ZAPClient") as mock_client_class:
            mock_client = AsyncMock()
            
            # Mock large alert dataset
            from src.owasp_zap_mcp.zap_client import ZAPAlert
            large_alerts = [
                ZAPAlert({
                    "name": f"Alert {i}",
                    "risk": "Medium",
                    "confidence": "High",
                    "description": f"Description for alert {i} " + "x" * 200,  # Long description
                    "url": f"https://example.com/path{i}",
                    "solution": f"Solution for alert {i} " + "y" * 200,  # Long solution
                })
                for i in range(1000)  # 1000 alerts
            ]
            
            mock_client.get_alerts.return_value = large_alerts
            mock_client.health_check.return_value = True
            
            mock_client_class.return_value.__aenter__.return_value = mock_client
            yield mock_client

    @pytest.mark.asyncio
    async def test_large_alert_dataset_handling(self, mock_zap_client_large_data):
        """Test handling of large alert datasets."""
        start_time = time.time()
        
        result = await mcp_zap_get_alerts()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should handle large datasets efficiently
        assert result["content"][0]["text"]
        assert execution_time < 5.0, f"Large alert processing took {execution_time:.2f}s"
        
        # Verify response structure
        response_data = json.loads(result["content"][0]["text"])  # Use json.loads instead of eval
        assert response_data["success"] is True
        assert response_data["total_alerts"] == 1000
        # Only first 10 should be displayed due to pagination
        assert response_data["displayed_alerts"] == 10

    @pytest.mark.asyncio
    async def test_repeated_operations_memory_stability(self, mock_zap_client_large_data):
        """Test memory stability during repeated operations."""
        results = []
        
        start_time = time.time()
        
        # Perform repeated operations to test for memory leaks
        for i in range(50):
            result = await mcp_zap_health_check()
            results.append(result)
            
            # Periodically check alerts to mix operations
            if i % 10 == 0:
                alert_result = await mcp_zap_get_alerts()
                results.append(alert_result)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete all operations
        assert len(results) >= 50
        
        # Should maintain reasonable performance throughout
        assert execution_time < 30.0, f"Repeated operations took {execution_time:.2f}s"


class TestErrorRecoveryPerformance:
    """Test performance characteristics during error recovery."""

    @pytest.fixture
    def mock_zap_client_intermittent_errors(self):
        """Create a mock ZAP client with intermittent errors."""
        with patch("src.owasp_zap_mcp.tools.zap_tools.ZAPClient") as mock_client_class:
            mock_client = AsyncMock()
            
            # Create a counter to simulate intermittent failures
            call_count = {"count": 0}  # Use dict to make it mutable
            
            def intermittent_health_check():
                call_count["count"] += 1
                if call_count["count"] % 3 == 0:  # Fail every third call
                    raise ConnectionError("Intermittent connection error")
                return True
            
            mock_client.health_check.side_effect = intermittent_health_check
            mock_client_class.return_value.__aenter__.return_value = mock_client
            yield mock_client

    @pytest.mark.asyncio
    async def test_error_recovery_performance(self, mock_zap_client_intermittent_errors):
        """Test performance during error recovery scenarios."""
        successes = 0
        failures = 0
        
        start_time = time.time()
        
        # Run multiple operations expecting some to fail
        for i in range(10):
            try:
                result = await mcp_zap_health_check()
                response_data = json.loads(result["content"][0]["text"])  # Use json.loads
                if response_data["success"]:
                    successes += 1
                else:
                    failures += 1
            except Exception:
                failures += 1
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should have a mix of successes and failures
        assert successes > 0, "No successful operations"
        assert failures > 0, "No failed operations (expected some failures)"
        
        # Error handling should not significantly slow down operations
        assert execution_time < 10.0, f"Error recovery took {execution_time:.2f}s"


class TestScalabilityScenarios:
    """Test scalability with varying load levels."""

    @pytest.fixture
    def mock_zap_client_scalable(self):
        """Create a mock ZAP client for scalability testing."""
        with patch("src.owasp_zap_mcp.tools.zap_tools.ZAPClient") as mock_client_class:
            mock_client = AsyncMock()
            
            # Simulate realistic response times
            async def slow_spider_scan(url, max_depth=5):
                await asyncio.sleep(0.1)  # Simulate processing time
                return "123"
            
            async def slow_health_check():
                await asyncio.sleep(0.05)  # Simulate processing time
                return True
            
            mock_client.spider_scan.side_effect = slow_spider_scan
            mock_client.health_check.side_effect = slow_health_check
            
            mock_client_class.return_value.__aenter__.return_value = mock_client
            yield mock_client

    @pytest.mark.asyncio
    async def test_low_load_performance(self, mock_zap_client_scalable):
        """Test performance under low load (1-5 operations)."""
        start_time = time.time()
        
        tasks = [mcp_zap_health_check() for _ in range(5)]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        assert len(results) == 5
        # With 0.05s simulated delay, 5 concurrent operations should complete quickly
        assert execution_time < 1.0, f"Low load took {execution_time:.2f}s"

    @pytest.mark.asyncio
    async def test_medium_load_performance(self, mock_zap_client_scalable):
        """Test performance under medium load (10-20 operations)."""
        start_time = time.time()
        
        # Mix of operations
        tasks = []
        tasks.extend([mcp_zap_health_check() for _ in range(10)])
        tasks.extend([mcp_zap_spider_scan(f"example{i}.com") for i in range(10)])
        
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        assert len(results) == 20
        # Should scale reasonably well
        assert execution_time < 3.0, f"Medium load took {execution_time:.2f}s"

    @pytest.mark.asyncio
    async def test_high_load_performance(self, mock_zap_client_scalable):
        """Test performance under high load (50+ operations)."""
        start_time = time.time()
        
        # Large number of concurrent operations
        tasks = [mcp_zap_health_check() for _ in range(50)]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        assert len(results) == 50
        # Should handle high concurrency
        assert execution_time < 5.0, f"High load took {execution_time:.2f}s"
        
        # All operations should succeed
        for result in results:
            assert result["content"][0]["text"]


@pytest.mark.slow
class TestLongRunningOperations:
    """Test long-running operation scenarios (marked as slow tests)."""

    @pytest.fixture
    def mock_zap_client_long_operations(self):
        """Create a mock ZAP client that simulates long operations."""
        with patch("src.owasp_zap_mcp.tools.zap_tools.ZAPClient") as mock_client_class:
            mock_client = AsyncMock()
            
            async def long_spider_scan(url, max_depth=5):
                await asyncio.sleep(2.0)  # Simulate long scan
                return "123"
            
            mock_client.spider_scan.side_effect = long_spider_scan
            mock_client.health_check.return_value = True
            
            mock_client_class.return_value.__aenter__.return_value = mock_client
            yield mock_client

    @pytest.mark.asyncio
    async def test_long_operation_performance(self, mock_zap_client_long_operations):
        """Test performance of long-running operations."""
        start_time = time.time()
        
        # Start a long operation
        result = await mcp_zap_spider_scan("long-scan-target.com")
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete the long operation
        assert result["content"][0]["text"]
        
        # Verify it actually took the expected time
        assert execution_time >= 2.0, f"Long operation completed too quickly: {execution_time:.2f}s"
        assert execution_time < 5.0, f"Long operation took too long: {execution_time:.2f}s"

    @pytest.mark.asyncio
    async def test_concurrent_long_operations(self, mock_zap_client_long_operations):
        """Test concurrent long-running operations."""
        start_time = time.time()
        
        # Start multiple long operations concurrently
        tasks = [
            mcp_zap_spider_scan("target1.com"),
            mcp_zap_spider_scan("target2.com"),
            mcp_zap_spider_scan("target3.com"),
        ]
        
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete all operations
        assert len(results) == 3
        
        # Concurrent execution should be efficient (not 3x sequential time)
        assert execution_time >= 2.0, f"Concurrent long operations too fast: {execution_time:.2f}s"
        assert execution_time < 4.0, f"Concurrent long operations too slow: {execution_time:.2f}s" 
