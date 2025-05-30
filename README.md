# OWASP ZAP MCP Server

A comprehensive Model Context Protocol (MCP) server for integrating OWASP ZAP security scanning with AI-powered development workflows. This implementation provides seamless security testing capabilities through modern AI interfaces like Cursor IDE.

> **Disclaimer**: This project is an independent implementation and is not officially associated with, endorsed by, or affiliated with the OWASP Foundation or the OWASP ZAP project. OWASP and ZAP are trademarks of the OWASP Foundation.

## Features

- 🔒 **Security Scanning**: Spider scans, active scans, and vulnerability detection
- 🕷️ **Content Discovery**: Automated web application crawling and mapping  
- 🎯 **Targeted Analysis**: Risk-based alert filtering and comprehensive reporting
- 📊 **Multiple Formats**: HTML, XML, and JSON report generation
- 🔄 **Session Management**: Clear and manage ZAP scanning sessions
- 🚀 **SSE Mode**: Server-Sent Events for modern AI integration
- 🤖 **AI Integration**: Native Cursor IDE and VS Code integration via MCP protocol
- 📁 **Organized Reports**: Automatic report organization by domain

## Architecture

This project provides a native MCP server implementation that bridges AI models with OWASP ZAP:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Cursor IDE    │◄──►│ owasp_zap_mcp   │◄──►│   OWASP ZAP     │
│                 │    │                 │    │                 │
│ - MCP Client    │    │ - SSE Server    │    │ - REST API      │
│ - AI Assistant  │    │ - ZAP Tools     │    │ - Scanner       │
│ - Code Analysis │    │ - HTTP/3000     │    │ - Proxy/8080    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/ashmere/owasp-zap-mcp.git
cd owasp-zap-mcp

# One-time setup
./scripts/dev-setup.sh
```

### 2. Start Services

```bash
# Start security scanning services (most common)
./scripts/start.sh

# Or choose specific type
./scripts/start.sh --type image      # Pre-built image (default)
./scripts/start.sh --type build      # Build from source
./scripts/start.sh --type dev        # Local development
./scripts/start.sh --type devcontainer  # Container development
```

### 3. Verify Setup

```bash
# Test ZAP connectivity
curl http://localhost:8080/JSON/core/view/version/

# Test MCP server
curl http://localhost:3000/health
curl http://localhost:3000/status
```

### 4. Stop Services

```bash
# Auto-detect and stop (recommended)
./scripts/stop.sh

# Or stop specific type
./scripts/stop.sh --type image
```

## Development Options

### For Security Engineers (Recommended)

**Quick Security Scanning**: Use pre-built images for immediate scanning capability.

```bash
# Start services
./scripts/start.sh

# Services available at:
# - ZAP API: http://localhost:8080
# - ZAP Web UI: http://localhost:8090  
# - MCP Server: http://localhost:3000
```

### For Developers

Choose your preferred development workflow:

#### 1. Local Development (Fastest)
Run MCP server locally while using containerized ZAP:

```bash
# Start ZAP only
./scripts/start.sh --type dev

# In another terminal, run MCP server locally
cd owasp_zap_mcp && python -m owasp_zap_mcp.main --sse
```

**Benefits**: Fastest iteration, native debugging, no container overhead

#### 2. Container Development
Full development environment in containers:

```bash
# Start container development
./scripts/start.sh --type devcontainer

# Attach to development container
docker exec -it owasp-zap-mcp-devcontainer bash
```

**Benefits**: Consistent environment, VS Code devcontainer support

#### 3. Build Testing
Test builds from source code:

```bash
# Build and test from source
./scripts/start.sh --type build

# Or use rebuild script for complete testing
./scripts/rebuild.sh --type build
```

**Benefits**: Test Docker builds, validate container integration

## Installation

### Prerequisites

- Docker and Docker Compose
- Cursor IDE or VS Code (with MCP support)
- Python 3.12+ (for local development)

### IDE Configuration

#### Cursor IDE

The MCP server is pre-configured in `.cursor/mcp.json`:

```json
{
  "servers": {
    "owasp-zap-security": {
      "type": "http",
      "url": "http://localhost:3000/sse"
    }
  }
}
```

#### VS Code

The MCP server is pre-configured in `.vscode/mcp.json`:

```json
{
  "servers": {
    "owasp-zap-security": {
      "type": "http",
      "url": "http://localhost:3000/sse"
    }
  }
}
```

Simply open this directory in your IDE and start using security scanning tools through AI chat.

## Available Tools

The MCP server provides 10 security scanning tools:

| Tool | Description |
|------|-------------|
| `zap_health_check` | Check if ZAP is running and accessible |
| `zap_spider_scan` | Start spider scan for content discovery |
| `zap_active_scan` | Start active security vulnerability scan |
| `zap_spider_status` | Get spider scan progress and status |
| `zap_active_scan_status` | Get active scan progress and status |
| `zap_get_alerts` | Retrieve security alerts with risk filtering |
| `zap_generate_html_report` | Generate comprehensive HTML security report |
| `zap_generate_json_report` | Generate structured JSON security report |
| `zap_clear_session` | Clear ZAP session data |
| `zap_scan_summary` | Get comprehensive scan summary for a URL |

## Usage Examples

### With AI Assistant

Simply ask your AI assistant:

- "Please check if ZAP is running and ready for security testing"
- "Run a spider scan on <https://example.com>"
- "Show me all high-risk security alerts"
- "Generate a security report for the last scan"
- "Perform a complete security scan of <https://mysite.com>"

### Report Organization

All scan reports are automatically organized by domain:

```
reports/
├── example.com/
│   ├── example_com_security_report.html
│   ├── example_com_security_report.xml
│   ├── example_com_security_report.json
│   ├── example_com_alerts_summary.json
│   ├── example_com_scan_summary.md
│   └── example_com_scan_status.md
└── httpbin.org/
    ├── httpbin_io_security_report.html
    ├── httpbin_io_security_report.xml
    ├── httpbin_io_security_report.json
    ├── httpbin_io_alerts_summary.json
    ├── httpbin_io_scan_summary.md
    └── httpbin_io_scan_status.md
```

### Direct CLI Usage

```bash
# Start the MCP server in SSE mode (default)
# For security profile (image type):
docker exec -it owasp-zap-mcp-image python -m owasp_zap_mcp.main --sse

# For build profile (build type):
docker exec -it owasp-zap-mcp-build python -m owasp_zap_mcp.main --sse

# Or start in stdio mode for legacy compatibility
docker exec -it owasp-zap-mcp-image python -m owasp_zap_mcp.main
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and modify as needed:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level |
| `ZAP_BASE_URL` | `http://localhost:8080` | ZAP API base URL (use `http://localhost:8080` for local development) |
| `ZAP_API_KEY` | _(empty)_ | ZAP API key (disabled by default) |
| `SERVER_HOST` | `0.0.0.0` | Server host for SSE mode |
| `SERVER_PORT` | `3000` | Server port for SSE mode |

**Important**: For local development (host-based), set `ZAP_BASE_URL=http://localhost:8080`. The default `http://zap:8080` is for Docker container communication only.

### ZAP Configuration

ZAP is configured to run without API key authentication for internal container communication:

```bash
zap.sh -daemon -host 0.0.0.0 -port 8080 \
       -config api.addrs.addr.name=.* \
       -config api.addrs.addr.regex=true \
       -config api.disablekey=true
```

## Project Structure

```
owasp-zap-mcp/
├── owasp_zap_mcp/              # Main MCP server implementation
│   ├── src/owasp_zap_mcp/      # Source code
│   │   ├── config.py           # Environment-based configuration
│   │   ├── main.py             # Entry point with SSE/stdio modes
│   │   ├── sse_server.py       # SSE server implementation
│   │   ├── zap_client.py       # ZAP API client implementation
│   │   └── tools/              # Tool implementations
│   ├── tests/                  # Test suite
│   ├── pyproject.toml          # Project configuration and dependencies
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile             # Container configuration
│   ├── run.py                  # Development runner script
│   └── README.md              # Implementation documentation
├── docker-compose.yml         # Service orchestration with profiles
├── scripts/                   # Development workflow scripts
│   ├── dev-setup.sh          # One-time development setup
│   ├── start.sh              # Start services with options
│   ├── stop.sh               # Stop services with auto-detection
│   ├── rebuild.sh            # Complete rebuild and testing
│   └── test.sh               # Run comprehensive tests
├── .devcontainer/            # DevContainer configuration
│   ├── devcontainer.json     # Simplified devcontainer setup
│   └── README.md            # DevContainer documentation
├── .cursor/                  # Cursor IDE configuration
│   ├── mcp.json             # MCP server configuration
│   └── rules/               # Scanning rules and guidelines
├── .vscode/                 # VS Code configuration
│   └── mcp.json            # MCP server configuration
├── .github/                 # GitHub Actions workflows
│   ├── workflows/           # CI/CD pipeline definitions
│   └── .actrc              # Local testing configuration
├── docs/                    # Documentation
│   ├── scripts.md          # Detailed scripts documentation
│   ├── docker.md           # Docker configuration and profiles
│   ├── development-tips.ai.md  # AI assistant development guide
│   ├── architecture.md     # System architecture documentation
│   └── threatmodel.md      # Security threat model
├── reports/                 # Organized scan reports by domain
├── research/                # Research and reference materials
├── debugging/               # Debugging artifacts and logs
├── .env.example            # Environment configuration template
├── .env                    # Local environment configuration
├── LICENSE                 # MIT license
└── README.md               # This file
```

## Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `dev-setup.sh` | One-time environment setup | `./scripts/dev-setup.sh` |
| `start.sh` | Start services with options | `./scripts/start.sh [--type TYPE]` |
| `stop.sh` | Stop services with auto-detection | `./scripts/stop.sh [--type TYPE]` |
| `rebuild.sh` | Complete rebuild and test | `./scripts/rebuild.sh [--type TYPE]` |
| `test.sh` | Run comprehensive tests | `./scripts/test.sh` |

For detailed script documentation, see [docs/scripts.md](docs/scripts.md).

## Troubleshooting

### Common Issues

1. **ZAP Connection Failed**:
   - Ensure ZAP container is healthy: `docker compose ps`
   - Check ZAP logs: `docker compose logs zap`
   - For local development, verify `ZAP_BASE_URL=http://localhost:8080`
   - Verify network connectivity between containers

2. **MCP Tools Not Available**:
   - Check MCP server logs: `docker compose logs owasp-zap-mcp-image`
   - Verify IDE MCP configuration
   - Test SSE endpoint: `curl http://localhost:3000/sse`
   - Restart your IDE if needed

3. **SSE Connection Issues**:
   - Verify port 3000 is accessible: `curl http://localhost:3000/health`
   - Check firewall settings
   - Ensure containers are on the same network

4. **Container Issues**:
   - Rebuild containers: `./scripts/rebuild.sh`
   - Reset everything: `./scripts/stop.sh && ./scripts/start.sh`

### Useful Commands

```bash
# View all logs
docker compose logs -f

# Restart services
./scripts/stop.sh && ./scripts/start.sh

# Clean rebuild
./scripts/rebuild.sh

# Test endpoints
curl http://localhost:8080/JSON/core/view/version/  # ZAP API
curl http://localhost:3000/health                   # MCP Health
curl http://localhost:3000/status                   # MCP Status
```

## Security Considerations

- ZAP runs with API key disabled for internal container communication
- Containers communicate over isolated Docker network
- No sensitive data is exposed to host system by default
- ZAP web interface is exposed on localhost:8080 for debugging (can be disabled)
- MCP server runs on localhost:3000 for AI integration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the existing code patterns
4. Add tests for new functionality
5. Update documentation as needed
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OWASP ZAP team for the excellent security testing tool
- Model Context Protocol specification for standardized AI tool integration
- Cursor team for MCP integration and AI-powered development workflows
- Apache Doris MCP Server for architectural inspiration

---

**Author**: Mat Davies ([@ashmere](https://github.com/ashmere/))  
**Compatibility**: Cursor IDE, VS Code, MCP 1.0+
