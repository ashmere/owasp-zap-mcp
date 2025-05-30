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
The SSE server must handle MCP interface limitations where only `random_string` parameter is available:

```python
def _process_tool_arguments(self, tool_name, arguments, recent_query):
    """Process tool parameters with random_string fallback"""
    processed_args = dict(arguments)
    
    if "random_string" in processed_args and tool_name.startswith("mcp_zap_"):
        random_string = processed_args.pop("random_string", "")
        
        # URL extraction for spider_scan, active_scan, scan_summary
        if tool_name in ["mcp_zap_spider_scan", "mcp_zap_active_scan", "mcp_zap_scan_summary"]:
            if not processed_args.get("url"):
                # Extract URL or convert domain to https://
                url_fallback = extract_or_convert_url(random_string)
                if url_fallback:
                    processed_args["url"] = url_fallback
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
- ✅ **Always implement**: Fallback parameter extraction following Doris pattern
- **Test both**: Direct function calls AND MCP interface calls

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

## 📚 **Reference Materials**

### **Key Files to Study**
1. `research/doris-mcp-server/doris_mcp_server/sse_server.py` - Parameter processing patterns
2. `owasp_zap_mcp/src/owasp_zap_mcp/sse_server.py` - Current implementation
3. `owasp_zap_mcp/src/owasp_zap_mcp/tools/zap_tools.py` - Tool implementations

### **Documentation**
- `docs/architecture.md` - System architecture
- `docs/threatmodel.md` - Security considerations
- `README.md` - Setup and usage instructions

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

## ⚠️ **Critical Reminders**

1. **Always** use sequential thinking for complex problems
2. **Never** break Apache Doris MCP server patterns
3. **Always** test parameter processing with `random_string`
4. **Never** use deprecated `docker-compose` syntax
5. **Always** verify container health before testing
6. **Never** add unauthorized system packages to containers
7. **Always** implement proper error handling and logging
8. **Never** ignore user-specific requirements or constraints

---

*This document should be updated whenever significant patterns or lessons are learned during development.* 
 