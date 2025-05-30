# OWASP ZAP MCP Development Guide

A comprehensive guide for developing and contributing to the OWASP ZAP MCP (Model Context Protocol) integration project.

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Project Overview](#️-project-overview)
- [Development Environment Setup](#️-development-environment-setup)
- [Testing](#-testing)
- [Making Changes](#-making-changes)
- [Performance & Quality](#-performance--quality)
- [Troubleshooting](#-troubleshooting)

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Git

### Setup Commands

```bash
# Clone and setup
git clone <repository-url>
cd owasp-zap-mcp

# Start development environment
./scripts/dev-setup.sh
./scripts/start.sh

# Run tests
cd owasp_zap_mcp
python -m pytest

# Stop environment
./scripts/stop.sh
```

## 🏗️ Project Overview

### Core Components

- **MCP Server** (`src/owasp_zap_mcp/mcp_core.py`) - Core MCP implementation
- **SSE Server** (`src/owasp_zap_mcp/sse_server.py`) - HTTP/SSE transport layer
- **ZAP Client** (`src/owasp_zap_mcp/zap_client.py`) - OWASP ZAP API wrapper
- **Tools** (`src/owasp_zap_mcp/tools/`) - Individual security scanning tools
- **Configuration** (`src/owasp_zap_mcp/config.py`) - Environment configuration

### Project Structure

```
owasp-zap-mcp/
├── src/owasp_zap_mcp/           # Core application code
│   ├── mcp_core.py              # MCP server instance
│   ├── sse_server.py            # SSE/HTTP server
│   ├── zap_client.py            # ZAP API client
│   ├── config.py                # Configuration
│   └── tools/                   # MCP tools
├── tests/                       # Comprehensive test suite
├── scripts/                     # Development & deployment scripts
├── docs/                        # Documentation
├── docker-compose.yml           # Container orchestration
└── Dockerfile                   # Container definition
```

## 🛠️ Development Environment Setup

### Option 1: Docker Development (Recommended)

```bash
# Setup development environment
./scripts/dev-setup.sh

# Start with pre-built image (fast)
./scripts/start.sh

# Or start with source build (for development)
./scripts/rebuild.sh --type build
```

### Option 2: Local Development

```bash
cd owasp_zap_mcp
pip install -r requirements.txt
pip install -e .

# Start ZAP separately
docker run -d -p 8080:8080 zaproxy/zap-stable:latest -daemon -host 0.0.0.0 -port 8080 -config api.addrs.addr.name=.* -config api.addrs.addr.regex=true

# Run MCP server
python run.py
```

## 🧪 Testing

### Test Organization

The project has a comprehensive test suite with **135+ tests** covering:

- **Unit Tests** (94) - Individual component testing
- **Integration Tests** (13) - End-to-end workflows
- **Error Handling Tests** (28) - Error scenarios and edge cases
- **Performance Tests** (13) - Concurrency and load testing
- **SSE Server Tests** (27) - Parameter processing and session management

### Test Files Structure

```
tests/
├── test_mcp_tools.py        # MCP tool functions and URL normalization
├── test_zap_client.py       # ZAP client wrapper tests  
├── test_sse_server.py       # SSE server parameter processing
├── test_integration.py      # Complete workflow tests
├── test_error_scenarios.py  # Error handling and edge cases
├── test_performance.py      # Performance and concurrency tests
├── conftest.py             # Shared fixtures and configuration
├── pytest.ini             # Test configuration and markers
└── README.md               # Comprehensive testing documentation
```

### Running Tests

#### Basic Test Execution

```bash
cd owasp_zap_mcp

# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_mcp_tools.py

# Run specific test
python -m pytest tests/test_mcp_tools.py::TestMCPZAPTools::test_mcp_zap_health_check_success
```

#### Test Categories (Markers)

```bash
# Run by category
python -m pytest -m "mcp"              # MCP functionality tests
python -m pytest -m "error_handling"   # Error scenario tests
python -m pytest -m "url_normalization" # URL normalization tests
python -m pytest -m "security"         # Security-related tests

# Special test categories (require flags)
python -m pytest -m "integration" --run-integration    # Integration tests
python -m pytest -m "performance" --run-performance    # Performance tests
python -m pytest -m "slow" --run-slow                  # Long-running tests

# Combine markers
python -m pytest -m "mcp and not slow"                 # MCP tests excluding slow ones
python -m pytest -m "error_handling or performance" --run-performance
```

#### Test Coverage

```bash
# Run with coverage
python -m pytest --cov=src/owasp_zap_mcp --cov-report=html --cov-report=term-missing

# View HTML coverage report
open htmlcov/index.html
```

### Manual Integration Testing

For debugging and manual verification when the full environment is running:

```bash
# Start the environment first
./scripts/start.sh

# Run manual integration test
python scripts/manual-integration-test.py

# This tests:
# - Health and status endpoints
# - MCP tool execution via HTTP/SSE
# - URL normalization and parameter processing  
# - Error handling
# - Real-world scenarios with httpbin.org, example.com
```

The manual integration test is useful for:

- 🔍 **Debugging MCP interface issues**
- 🧪 **Manual verification after changes**
- 🔧 **Testing parameter processing**
- 📊 **Validating environment health**

### Performance Benchmarks

The test suite includes performance validation with these targets:

- Health check: < 1 second
- Spider scan start: < 2 seconds  
- Alert retrieval: < 3 seconds
- Concurrent operations (10x): < 5 seconds
- Large dataset processing (1000 alerts): < 5 seconds

## 🎯 Making Changes

### When Adding New Tools

1. **Implement the tool function** in `src/owasp_zap_mcp/tools/zap_tools.py`
2. **Register the tool** in `src/owasp_zap_mcp/tools/tool_initializer.py`
3. **Add parameter processing** in `src/owasp_zap_mcp/sse_server.py` if needed
4. **Create comprehensive tests** in appropriate test files
5. **Update documentation** including tool descriptions

### When Modifying Existing Tools

1. **Update the function** with proper error handling
2. **Modify parameter processing** if signature changes
3. **Update both unit and integration tests**
4. **Test both direct calls and MCP interface calls**
5. **Update relevant documentation**

### When Changing Infrastructure

1. **Follow Apache Doris MCP patterns** - Never deviate without approval
2. **Test with full container rebuild** - Use `./scripts/rebuild.sh`
3. **Verify environment variable handling**
4. **Update deployment documentation**

### Files to Update Checklist

When making changes, consider updating these files:

#### For New Features

- [ ] Core implementation files (`src/owasp_zap_mcp/`)
- [ ] Test files (`tests/`)
- [ ] Documentation (`docs/`, `README.md`)
- [ ] Configuration files if needed

#### For Bug Fixes

- [ ] Fix implementation
- [ ] Add regression tests
- [ ] Update error handling tests
- [ ] Document the fix

#### For Performance Changes

- [ ] Implementation changes
- [ ] Performance tests (`tests/test_performance.py`)
- [ ] Benchmark documentation
- [ ] Load testing scenarios

## ⚡ Performance & Quality

### Performance Guidelines

- **Async Operations** - Use `async/await` for all I/O operations
- **Connection Pooling** - Reuse ZAP client connections when possible  
- **Error Recovery** - Implement graceful degradation
- **Timeouts** - Set appropriate timeouts for all operations
- **Memory Management** - Clean up resources properly

### Quality Standards

- **Test Coverage** - Maintain >90% test coverage
- **Error Handling** - All public functions must handle errors gracefully
- **Documentation** - All functions must have docstrings
- **Type Hints** - Use type hints for all function signatures
- **Logging** - Include appropriate logging for debugging

### Security Considerations

- **Input Validation** - Validate all user inputs
- **Environment Variables** - Never hardcode secrets
- **Container Security** - Follow container security best practices
- **API Security** - Implement proper authentication where needed

## 🔧 Troubleshooting

### Common Issues

#### Tests Failing

```bash
# Check test environment
python -m pytest --collect-only

# Run with verbose output
python -m pytest -v -s

# Check specific failing test
python -m pytest tests/test_mcp_tools.py::specific_test -v -s
```

#### Container Issues

```bash
# Check container status
docker compose ps

# View logs
docker compose logs owasp-zap-mcp
docker compose logs zap

# Rebuild containers
./scripts/rebuild.sh --clean
```

#### ZAP Connection Issues

```bash
# Check ZAP accessibility
curl http://localhost:8080/JSON/core/view/version/

# Check container networking
docker compose exec owasp-zap-mcp curl http://zap:8080/JSON/core/view/version/
```

#### MCP Interface Issues

```bash
# Check MCP server health
curl http://localhost:3000/health

# Check available tools
curl http://localhost:3000/status
```

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python run.py
```

### Getting Help

1. **Check Documentation** - Review relevant docs first
2. **Run Tests** - Verify your environment with the test suite
3. **Check Issues** - Look for similar issues in the project
4. **Create Detailed Bug Report** - Include logs, environment details, and reproduction steps

## 📞 Support & Contributing

### Development Resources

- **Test Documentation**: [tests/README.md](../owasp_zap_mcp/tests/README.md)
- **Architecture Guide**: [docs/architecture.md](architecture.md)
- **Docker Setup**: [docs/docker.md](docker.md)
- **Script Reference**: [docs/scripts.md](scripts.md)

### Contributing Guidelines

1. **Follow the development workflow** outlined above
2. **Maintain test coverage** - Add tests for new features
3. **Update documentation** - Keep docs in sync with code changes
4. **Follow coding standards** - Use consistent patterns and error handling
5. **Test thoroughly** - Run full test suite before submitting

---

*For AI assistants: This guide provides comprehensive information for code changes. Always reference the test suite when modifying code and update relevant documentation. The test files provide excellent examples of usage patterns and expected behaviors.*
