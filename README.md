# OWASP ZAP MCP Server

A comprehensive Model Context Protocol (MCP) server for integrating OWASP ZAP security scanning with AI-powered development workflows. This implementation provides seamless security testing capabilities through modern AI interfaces like Cursor IDE.

> **Author**: Mat Davies ([@ashmere](https://github.com/ashmere/))  
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

## Development

### Quick Start (Recommended)

The fastest way to get started with development:

```bash
# One-time setup
./scripts/dev-setup.sh

# Daily workflow
./scripts/dev-start.sh

# For local development, set the correct ZAP URL
export ZAP_BASE_URL=http://localhost:8080
cd owasp_zap_mcp && python -m owasp_zap_mcp.main --sse

# When done
./scripts/dev-stop.sh
```

### Development Options

#### 1. Host Development (Recommended)

- **Fastest**: No container overhead
- **Native permissions**: No file permission issues
- **Better IDE integration**: Native debugging and file watching
- **Simple setup**: Just start ZAP, develop on host

#### 2. DevContainer Development

- **Consistent environment**: Same setup for all developers
- **Isolated**: Doesn't affect host system
- **VS Code integration**: Built-in devcontainer support

```bash
# Open in VS Code and use "Reopen in Container"
# Or manually:
docker compose --profile devcontainer up -d
```

### Docker Compose Profiles

- **`dev`**: Host development (ZAP only)
- **`devcontainer`**: Container development (ZAP + dev container)
- **`services`**: Production deployment (ZAP + MCP server)

### Architecture Benefits

✅ **Zero Code Duplication**: Single docker-compose.yml with profiles  
✅ **No Permission Issues**: Host development uses native permissions  
✅ **Simpler Setup**: One command to start development environment  
✅ **Flexible**: Choose host or container development  
✅ **Better Performance**: No container overhead for development  

## Installation

### Prerequisites

- Docker and Docker Compose
- Cursor IDE or VS Code (with MCP support)
- Python 3.12+ (for local development)

### 1. Start Services

```bash
# Clone the repository
git clone https://github.com/ashmere/owasp-zap-mcp.git
cd owasp-zap-mcp

# Start all services
docker compose up -d

# Check status
docker compose ps
```

### 2. Verify Setup

```bash
# Test ZAP connectivity
curl http://localhost:8080/JSON/core/view/version/

# Test MCP server
curl http://localhost:3000/health
curl http://localhost:3000/status

# Check MCP server logs
docker compose logs owasp-zap-mcp
```

### 3. Configure Your IDE

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
docker exec -it owasp-zap-mcp python -m owasp_zap_mcp.main --sse

# Or start in stdio mode for legacy compatibility
docker exec -it owasp-zap-mcp python -m owasp_zap_mcp.main
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
│   ├── pyproject.toml          # Project configuration and dependencies
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile             # Container configuration
│   └── README.md              # Implementation documentation
├── docker-compose.yml         # Service orchestration with profiles
├── scripts/                   # Development workflow scripts
│   ├── dev-setup.sh          # One-time development setup
│   ├── dev-start.sh          # Start development environment
│   └── dev-stop.sh           # Stop development environment
├── .devcontainer/            # DevContainer configuration
│   ├── devcontainer.json     # Simplified devcontainer setup
│   └── README.md            # DevContainer documentation
├── .cursor/                  # Cursor IDE configuration
│   ├── mcp.json             # MCP server configuration
│   └── rules/               # Scanning rules and guidelines
├── .vscode/                 # VS Code configuration
│   └── mcp.json            # MCP server configuration
├── reports/                 # Organized scan reports by domain
├── docs/                    # Documentation
└── README.md               # This file
```

## Troubleshooting

### Common Issues

1. **ZAP Connection Failed**:
   - Ensure ZAP container is healthy: `docker compose ps`
   - Check ZAP logs: `docker compose logs zap`
   - For local development, verify `ZAP_BASE_URL=http://localhost:8080`
   - Verify network connectivity between containers

2. **MCP Tools Not Available**:
   - Check MCP server logs: `docker compose logs owasp-zap-mcp`
   - Verify IDE MCP configuration
   - Test SSE endpoint: `curl http://localhost:3000/sse`
   - Restart your IDE if needed

3. **SSE Connection Issues**:
   - Verify port 3000 is accessible: `curl http://localhost:3000/health`
   - Check firewall settings
   - Ensure containers are on the same network

4. **Container Issues**:
   - Rebuild containers: `docker compose build --no-cache`
   - Reset everything: `docker compose down -v && docker compose up -d`

### Fallback Strategy

If MCP tools fail, you can use direct ZAP API calls. See `.cursor/rules/owasp_zap_scanning.mdc` for complete fallback commands and troubleshooting procedures.

### Useful Commands

```bash
# View all logs
docker compose logs -f

# Restart services
docker compose restart

# Stop services
docker compose down

# Clean rebuild
docker compose down -v && docker compose build --no-cache && docker compose up -d

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
