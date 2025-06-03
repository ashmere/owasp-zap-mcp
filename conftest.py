import pytest

# Pytest top-level configuration for OWASP ZAP MCP

pytest_plugins = []


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "mcp: mark test as testing MCP functionality")
    config.addinivalue_line(
        "markers", "sse: mark test as testing SSE server functionality"
    )
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line(
        "markers", "real_world: mark test as testing real-world scenarios"
    )
    config.addinivalue_line("markers", "performance: mark test as performance testing")
    config.addinivalue_line(
        "markers", "error_handling: mark test as error handling testing"
    )
    config.addinivalue_line(
        "markers", "url_normalization: mark test as URL normalization testing"
    )
    config.addinivalue_line(
        "markers", "security: mark test as security-related testing"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location and name."""
    for item in items:
        # Mark tests based on file location
        if "test_performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)

        if "test_error_scenarios" in str(item.fspath):
            item.add_marker(pytest.mark.error_handling)

        if "test_integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        if "test_sse_server" in str(item.fspath):
            item.add_marker(pytest.mark.sse)

        if "test_mcp_tools" in str(item.fspath):
            item.add_marker(pytest.mark.mcp)

        # Mark tests based on test name patterns
        if "normalize_url" in item.name:
            item.add_marker(pytest.mark.url_normalization)

        if "security" in item.name or "alert" in item.name:
            item.add_marker(pytest.mark.security)

        if "concurrent" in item.name or "performance" in item.name:
            item.add_marker(pytest.mark.performance)

        if "long_running" in item.name or "slow" in item.name:
            item.add_marker(pytest.mark.slow)


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--run-slow", action="store_true", default=False, help="run slow tests"
    )
    parser.addoption(
        "--run-performance",
        action="store_true",
        default=False,
        help="run performance tests",
    )
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="run integration tests",
    )


def pytest_runtest_setup(item):
    """Skip tests based on command line options."""
    if "slow" in item.keywords and not item.config.getoption("--run-slow"):
        pytest.skip("need --run-slow option to run")

    if "performance" in item.keywords and not item.config.getoption(
        "--run-performance"
    ):
        pytest.skip("need --run-performance option to run")

    if "integration" in item.keywords and not item.config.getoption(
        "--run-integration"
    ):
        pytest.skip("need --run-integration option to run") 
