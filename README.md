# OWASP ZAP MCP Tooling

A comprehensive toolkit for integrating OWASP ZAP security scanning with AI-powered development workflows through the Model Context Protocol (MCP). This implementation follows Apache Doris MCP server patterns for robust, production-ready integration.

> **Disclaimer**: This project is an independent implementation and is not officially associated with, endorsed by, or affiliated with the OWASP Foundation or the OWASP ZAP project. OWASP and ZAP are trademarks of the OWASP Foundation.

## Features

- 🔒 **Security Scanning**: Spider scans, active scans, and vulnerability detection
- 🕷️ **Content Discovery**: Automated web application crawling and mapping  
- 🎯 **Targeted Analysis**: Risk-based alert filtering and comprehensive reporting
- 📊 **Multiple Formats**: HTML and JSON report generation
- 🔄 **Session Management**: Clear and manage ZAP scanning sessions
- 🚀 **Multiple Transports**: Support for both stdio and SSE/HTTP protocols
- 🤖 **AI Integration**: Native Cursor IDE integration via MCP protocol

## Architecture

This project provides a native MCP server implementation that bridges AI models with OWASP ZAP:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Cursor IDE    │◄──►│ owasp_zap_mcp   │◄──►│   OWASP ZAP     │
│                 │    │                 │    │                 │
│ - MCP Client    │    │ - Native MCP    │    │ - REST API      │
│ - AI Assistant  │    │ - ZAP Tools     │    │ - Scanner       │
│ - Code Analysis │    │ - Stdio I/O     │    │ - Proxy         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Project Structure

```
zap-mcp-tooling/
├── owasp_zap_mcp/              # Main MCP server implementation
│   ├── src/owasp_zap_mcp/      # Source code
│   │   ├── config.py           # Environment-based configuration
│   │   ├── mcp_core.py         # Core MCP instance for stdio mode
│   │   ├── main.py             # SSE/HTTP mode entry point
│   │   ├── zap_client.py       # ZAP API client implementation
│   │   └── tools/              # Tool implementations
│   ├── pyproject.toml          # Project configuration and entry points
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile             # Container configuration
│   └── README.md              # Detailed implementation docs
├── docker-compose.yml         # Service orchestration
├── .cursor/mcp.json          # Cursor IDE MCP configuration
└── README.md                 # This file
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Cursor IDE (or other MCP-compatible client)
- Python 3.12+ (for local development)

### 1. Start Services

```bash
# Clone the repository
git clone <repository-url>
cd zap-mcp-tooling

# Start all services
docker compose up -d

# Check status
docker compose ps
```

### 2. Verify Setup

```bash
# Test ZAP connectivity
curl http://localhost:8080/JSON/core/view/version/

# Check MCP server logs
docker compose logs owasp-zap-mcp
```

### 3. Configure Cursor IDE

The MCP server is pre-configured in `.cursor/mcp.json`. Simply open this directory in Cursor IDE and start using security scanning tools through AI chat.

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

### With Cursor IDE

Simply ask your AI assistant:

- "Please check if ZAP is running and ready for security testing"
- "Run a spider scan on <https://example.com>"
- "Show me all high-risk security alerts"
- "Generate a security report for the last scan"

### Direct CLI Usage

```bash
# Start the MCP server directly
docker exec -it owasp-zap-mcp owasp-zap-mcp

# Or run in SSE mode for web integration
docker exec -it owasp-zap-mcp python -m owasp_zap_mcp.main --sse
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level |
| `ZAP_BASE_URL` | `http://zap:8080` | ZAP API base URL |
| `ZAP_API_KEY` | _(empty)_ | ZAP API key (disabled by default) |
| `SERVER_HOST` | `0.0.0.0` | Server host for SSE mode |
| `SERVER_PORT` | `3000` | Server port for SSE mode |

### ZAP Configuration

ZAP is configured to run without API key authentication for internal container communication:

```bash
zap.sh -daemon -host 0.0.0.0 -port 8080 \
       -config api.addrs.addr.name=.* \
       -config api.addrs.addr.regex=true \
       -config api.disablekey=true
```

## Development

### Local Development

```bash
cd owasp_zap_mcp

# Install in development mode
pip install -e .

# Run the server
owasp-zap-mcp
```

### Adding New Tools

1. Implement the tool function in `src/owasp_zap_mcp/tools/zap_tools.py`
2. Register the tool in `src/owasp_zap_mcp/tools/tool_initializer.py`
3. Follow existing patterns for error handling and response formatting

### Testing

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Code formatting
black src/
flake8 src/
```

## Troubleshooting

### Common Issues

1. **ZAP Connection Failed**:
   - Ensure ZAP container is healthy: `docker compose ps`
   - Check ZAP logs: `docker compose logs zap`
   - Verify network connectivity between containers

2. **MCP Tools Not Available**:
   - Check MCP server logs: `docker compose logs owasp-zap-mcp`
   - Verify Cursor MCP configuration in `.cursor/mcp.json`
   - Restart Cursor IDE if needed

3. **Container Issues**:
   - Rebuild containers: `docker compose build --no-cache`
   - Reset everything: `docker compose down -v && docker compose up -d`

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
```

## Security Considerations

- ZAP runs with API key disabled for internal container communication
- Containers communicate over isolated Docker network
- No sensitive data is exposed to host system by default
- ZAP web interface is exposed on localhost:8080 for debugging (can be disabled)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the existing code patterns (based on Apache Doris MCP server)
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Apache Doris MCP Server for architectural patterns and best practices
- OWASP ZAP team for the excellent security testing tool
- Model Context Protocol specification for standardized AI tool integration
- Cursor team for MCP integration and AI-powered development workflows

---

**Version**: 0.1.0  
**Status**: Active Development  
**Compatibility**: Cursor IDE, MCP 1.0+
