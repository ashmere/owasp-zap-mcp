# OWASP ZAP MCP Test Suite

This directory contains comprehensive tests for the OWASP ZAP MCP (Model Context Protocol) integration.

## Test Structure

### Test Files

- **`test_integration.py`** - Integration tests for the complete MCP server functionality
- **`test_mcp_tools.py`** - Unit tests for individual MCP tool functions
- **`test_sse_server.py`** - Tests for the Server-Sent Events (SSE) server implementation
- **`test_zap_client.py`** - Tests for the ZAP client wrapper
- **`test_error_scenarios.py`** - Comprehensive error handling and edge case tests
- **`test_performance.py`** - Performance, concurrency, and load testing

### Configuration Files

- **`conftest.py`** - Pytest configuration and shared fixtures
- **`pytest.ini`** - Pytest settings and test markers

## Test Categories

### Test Markers

Tests are automatically categorized using pytest markers:

- `unit` - Unit tests for individual components
- `integration` - Integration tests for complete workflows
- `mcp` - MCP functionality tests
- `sse` - SSE server tests
- `performance` - Performance and load tests
- `error_handling` - Error scenario tests
- `url_normalization` - URL normalization tests
- `security` - Security-related tests
- `slow` - Long-running tests
- `real_world` - Real-world scenario tests

## Running Tests

### Basic Test Execution

```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_mcp_tools.py

# Run specific test class
python -m pytest tests/test_mcp_tools.py::TestMCPZAPTools

# Run specific test
python -m pytest tests/test_mcp_tools.py::TestMCPZAPTools::test_mcp_zap_health_check_success
```

### Running Tests by Category

```bash
# Run only MCP functionality tests
python -m pytest -m "mcp"

# Run only error handling tests
python -m pytest -m "error_handling"

# Run only URL normalization tests
python -m pytest -m "url_normalization"

# Run only security-related tests
python -m pytest -m "security"

# Run integration tests
python -m pytest -m "integration" --run-integration

# Run performance tests
python -m pytest -m "performance" --run-performance

# Run slow tests
python -m pytest -m "slow" --run-slow
```

### Combining Markers

```bash
# Run MCP tests but exclude slow ones
python -m pytest -m "mcp and not slow"

# Run error handling and performance tests
python -m pytest -m "error_handling or performance" --run-performance

# Run all tests except slow and performance
python -m pytest -m "not slow and not performance"
```

### Test Output Options

```bash
# Quiet output (minimal)
python -m pytest -q

# Show test coverage
python -m pytest --cov=src

# Generate HTML coverage report
python -m pytest --cov=src --cov-report=html

# Show only failed tests
python -m pytest --tb=short

# Show detailed failure information
python -m pytest --tb=long
```

## Test Coverage

### Current Test Statistics

- **Total Tests**: 142
- **Unit Tests**: 94 (MCP tools, ZAP client, URL normalization)
- **Integration Tests**: 13 (Complete workflows)
- **Error Handling Tests**: 28 (Connection, API, timeout, validation errors)
- **Performance Tests**: 13 (Concurrency, load, memory usage)
- **SSE Server Tests**: 27 (Parameter processing, tool execution)

### Coverage Areas

#### MCP Tools (`test_mcp_tools.py`)

- ✅ Health check functionality
- ✅ Spider scan operations
- ✅ Active scan operations
- ✅ Scan status monitoring
- ✅ Alert retrieval and filtering
- ✅ Report generation (HTML/JSON)
- ✅ Session management
- ✅ URL normalization
- ✅ Complete scan workflows
- ✅ Real-world scenarios

#### ZAP Client (`test_zap_client.py`)

- ✅ Connection management
- ✅ API wrapper functions
- ✅ Error handling
- ✅ Async context management
- ✅ Data model validation

#### SSE Server (`test_sse_server.py`)

- ✅ Parameter processing
- ✅ Tool execution
- ✅ URL normalization via random_string
- ✅ Session management
- ✅ Error handling
- ✅ Health and status endpoints

#### Error Scenarios (`test_error_scenarios.py`)

- ✅ Connection failures
- ✅ API errors
- ✅ Timeout scenarios
- ✅ Input validation
- ✅ Data corruption handling
- ✅ Edge cases

#### Performance (`test_performance.py`)

- ✅ Concurrent operations
- ✅ Load testing
- ✅ Memory usage patterns
- ✅ Error recovery performance
- ✅ Scalability scenarios
- ✅ Long-running operations

#### Integration (`test_integration.py`)

- ✅ Complete scan workflows
- ✅ Multi-tool coordination
- ✅ Real-world scenarios
- ✅ End-to-end functionality

## Test Data and Fixtures

### Shared Fixtures

- `mock_zap_client_factory` - Configurable ZAP client mocks
- `sample_security_alerts` - Realistic security findings
- `url_normalization_test_cases` - URL normalization scenarios
- `realistic_scan_results` - Real-world scan data
- `performance_test_data` - Performance testing parameters
- `error_scenarios` - Common error conditions

### Test Data Sources

Tests use realistic data based on actual security scans:

- **Target URLs**: httpbin.org, example.com, example.com
- **Security Findings**: Real vulnerabilities found during testing
- **Scan Results**: Actual ZAP scan outputs
- **Error Conditions**: Real-world failure scenarios

## Continuous Integration

### GitHub Actions

Tests are automatically run on:

- Pull requests
- Pushes to main branch
- Scheduled runs (daily)

### Test Matrix

- Python versions: 3.11, 3.12
- Operating systems: Ubuntu, macOS, Windows
- Test categories: Unit, Integration, Performance

## Development Guidelines

### Adding New Tests

1. **Choose the appropriate test file** based on functionality
2. **Use descriptive test names** that explain what is being tested
3. **Include docstrings** explaining the test purpose
4. **Use appropriate fixtures** from conftest.py
5. **Add markers** for test categorization
6. **Mock external dependencies** (ZAP API calls)
7. **Test both success and failure scenarios**

### Test Naming Convention

```python
def test_[component]_[action]_[expected_result]():
    """Test [component] [action] [expected_result]."""
```

Examples:

- `test_mcp_zap_health_check_success()`
- `test_spider_scan_connection_error()`
- `test_url_normalization_edge_cases()`

### Mock Usage

```python
@pytest.fixture
def mock_zap_client():
    with patch("src.owasp_zap_mcp.tools.zap_tools.ZAPClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.health_check.return_value = True
        mock_client_class.return_value.__aenter__.return_value = mock_client
        yield mock_client
```

### Async Test Pattern

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result["success"] is True
```

## Troubleshooting

### Common Issues

1. **Tests fail with connection errors**
   - Ensure ZAP is not required to be running for unit tests
   - Check that mocks are properly configured

2. **Async test failures**
   - Verify `@pytest.mark.asyncio` decorator is present
   - Check event loop configuration

3. **Import errors**
   - Ensure PYTHONPATH includes the src directory
   - Check relative imports in test files

4. **Fixture not found**
   - Verify fixture is defined in conftest.py
   - Check fixture scope and dependencies

### Debug Mode

```bash
# Run tests with debug output
python -m pytest -s -vv --tb=long

# Run single test with debugging
python -m pytest tests/test_mcp_tools.py::test_health_check -s -vv

# Show test setup and teardown
python -m pytest --setup-show
```

## Contributing

When contributing new tests:

1. Follow the existing test structure and patterns
2. Add appropriate test markers
3. Include both positive and negative test cases
4. Update this README if adding new test categories
5. Ensure tests pass in CI environment

## Performance Benchmarks

### Current Performance Targets

- Health check: < 1 second
- Spider scan start: < 2 seconds
- Alert retrieval: < 3 seconds
- Concurrent operations (10x): < 5 seconds
- Large dataset processing (1000 alerts): < 5 seconds

### Running Performance Tests

```bash
# Run all performance tests
python -m pytest -m "performance" --run-performance

# Run specific performance category
python -m pytest tests/test_performance.py::TestConcurrentOperations --run-performance

# Run with timing information
python -m pytest -m "performance" --run-performance --durations=10
```
