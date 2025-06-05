# Development Tips for AI Assistants

## OWASP ZAP MCP Implementation

This document contains critical development tips and lessons learned for AI assistants working on the OWASP ZAP MCP implementation. It's designed to prevent common mistakes and ensure consistent, high-quality development practices.

## 🎯 **Core Principles**

### 1. **Always Follow Apache Doris MCP Server Patterns**

- **Reference Implementation**: `research/doris-mcp-server/` contains the trusted Apache Foundation MCP server
- **Key Pattern**: Parameter processing with `_process_tool_arguments` and `_extract_recent_query` methods
- **Never deviate** from these patterns without explicit user approval
- **Import Structure**: Study how Doris handles tool registration, parameter processing, and error handling

### 2. **Sequential Thinking for Complex Problems**

- **Always use** `mcp_sequential-thinking_sequentialthinking` tool for multi-step problems
- **Break down** complex issues into logical steps
- **Document** your reasoning process for future reference
- **Verify** each step before proceeding to the next

### 3. **Comprehensive Testing is Mandatory**

- **Test Coverage**: 135+ tests with 109 passing, 26 skipped (requiring flags)
- **Test First**: Review existing tests before making changes
- **Update Tests**: Always update tests when modifying code
- **Test Categories**: Unit, integration, error handling, performance, SSE server

## 🧪 **Testing Guidelines**

### **Test Structure Overview**

The project has a comprehensive test suite organized as follows:

```
tests/
├── test_mcp_tools.py        # 60+ tests for MCP tool functions and URL normalization
├── test_zap_client.py       # ZAP client wrapper tests  
├── test_sse_server.py       # 27 tests for SSE server parameter processing
├── test_integration.py      # 13 integration tests for complete workflows
├── test_error_scenarios.py  # 28 error handling and edge case tests
├── test_performance.py      # 13 performance and concurrency tests
├── conftest.py             # Shared fixtures and pytest configuration
├── pytest.ini             # Test markers and configuration
└── README.md               # Comprehensive test documentation
```

### **When Making Code Changes**

#### **ALWAYS Update Tests When:**

1. **Adding new tool functions** → Add tests to `test_mcp_tools.py`
2. **Modifying ZAP client** → Update `test_zap_client.py`
3. **Changing SSE parameter processing** → Update `test_sse_server.py`
4. **Adding error handling** → Add to `test_error_scenarios.py`
5. **Performance-critical changes** → Add to `test_performance.py`
6. **Complete workflow changes** → Update `test_integration.py`

#### **Test Running Commands**

```bash
# ALWAYS run these after making changes
cd owasp_zap_mcp

# Quick test run (recommended first)
python -m pytest -q

# Full test run with markers
python -m pytest -v

# Test specific categories
python -m pytest -m "mcp"              # MCP functionality
python -m pytest -m "error_handling"   # Error scenarios  
python -m pytest -m "url_normalization" # URL normalization
python -m pytest -m "security"         # Security-related

# Performance tests (need flag)
python -m pytest -m "performance" --run-performance

# Integration tests (need flag)  
python -m pytest -m "integration" --run-integration

# Coverage report
python -m pytest --cov=src/owasp_zap_mcp --cov-report=term-missing
```

#### **Test Patterns to Follow**

**For MCP Tool Functions:**

```python
@pytest.mark.asyncio
async def test_mcp_zap_new_tool_success(self, mock_zap_client):
    """Test new MCP tool success scenario."""
    # Mock the ZAP client response
    mock_zap_client.new_operation.return_value = "expected_result"

    # Call the tool function
    result = await mcp_zap_new_tool("test_parameter")

    # Verify MCP response format
    assert result["content"][0]["text"]
    response_data = json.loads(result["content"][0]["text"])
    assert response_data["success"] is True

    # Verify ZAP client was called correctly
    mock_zap_client.new_operation.assert_called_with("test_parameter")
```

**For Error Scenarios:**

```python
@pytest.mark.asyncio
async def test_new_tool_connection_error(self, mock_zap_client):
    """Test new tool when ZAP connection fails."""
    mock_zap_client.new_operation.side_effect = ConnectionError("ZAP not running")

    result = await mcp_zap_new_tool("test_parameter")

    response_data = json.loads(result["content"][0]["text"])
    assert response_data["success"] is False
    assert "ZAP not running" in response_data["error"]
```

**For Parameter Processing:**

```python
def test_process_tool_arguments_new_parameter(self, sse_server):
    """Test processing new parameter type from random_string."""
    args = {"random_string": "test_input_pattern"}
    result = sse_server._process_tool_arguments("mcp_zap_new_tool", args, None)

    assert result["extracted_param"] == "expected_value"
    assert "random_string" not in result
```

### **Performance Benchmarks to Maintain**

When making changes, ensure these performance targets are met:

- Health check: < 1 second
- Spider scan start: < 2 seconds  
- Alert retrieval: < 3 seconds
- Concurrent operations (10x): < 5 seconds
- Large dataset processing (1000 alerts): < 5 seconds

### **Test Fixtures and Helpers**

Use these shared fixtures from `conftest.py`:

- `mock_zap_client_factory` - Configurable ZAP client mocks
- `sample_security_alerts` - Realistic security findings
- `url_normalization_test_cases` - URL normalization scenarios
- `realistic_scan_results` - Real-world scan data
- `performance_test_data` - Performance testing parameters
- `error_scenarios` - Common error conditions

## 🏗️ **Architecture Understanding**

### **Project Structure**

```
owasp_zap_mcp/
├── src/owasp_zap_mcp/
│   ├── mcp_core.py          # Core MCP instance (stdio_mcp)
│   ├── sse_server.py        # SSE/HTTP server implementation
│   ├── tools/               # Tool implementations
│   │   ├── tool_initializer.py  # Tool registration
│   │   └── zap_tools.py     # Individual tool functions
│   ├── zap_client.py        # ZAP API client
│   └── config.py            # Configuration management
├── docker-compose.yml       # Container orchestration
├── Dockerfile              # Container build
└── docs/                   # Documentation
```

### **Key Components**

1. **MCP Core** (`mcp_core.py`): Contains `stdio_mcp` instance
2. **SSE Server** (`sse_server.py`): Handles HTTP/SSE transport with parameter processing
3. **Tools** (`tools/`): Individual ZAP tool implementations
4. **Client** (`zap_client.py`): ZAP API communication layer

## 🔧 **Critical Implementation Details**

### **Parameter Processing (CRITICAL)**

The SSE server must handle MCP interface limitations where only `random_string` parameter is available. Recent improvements (v0.3.2) include robust error handling and URL extraction:

```python
def _process_tool_arguments(self, tool_name, arguments, recent_query):
    """Process tool parameters with random_string fallback and error handling"""
    processed_args = dict(arguments)

    # Handle empty arguments case (v0.3.2 fix)
    if not arguments or not arguments.get("random_string"):
        # Try to extract URL from recent_query as fallback
        if recent_query and tool_name in ["mcp_zap_spider_scan", "mcp_zap_active_scan", "mcp_zap_scan_summary"]:
            extracted_url = self._extract_url_from_text(recent_query)
            if extracted_url:
                processed_args["url"] = extracted_url
                return processed_args

        # Return helpful error message if no URL can be determined
        return None  # Triggers helpful error message in call_tool

    if "random_string" in processed_args and tool_name.startswith("mcp_zap_"):
        random_string = processed_args.pop("random_string", "")

        # URL extraction for spider_scan, active_scan, scan_summary
        if tool_name in ["mcp_zap_spider_scan", "mcp_zap_active_scan", "mcp_zap_scan_summary"]:
            if not processed_args.get("url"):
                # Extract URL using improved regex patterns (v0.3.2)
                url_fallback = self._extract_url_from_text(random_string)
                if url_fallback:
                    processed_args["url"] = url_fallback
```

### **URL Extraction Improvements (v0.3.2)**

The `_extract_url_from_text` method now includes robust URL pattern matching:

```python
def _extract_url_from_text(self, text):
    """Extract URL from text using improved patterns (v0.3.2)"""
    if not text:
        return None

    import re

    # First try to find complete URLs
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    url_matches = re.findall(url_pattern, text)
    if url_matches:
        return url_matches[0]

    # Then try to find domain patterns and add https://
    # Improved domain pattern matching (v0.3.2)
    domain_pattern = r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b'
    domain_matches = re.findall(domain_pattern, text)
    if domain_matches:
        return f"https://{domain_matches[0]}"

    return None
```

### **Tool Function Signatures**

- **Direct functions**: `async def mcp_zap_spider_scan(url: str, max_depth: int = 5)`
- **MCP interface**: Only receives `{"random_string": "value"}`
- **Solution**: Parameter processing extracts meaningful data from `random_string`

### **Error Handling Patterns**

```python
try:
    # Tool execution
    result = await tool_function(**processed_args)
    logger.info(f"Tool {tool_name} executed successfully")
    return result
except Exception as e:
    logger.error(f"Error in call_tool for {tool_name}: {str(e)}", exc_info=True)
    raise ValueError(f"Tool execution failed: {str(e)}")
```

## 🚨 **Common Mistakes to Avoid**

### **1. Docker Compose Commands**

- ❌ **NEVER use**: `docker-compose` (deprecated)
- ✅ **ALWAYS use**: `docker compose` (modern syntax)
- **Update all scripts** and documentation accordingly

### **2. Container Dependencies**

- ❌ **Don't add**: `build-essential` to Dockerfile (user specifically requested removal)
- ✅ **Keep minimal**: Only essential packages for Python and networking
- **Check user requirements** before adding system packages

### **3. Parameter Processing**

- ❌ **Don't ignore**: `random_string` parameter in MCP interface
- ❌ **Don't assume**: Arguments will always contain `random_string` (v0.3.2 fix)
- ✅ **Always implement**: Fallback parameter extraction following Doris pattern
- ✅ **Always handle**: Empty arguments `{}` case with helpful error messages
- **Test both**: Direct function calls AND MCP interface calls
- **Test edge cases**: Empty arguments, malformed URLs, missing parameters

### **4. Import Patterns**

- ❌ **Wrong**: `from owasp_zap_mcp.server import create_mcp_server` (deprecated)
- ✅ **Correct**: `from owasp_zap_mcp.mcp_core import stdio_mcp`
- **Use**: `from owasp_zap_mcp.tools.tool_initializer import register_mcp_tools`

### **5. Environment Configuration**

- ❌ **Don't assume**: Default ZAP URLs work in all environments
- ✅ **Always check**: `ZAP_BASE_URL` and container networking
- **Verify**: Container health before running tools

### **6. Rebuild Script Consistency**

- ❌ **Wrong**: Build `owasp-zap-mcp-build` service then use `security` profile (uses different service)
- ✅ **Correct**: Use `./scripts/rebuild.sh --type build` for build-dev profile
- ✅ **Correct**: Use `./scripts/rebuild.sh --type image` for security profile (default)
- **Always match**: Build step with corresponding Docker Compose profile

### **7. Testing Mistakes**

- ❌ **Don't skip**: Test updates when modifying code
- ❌ **Don't ignore**: Failing tests or reduced coverage
- ❌ **Don't forget**: To test both direct calls and MCP interface
- ✅ **Always run**: Full test suite before submitting changes
- ✅ **Always add**: Error scenario tests for new functionality
- ✅ **Always maintain**: Performance benchmarks

## 🧪 **Testing Strategies**

### **Multi-Level Testing**

1. **Direct Tool Functions**: Test individual tool functions with proper parameters
2. **SSE Parameter Processing**: Test parameter extraction from `random_string`
3. **Container Integration**: Test full Docker Compose stack
4. **End-to-End**: Test complete security scanning workflows

### **Test Script Patterns**

```python
# Test direct functions
result = await mcp_zap_spider_scan(url='https://example.com')

# Test SSE parameter processing
result = await sse_server.call_tool(
    "zap_spider_scan",
    {"random_string": "https://example.com"},
    mock_request
)
```

### **Container Testing**

```bash
# Rebuild and test with pre-built image (default)
./scripts/rebuild.sh

# Rebuild and test with source build
./scripts/rebuild.sh --type build

# Manual rebuild commands
docker compose build --no-cache owasp-zap-mcp-build  # For build mode
docker compose --profile security up -d              # For image mode  
docker compose --profile build-dev up -d             # For build mode
docker exec owasp-zap-mcp-build python test_script.py
```

### **Rebuild Script Usage**

The `scripts/rebuild.sh` script supports two modes:

- `--type image` (default): Uses pre-built image with security profile
- `--type build`: Builds from source with build-dev profile

**CRITICAL**: Always ensure consistency between build step and profile:

- ❌ **Wrong**: Build `owasp-zap-mcp-build` then use `security` profile
- ✅ **Correct**: Build `owasp-zap-mcp-build` then use `build-dev` profile
- ✅ **Correct**: Skip build then use `security` profile with pre-built image

## 📋 **Development Workflow**

### **1. Problem Analysis**

- Use sequential thinking for complex issues
- Identify root cause before implementing fixes
- Check Apache Doris patterns for similar solutions

### **2. Implementation**

- Follow existing code patterns
- Implement parameter processing for new tools
- Add proper error handling and logging

### **3. Testing**

- Test direct functions first
- Test SSE parameter processing
- Verify container integration
- Run full end-to-end tests

### **4. Documentation**

- Update relevant documentation
- Add code comments for complex logic
- Document any deviations from standard patterns

## 🔍 **Debugging Tips**

### **Container Logs**

```bash
# Check container status
docker compose ps

# View logs
docker compose logs owasp-zap-mcp-build
docker compose logs zap

# Interactive debugging
docker exec -it owasp-zap-mcp-build bash
```

### **Parameter Processing Debug**

- Add debug logging in `_process_tool_arguments`
- Check `random_string` content and extraction logic
- Verify URL pattern matching and conversion

### **Tool Registration Debug**

- Verify tools are registered: `await mcp_server.list_tools()`
- Check tool names match mapping in `call_tool`
- Ensure tool functions are importable

## 🎯 **Performance Considerations**

### **Container Optimization**

- Use multi-stage builds for smaller images
- Cache pip dependencies appropriately
- Minimize system package installations

### **ZAP Integration**

- Implement proper connection pooling
- Handle ZAP startup delays gracefully
- Use health checks before tool execution

## 🔐 **Security Best Practices**

### **Environment Variables**

- Never hardcode sensitive values
- Use proper environment variable precedence
- Document required vs optional configuration

### **Container Security**

- Run with minimal privileges
- Use specific base image versions
- Regularly update dependencies

## 📚 **Reference Materials & Documentation Files**

### **Key Files to Study**

1. `research/doris-mcp-server/doris_mcp_server/sse_server.py` - Parameter processing patterns
2. `owasp_zap_mcp/src/owasp_zap_mcp/sse_server.py` - Current implementation
3. `owasp_zap_mcp/src/owasp_zap_mcp/tools/zap_tools.py` - Tool implementations

### **Critical Documentation Files to Update**

When making changes, **ALWAYS** consider updating these files:

#### **Core Documentation:**

- **`README.md`** - Main project documentation, setup instructions
- **`docs/development.md`** - Development guide with testing info  
- **`docs/architecture.md`** - System architecture and design
- **`docs/docker.md`** - Container setup and configuration
- **`docs/scripts.md`** - Development scripts documentation
- **`docs/threatmodel.md`** - Security considerations
- **`docs/development-tips.ai.md`** - This file - AI assistant guidelines

#### **Test Documentation:**

- **`owasp_zap_mcp/tests/README.md`** - Comprehensive test documentation
- **`owasp_zap_mcp/pytest.ini`** - Test configuration and markers
- **`owasp_zap_mcp/tests/conftest.py`** - Test fixtures and configuration

#### **Configuration Files:**

- **`docker-compose.yml`** - Container orchestration
- **`Dockerfile`** - Container build instructions
- **`owasp_zap_mcp/requirements.txt`** - Python dependencies
- **`owasp_zap_mcp/pyproject.toml`** - Project configuration

#### **Script Documentation:**

- **`scripts/rebuild.sh`** - Container rebuild automation
- **`scripts/test.sh`** - Integration testing script
- **`scripts/start.sh`** - Environment startup
- **`scripts/stop.sh`** - Environment shutdown

### **Documentation Update Checklist**

When making changes, check these documentation areas:

#### **For New Features:**

- [ ] Update `README.md` with new capabilities
- [ ] Add to `docs/development.md` if development-related
- [ ] Update `docs/architecture.md` if architectural changes
- [ ] Add test documentation to `tests/README.md`
- [ ] Update API documentation if tools change

#### **For Bug Fixes:**

- [ ] Document the fix in relevant files
- [ ] Update troubleshooting sections
- [ ] Add to test documentation if test changes made

#### **For Performance Changes:**

- [ ] Update performance benchmarks in documentation
- [ ] Document new performance considerations
- [ ] Update `test_performance.py` and its documentation

#### **For Security Changes:**

- [ ] Update `docs/threatmodel.md`
- [ ] Review and update security documentation
- [ ] Update container security considerations

## 🚀 **Future Development Guidelines**

### **Adding New Tools**

1. Implement in `zap_tools.py` with proper async signature
2. Register in `tool_initializer.py`
3. Add parameter processing logic in `sse_server.py`
4. Create comprehensive tests
5. Update documentation

### **Modifying Existing Tools**

1. Maintain backward compatibility
2. Update parameter processing if signature changes
3. Test both direct and MCP interface calls
4. Update relevant documentation

### **Infrastructure Changes**

1. Follow Apache Doris patterns
2. Test with full container rebuild
3. Verify environment variable handling
4. Update deployment documentation

## ⚠️ DO NOT BREAK WORKING CODE: Test-Driven Guidance for AI Assistants

- All report generation via MCP tools **must** result in pure, valid ZAP HTML and JSON files in `/reports` (not JSON-RPC envelopes or empty files).
- The integration script (`scripts/manual_integration_script.py`) now enforces this: it extracts the report content and writes it as the final file, and checks validity (HTML starts with `<!DOCTYPE html>`, JSON parses as a dict).
- Future changes **must not break** this contract. If the reports are not valid, the test and integration script will fail.
- A dedicated test now checks for this issue to prevent regressions.

---

*This document should be updated whenever significant patterns or lessons are learned during development. The test suite provides excellent examples of usage patterns and expected behaviors - always consult it when making changes.*

## Manual/Debug Scripts

All manual and debug scripts are now located in the scripts/ directory. They use a sys.path hack at the top to ensure imports work with the src layout, regardless of the working directory.

To run a manual/debug script:

```bash
python scripts/manual_integration_script.py
python scripts/test_mcp_params.py
python scripts/test_sse_params.py
```

No need to set PYTHONPATH manually.
