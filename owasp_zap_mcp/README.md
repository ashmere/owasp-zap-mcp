# OWASP ZAP MCP Server

A native Model Context Protocol (MCP) server for OWASP ZAP security scanning. This implementation follows Apache Doris MCP server patterns for robust, production-ready integration with Cursor IDE and other MCP-compatible clients.

## Features

- 🔒 **Security Scanning**: Spider scans, active scans, and vulnerability detection
- 🕷️ **Content Discovery**: Automated web application crawling and mapping
- 🎯 **Targeted Analysis**: Risk-based alert filtering and comprehensive reporting
- 📊 **Multiple Formats**: HTML and JSON report generation
- 🔄 **Session Management**: Clear and manage ZAP scanning sessions
- 🚀 **Multiple Transports**: Support for both stdio and SSE/HTTP protocols

## Architecture

This implementation follows the Apache Doris MCP server patterns with a modular architecture:

```
owasp_zap_mcp/
├── src/owasp_zap_mcp/
│   ├── __init__.py          # Package initialization
│   ├── config.py            # Environment-based configuration
│   ├── mcp_core.py          # Core MCP instance for stdio mode
│   ├── main.py              # SSE/HTTP mode entry point
│   ├── zap_client.py        # ZAP API client implementation
│   ├── server.py            # DEPRECATED - legacy compatibility
│   └── tools/               # Tool implementations
│       ├── __init__.py      # Tools package
│       ├── zap_tools.py     # Core tool implementations
│       └── tool_initializer.py  # Centralized tool registration
├── pyproject.toml           # Project configuration and entry points
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container configuration
├── .env.example            # Environment configuration template
└── README.md               # This file
```

## Installation

### Using pip (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd owasp_zap_mcp

# Install in development mode
pip install -e .

# Or install from requirements
pip install -r requirements.txt
```

### Using Docker

```bash
# Build the container
docker build -t owasp-zap-mcp .

# Run with docker-compose (includes ZAP)
docker-compose up -d
```

## Configuration

Copy the example environment file and configure as needed:

```bash
cp .env.example .env
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `info` | Logging level (debug, info, warning, error, critical) |
| `ZAP_BASE_URL` | `http://zap:8080` | ZAP API base URL |
| `ZAP_API_KEY` | _(empty)_ | ZAP API key (optional) |
| `SERVER_HOST` | `0.0.0.0` | Server host for SSE mode |
| `SERVER_PORT` | `3000` | Server port for SSE mode |
| `ALLOWED_ORIGINS` | `*` | CORS allowed origins for SSE mode |
| `MCP_ALLOW_CREDENTIALS` | `false` | CORS allow credentials for SSE mode |

## Usage

### Stdio Mode (Default)

For integration with Cursor IDE and other MCP clients:

```bash
# Using the CLI entry point
owasp-zap-mcp

# Or using Python module
python -m owasp_zap_mcp.mcp_core
```

### SSE/HTTP Mode

For web-based integration:

```bash
python -m owasp_zap_mcp.main --sse --host 0.0.0.0 --port 3000
```

### Docker Usage

```bash
# Stdio mode (default)
docker run -it owasp-zap-mcp

# SSE mode
docker run -p 3000:3000 owasp-zap-mcp python -m owasp_zap_mcp.main --sse

# With docker-compose
docker-compose up -d
```

## Available Tools

The server provides 11 security scanning tools:

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

## Integration with Cursor IDE

Add to your `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "owasp-zap-security": {
      "command": "docker",
      "args": ["exec", "-i", "owasp-zap-mcp", "owasp-zap-mcp"],
      "env": {
        "ZAP_BASE_URL": "http://zap:8080"
      }
    }
  }
}
```

## Development

### Project Structure

The project follows Apache Doris MCP server patterns:

- **Modular Architecture**: Separate concerns into focused modules
- **Tool Organization**: Centralized tool registration and implementation
- **Configuration Management**: Environment-based configuration with `.env` support
- **Multiple Transports**: Support for both stdio and SSE protocols
- **Proper Error Handling**: Comprehensive error handling with structured responses
- **Logging**: Structured logging throughout the application

### Adding New Tools

1. Implement the tool function in `src/owasp_zap_mcp/tools/zap_tools.py`
2. Register the tool in `src/owasp_zap_mcp/tools/tool_initializer.py`
3. Follow the existing patterns for error handling and response formatting

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

## Migration from Legacy Implementation

If you're upgrading from the previous implementation:

1. **Old entry points are deprecated**:
   - `run.py` → Use `owasp-zap-mcp` command
   - `server.py` → Use modular structure

2. **New CLI entry point**:
   ```bash
   # Old way
   python run.py
   
   # New way
   owasp-zap-mcp
   ```

3. **Environment configuration**:
   - Copy `.env.example` to `.env`
   - Update environment variables as needed

## Troubleshooting

### Common Issues

1. **ZAP Connection Failed**:
   - Ensure ZAP is running and accessible
   - Check `ZAP_BASE_URL` configuration
   - Verify network connectivity

2. **Tools Not Available**:
   - Check server logs for tool registration errors
   - Ensure all dependencies are installed
   - Verify MCP client configuration

3. **Permission Errors**:
   - Ensure proper file permissions
   - Check Docker user configuration
   - Verify network access

### Logging

Enable debug logging for troubleshooting:

```bash
export LOG_LEVEL=debug
owasp-zap-mcp
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the existing code patterns
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Apache Doris MCP Server for architectural patterns
- OWASP ZAP team for the security scanning engine
- Model Context Protocol specification
