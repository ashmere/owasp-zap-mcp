# Development Tips for AI Assistants

This document provides essential information for AI assistants working with the OWASP ZAP MCP server codebase.

## Quick Reference

### Key Commands

```bash
# Test everything
./scripts/test.sh

# Start environment
./scripts/start.sh --type build

# Run specific tests
pytest -xvs tests/test_mcp_interface.py::test_mcp_tool_call

# Debug with verbose logging
LOG_LEVEL=DEBUG ./scripts/start.sh --type build
```

### Important Files

- `src/owasp_zap_mcp/config.py` - Configuration and logging setup
- `src/owasp_zap_mcp/main.py` - SSE server entry point
- `src/owasp_zap_mcp/sse_server.py` - MCP interface implementation
- `src/owasp_zap_mcp/tools/zap_tools.py` - ZAP tool implementations
- `tests/test_mcp_interface.py` - Core MCP integration tests

### Environment Variables

```bash
LOG_LEVEL=DEBUG          # Enable debug logging
ZAP_BASE_URL=http://zap:8080
SERVER_HOST=0.0.0.0
SERVER_PORT=3000
```

## Logging and Debugging

### Overview

The project implements a comprehensive logging system with configurable log levels to help with debugging and troubleshooting.

### Log Levels

| Level | Usage | Output |
|-------|--------|--------|
| `DEBUG` | Detailed tracing, parameter processing, internal state | All operations with timing and parameters |
| `INFO` | Normal operations, scan status, tool registration | Key milestones and status updates |
| `WARNING` | Configuration issues, minor errors | Non-critical issues that should be reviewed |
| `ERROR` | Failed operations, connection issues | Critical errors requiring attention |
| `CRITICAL` | Fatal errors, startup failures | System-breaking issues |

### Setting Log Level

**Environment Variable (Recommended)**:

```bash
export LOG_LEVEL=DEBUG
./scripts/start.sh --type build
```

**Docker Environment**:

```bash
# In docker-compose.yml or .env
LOG_LEVEL=DEBUG

# Or inline
LOG_LEVEL=DEBUG docker-compose up
```

**Dockerfile Default**:

```dockerfile
ENV LOG_LEVEL=INFO  # Default in container
```

### Debug Logging Examples

**Tool Registration**:

```
2024-01-15 10:30:01 - owasp-zap-tools-initializer - DEBUG - [register_mcp_tools:45] - Registering tool: zap_health_check
2024-01-15 10:30:01 - owasp-zap-tools-initializer - INFO - [register_mcp_tools:102] - ✅ All tools registered successfully!
```

**ZAP Client Operations**:

```
2024-01-15 10:30:05 - owasp-zap-client - DEBUG - [connect:67] - Parsed ZAP URL - Host: zap, Port: 8080
2024-01-15 10:30:05 - owasp-zap-client - INFO - [connect:78] - ✅ ZAP client initialized successfully
2024-01-15 10:30:06 - owasp-zap-client - INFO - [health_check:95] - ✅ ZAP health check passed - Version: 2.14.0 (took 0.15s)
```

**MCP Interface**:

```
2024-01-15 10:30:10 - owasp-zap-mcp-sse - DEBUG - [_process_tool_arguments:712] - Processing arguments for mcp_zap_spider_scan: original={'random_string': 'example.com'}, recent_query='None'
2024-01-15 10:30:10 - owasp-zap-mcp-sse - INFO - [_process_tool_arguments:742] - Using random_string/recent_query as URL for mcp_zap_spider_scan: https://example.com
```

### Troubleshooting with Logs

**Common Debugging Scenarios**:

1. **Tool Registration Issues**:

   ```bash
   LOG_LEVEL=DEBUG ./scripts/start.sh --type build
   # Look for: "Failed to register tool" messages
   ```

2. **ZAP Connection Problems**:

   ```bash
   LOG_LEVEL=DEBUG ./scripts/start.sh --type build
   # Look for: "ZAP health check failed" or connection errors
   ```

3. **MCP Parameter Processing**:

   ```bash
   LOG_LEVEL=DEBUG ./scripts/start.sh --type build
   # Look for: "_process_tool_arguments" debug messages
   ```

4. **Scan Execution Issues**:

   ```bash
   LOG_LEVEL=DEBUG ./scripts/start.sh --type build
   # Look for: Spider/Active scan start/status messages
   ```

### Log Output Locations

**Console Output**: All logs go to stdout/stderr for container compatibility

**Testing Logs**: Pytest captures logs automatically:

```bash
pytest -xvs --log-cli-level=DEBUG tests/
```

**Docker Logs**:

```bash
docker-compose logs -f owasp-zap-mcp
docker-compose logs -f zap
```

### Key Logger Names

| Logger | Purpose | When to Monitor |
|--------|---------|-----------------|
| `owasp-zap-mcp-config` | Configuration and startup | Environment issues |
| `owasp-zap-mcp-main` | SSE server main entry | Server startup problems |
| `owasp-zap-mcp-sse` | MCP interface operations | MCP communication issues |
| `owasp-zap-client` | ZAP API operations | ZAP connectivity/scan issues |
| `owasp-zap-tools-initializer` | Tool registration | Tool availability problems |
| `owasp-zap-tools` | Individual tool execution | Specific tool failures |

### Performance Monitoring

**Timing Information** (DEBUG level):

- ZAP API call durations
- Tool execution timing  
- MCP message processing time
- Scan status check intervals

**Resource Usage** (DEBUG level):

- Memory usage for large reports
- Network request timing
- Scan progress percentages

### Best Practices

1. **Start with INFO**: Normal operation monitoring
2. **Use DEBUG for Issues**: When troubleshooting specific problems
3. **Monitor Startup**: Check tool registration and ZAP connectivity
4. **Check Timing**: Look for performance bottlenecks in DEBUG logs
5. **Filter by Logger**: Focus on specific components when debugging

### Integration with Development Workflow

**During Development**:

```bash
export LOG_LEVEL=DEBUG
./scripts/start.sh --type build
# Watch logs in another terminal
docker-compose logs -f owasp-zap-mcp
```

**For Testing**:

```bash
LOG_LEVEL=DEBUG pytest -xvs tests/test_specific_issue.py
```

**For Production**:

```bash
LOG_LEVEL=INFO  # Default, balanced information
```

## Testing Framework

### Test Structure

The project uses pytest with custom markers for test organization:

```python
@pytest.mark.integration
@pytest.mark.mcp
class TestMCPInterface:
    """Integration tests for MCP functionality"""
```

### Key Test Categories

**Unit Tests** (`@pytest.mark.unit`):

- Individual function testing
- Mock-based testing
- Fast execution

**Integration Tests** (`@pytest.mark.integration`):

- End-to-end functionality
- Real service interaction
- Requires running environment

**MCP Tests** (`@pytest.mark.mcp`):

- MCP protocol compliance
- Tool registration verification
- Parameter processing

**SSE Tests** (`@pytest.mark.sse`):

- Server-Sent Events functionality
- Session management
- HTTP endpoint testing

### Running Tests

**All Tests**:

```bash
./scripts/test.sh
```

**Specific Categories**:

```bash
pytest -m unit
pytest -m integration
pytest -m "mcp and not slow"
```

**Individual Tests**:

```bash
pytest -xvs tests/test_mcp_interface.py::TestMCPInterfaceRegression::test_mcp_session_auto_creation
```

### When to Update Tests

1. **New Tool Added**: Update `test_tool_initializer.py`
2. **Parameter Processing Changed**: Update `test_sse_server.py`
3. **New MCP Feature**: Add to `test_mcp_interface.py`
4. **Bug Fix**: Add regression test to prevent recurrence

### Test Environment Requirements

**For Integration Tests**:

- ZAP container running on localhost:8080
- MCP server running on localhost:3000
- Network connectivity between services

**Environment Setup**:

```bash
./scripts/start.sh --type build
# Wait for services to be ready
./scripts/test.sh
```

## MCP Interface Patterns

### Parameter Processing

The SSE server implements smart parameter processing for MCP tools:

**URL Processing**:

```python
# Input: random_string = "example.com"
# Output: url = "https://example.com"

# Input: random_string = "https://api.github.com/user"
# Output: url = "https://api.github.com/user" (unchanged)
```

**Scan ID Extraction**:

```python
# Input: random_string = "scan id is 123"
# Output: scan_id = "123"

# Input: random_string = "456"
# Output: scan_id = "456"
```

**Risk Level Detection**:

```python
# Input: random_string = "show me high risk alerts"
# Output: risk_level = "High"
```

### Tool Registration Pattern

All tools follow this pattern:

```python
@mcp.tool(name="tool_name", description="Tool description")
async def tool_wrapper(**kwargs):
    """MCP tool wrapper that defers to SSE server parameter processing"""
    raise RuntimeError(
        f"Tool should be called via SSE server parameter processing"
    )

# Store actual function reference
tool_wrapper.actual_function = actual_tool_function
tool_wrapper.parameters = parameter_schema
```

### Session Management

**Auto-Creation**: Sessions are created automatically when needed
**Cleanup**: Idle sessions are cleaned up after 5 minutes
**Persistence**: Sessions persist across multiple tool calls

## Architecture Notes

### File Organization

```
src/owasp_zap_mcp/
├── config.py              # Configuration and logging
├── main.py                 # SSE server entry point  
├── mcp_core.py            # Stdio mode handler
├── sse_server.py          # MCP SSE implementation
├── zap_client.py          # ZAP API wrapper
└── tools/
    ├── tool_initializer.py # Tool registration
    ├── zap_tools.py       # ZAP tool implementations
    └── proxy_tools.py     # Proxy configuration tools
```

### Key Design Patterns

**Async Context Managers**: ZAP client uses `async with`
**Decorator Pattern**: MCP tool registration
**Strategy Pattern**: Different parameter processing strategies
**Factory Pattern**: Tool creation and registration

### Error Handling

**Graceful Degradation**: Continue with partial functionality when possible
**Detailed Logging**: Log errors with context for debugging
**User-Friendly Messages**: Return helpful error messages to users
**Retry Logic**: Implement retries for transient failures where appropriate

## Common Issues and Solutions

### ZAP Connection Issues

**Problem**: "ZAP health check failed"
**Solution**:

1. Check ZAP container is running
2. Verify ZAP_BASE_URL configuration
3. Check network connectivity
4. Enable DEBUG logging to see connection details

### Tool Registration Failures

**Problem**: Tools not available in MCP client
**Solution**:

1. Check tool registration logs
2. Verify all imports are working
3. Check for circular import issues
4. Ensure function signatures are correct

### Parameter Processing Issues

**Problem**: Parameters not being extracted correctly
**Solution**:

1. Enable DEBUG logging for parameter processing
2. Check `_process_tool_arguments` logic
3. Verify regular expressions for pattern matching
4. Test with known good inputs

### Test Failures

**Problem**: Integration tests failing
**Solution**:

1. Verify environment is running (`./scripts/start.sh`)
2. Check service health endpoints
3. Look for port conflicts
4. Check Docker container logs

## Performance Considerations

### Scanning Performance

- Spider scans: Configure appropriate max_depth
- Active scans: Monitor thread count and duration
- Large targets: Consider scan policies to limit scope

### Memory Usage

- Reports: Large HTML/JSON reports can consume significant memory
- Sessions: Clean up unused sessions to prevent memory leaks
- Logging: DEBUG logging increases memory usage

### Network Performance

- ZAP API: Multiple concurrent requests can impact performance
- Container networking: Use container names for service communication
- Timeouts: Configure appropriate timeouts for long-running scans

## Development Workflow

### Making Changes

1. **Update Code**: Make changes to source files
2. **Update Tests**: Add/modify tests for new functionality
3. **Test Locally**: Run test suite to verify changes
4. **Check Logs**: Use DEBUG logging to verify behavior
5. **Integration Test**: Test with real environment

### Adding New Tools

1. **Implement Function**: Add to `zap_tools.py`
2. **Register Tool**: Add to `tool_initializer.py`
3. **Add Tests**: Create unit and integration tests
4. **Update Documentation**: Update tool lists and examples
5. **Test MCP Interface**: Verify parameter processing works

### Debugging Workflow

1. **Reproduce Issue**: Create minimal test case
2. **Enable Debug Logging**: Set LOG_LEVEL=DEBUG
3. **Trace Execution**: Follow logs through the call stack
4. **Identify Root Cause**: Look for error patterns
5. **Fix and Test**: Implement fix and verify with tests
6. **Add Regression Test**: Prevent issue from recurring

## Links

- [Development Guide](development.md) - Comprehensive development information
- [Docker Guide](docker.md) - Container setup and configuration
- [Scripts Guide](scripts.md) - Available scripts and usage
- [Architecture Guide](architecture.md) - System architecture details

## Manual/Debug Scripts

All manual and debug scripts are now located in the scripts/ directory. They use a sys.path hack at the top to ensure imports work with the src layout, regardless of the working directory.

To run a manual/debug script:

```bash
python scripts/manual_integration_script.py
python scripts/test_mcp_params.py
python scripts/test_sse_params.py
```

No need to set PYTHONPATH manually.
