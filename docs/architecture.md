# OWASP ZAP MCP Server Architecture

## Overview

The OWASP ZAP MCP Server is a Model Context Protocol (MCP) implementation that bridges AI-powered development environments with OWASP ZAP security scanning capabilities. This document outlines the system architecture, component interactions, and implementation details.

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        AI Development Environment                │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │   Cursor IDE    │    │     VS Code     │                    │
│  │                 │    │                 │                    │
│  │ - MCP Client    │    │ - MCP Client    │                    │
│  │ - AI Assistant  │    │ - AI Assistant  │                    │
│  │ - Code Analysis │    │ - Code Analysis │                    │
│  └─────────────────┘    └─────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   │ HTTP/SSE
                                   │ Port 3000
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MCP Server Container                       │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                  owasp-zap-mcp                              │ │
│  │                                                             │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │ │
│  │  │ SSE Server  │  │ MCP Handler │  │    Tool Registry    │ │ │
│  │  │             │  │             │  │                     │ │ │
│  │  │ - FastAPI   │  │ - Protocol  │  │ - 10 ZAP Tools      │ │ │
│  │  │ - WebSocket │  │ - Session   │  │ - Tool Validation   │ │ │
│  │  │ - Events    │  │ - Messages  │  │ - Error Handling    │ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘ │ │
│  │                                                             │ │
│  │  ┌─────────────────────────────────────────────────────────┐ │ │
│  │  │                ZAP Client                               │ │ │
│  │  │                                                         │ │ │
│  │  │ - HTTP Client    - API Wrapper    - Response Parser    │ │ │
│  │  │ - Error Handler  - Retry Logic    - Data Validation    │ │ │
│  │  └─────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   │ HTTP API
                                   │ Port 8080
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                       ZAP Container                             │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    OWASP ZAP                                │ │
│  │                                                             │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │ │
│  │  │   Spider    │  │ Active Scan │  │    Proxy Engine     │ │ │
│  │  │             │  │             │  │                     │ │ │
│  │  │ - Discovery │  │ - Injection │  │ - Request/Response  │ │ │
│  │  │ - Crawling  │  │ - Analysis  │  │ - Session Handling  │ │ │
│  │  │ - Mapping   │  │ - Analysis  │  │ - Session Handling  │ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘ │ │
│  │                                                             │ │
│  │  ┌─────────────────────────────────────────────────────────┐ │ │
│  │  │                  REST API                               │ │ │
│  │  │                                                         │ │ │
│  │  │ - Core API       - Spider API      - Active Scan API   │ │ │
│  │  │ - Report API     - Alert API       - Session API       │ │ │
│  │  └─────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Network Architecture

```
┌─────────────────┐
│   Host System   │
│                 │
│ Cursor/VS Code  │
│ localhost:3000  │◄──────────┐
│ localhost:8080  │           │
└─────────────────┘           │
                              │
┌─────────────────────────────────────────────┐
│            Docker Network                   │
│            (zap-network)                    │
│                                             │
│  ┌─────────────────┐    ┌─────────────────┐ │
│  │ owasp-zap-mcp   │    │      zap        │ │
│  │                 │    │                 │ │
│  │ Port: 3000      │◄──►│ Port: 8080      │ │
│  │ Host: 0.0.0.0   │    │ Host: 0.0.0.0   │ │
│  │                 │    │                 │ │
│  │ Internal:       │    │ Internal:       │ │
│  │ http://zap:8080 │    │ ZAP API Server  │ │
│  └─────────────────┘    └─────────────────┘ │
└─────────────────────────────────────────────┘
```

## Development Architecture

### Docker Compose Profiles

The project uses Docker Compose profiles for different deployment scenarios:

```yaml
# Development Profile (dev)
docker compose --profile dev up -d zap

# DevContainer Profile (devcontainer)
docker compose --profile devcontainer up -d

# Production Profile (services)
docker compose --profile services up -d
```

### Development Workflow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Host Development (Recommended)                │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │ Native IDE      │    │ Development     │                    │
│  │                 │    │ Scripts         │                    │
│  │ - Cursor/VS Code│    │                 │                    │
│  │ - Native Debug  │    │ - dev-setup.sh  │                    │
│  │ - File Watching │    │ - dev-start.sh  │                    │
│  │ - No Containers │    │ - dev-stop.sh   │                    │
│  └─────────────────┘    └─────────────────┘                    │
│                                   │                             │
│                                   ▼                             │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              Docker (ZAP Only)                              │ │
│  │                                                             │ │
│  │  ┌─────────────────┐                                       │ │
│  │  │      ZAP        │  Profile: dev                         │ │
│  │  │                 │  Command: docker compose --profile    │ │
│  │  │ Port: 8080      │           dev up -d zap               │ │
│  │  │ Network: host   │                                       │ │
│  │  └─────────────────┘                                       │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   Container Development (Optional)               │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    DevContainer                             │ │
│  │                                                             │ │
│  │  ┌─────────────────┐    ┌─────────────────┐                │ │
│  │  │ Dev Container   │    │      ZAP        │                │ │
│  │  │                 │    │                 │                │ │
│  │  │ - Python 3.12   │    │ - Scanner       │                │ │
│  │  │ - VS Code       │    │ - API Server    │                │ │
│  │  │ - Workspace     │    │ - Port: 8080    │                │ │
│  │  │ - Docker Socket │    │                 │                │ │
│  │  └─────────────────┘    └─────────────────┘                │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. MCP Server (owasp-zap-mcp)

#### Core Components

#### SSE Server (`sse_server.py`)

- FastAPI-based HTTP server
- Server-Sent Events (SSE) implementation
- Session management and client tracking
- WebSocket-like bidirectional communication over HTTP
- Health and status endpoints

#### MCP Protocol Handler

- Implements MCP 1.0 specification
- Handles `initialize`, `tools/list`, `tools/call` methods
- Session lifecycle management
- Error handling and response formatting

#### Tool Registry

- Dynamic tool registration system
- 10 security scanning tools
- Input validation and sanitization
- Consistent error handling patterns

#### ZAP Client (`zap_client.py`)

- HTTP client for ZAP REST API
- Connection pooling and retry logic
- Response parsing and validation
- Error mapping and handling

#### Tool Implementation

```python
# Tool Structure
class ZAPTool:
    name: str
    description: str
    input_schema: dict
    handler: callable

# Tool Categories
- Health & Status: zap_health_check
- Scanning: zap_spider_scan, zap_active_scan
- Monitoring: zap_spider_status, zap_active_scan_status
- Analysis: zap_get_alerts, zap_scan_summary
- Reporting: zap_generate_html_report, zap_generate_json_report
- Management: zap_clear_session
```

### 2. OWASP ZAP Container

#### Configuration

```bash
# ZAP Daemon Configuration
zap.sh -daemon -host 0.0.0.0 -port 8080 \
       -config api.addrs.addr.name=.* \
       -config api.addrs.addr.regex=true \
       -config api.disablekey=true
```

#### Key Features

- **API Access**: No authentication required (internal network)
- **Spider Engine**: Content discovery and site mapping
- **Active Scanner**: Vulnerability detection and testing
- **Proxy Engine**: Traffic interception and analysis
- **Report Generation**: Multiple output formats (HTML, XML, JSON)

### 3. Container Orchestration

#### Docker Compose Services with Profiles

##### ZAP Service (All Profiles)

```yaml
zap:
  image: zaproxy/zap-stable:latest
  profiles: ["services", "dev", "devcontainer"]
  ports: ["8080:8080", "8090:8090"]
  healthcheck: curl -f http://localhost:8080/JSON/core/view/version/
  networks: [zap-network]
```

##### MCP Server Service (Production Only)

```yaml
owasp-zap-mcp:
  build: ./owasp_zap_mcp
  profiles: ["services"]  # Only for production/testing
  ports: ["3000:3000"]
  depends_on: [zap]
  command: ["python", "-m", "owasp_zap_mcp.main", "--sse"]
  networks: [zap-network]
```

##### DevContainer Service (Development Only)

```yaml
devcontainer:
  image: mcr.microsoft.com/devcontainers/python:3.12
  profiles: ["devcontainer"]
  volumes: [".:/workspace:cached", "/var/run/docker.sock:/var/run/docker.sock"]
  working_dir: /workspace
  network_mode: host
```

## Communication Protocols

### 1. MCP Protocol (AI ↔ MCP Server)

#### Connection Flow

```
1. AI Client → HTTP GET /sse
2. Server → SSE Connection Established
3. AI Client → POST /mcp/messages (initialize)
4. Server → SSE Response (capabilities)
5. AI Client → POST /mcp/messages (tools/list)
6. Server → SSE Response (tool definitions)
7. AI Client → POST /mcp/messages (tools/call)
8. Server → SSE Response (tool results)
```

#### Message Format

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "zap_spider_scan",
    "arguments": {
      "url": "https://example.com",
      "max_depth": 5
    }
  }
}
```

### 2. ZAP API Protocol (MCP Server ↔ ZAP)

#### API Endpoints

```
Health:     GET  /JSON/core/view/version/
Spider:     GET  /JSON/spider/action/scan/
Status:     GET  /JSON/spider/view/status/
Active:     GET  /JSON/ascan/action/scan/
Alerts:     GET  /JSON/core/view/alerts/
Reports:    GET  /OTHER/core/other/htmlreport/
```

#### Response Handling

```python
# Standard ZAP Response
{
  "Result": "OK",
  "scan": "0"  # Scan ID
}

# Error Response
{
  "code": "bad_parameter",
  "message": "Invalid URL format"
}
```

## Data Flow

### 1. Security Scan Workflow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ AI Request  │───►│ MCP Server  │───►│ ZAP Scanner │
│             │    │             │    │             │
│ "Scan URL"  │    │ Parse/Route │    │ Execute     │
└─────────────┘    └─────────────┘    └─────────────┘
                           │                   │
                           ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ AI Response │◄───│ Format      │◄───│ Results     │
│             │    │ Response    │    │             │
│ "Scan ID: 0"│    │ JSON/MCP    │    │ Raw Data    │
└─────────────┘    └─────────────┘    └─────────────┘
```

### 2. Report Generation Workflow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ AI Request  │───►│ Extract     │───►│ Create      │
│             │    │ Domain      │    │ Directory   │
│ "Generate   │    │ from URL    │    │ Structure   │
│  Report"    │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
                           │                   │
                           ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Organized   │◄───│ Generate    │◄───│ Fetch from  │
│ Reports     │    │ All Formats │    │ ZAP API     │
│             │    │             │    │             │
│ reports/    │    │ HTML/XML/   │    │ Multiple    │
│ domain/     │    │ JSON/MD     │    │ Endpoints   │
└─────────────┘    └─────────────┘    └─────────────┘
```

## Security Architecture

### 1. Network Security

#### Container Isolation

- Dedicated Docker network (`zap-network`)
- No direct external access to ZAP
- MCP server acts as security gateway

#### Port Exposure

- ZAP: 8080 (localhost only, for debugging)
- MCP: 3000 (localhost only, for AI integration)
- No external network exposure

### 2. API Security

#### ZAP Configuration

- API key disabled (internal network only)
- Address filtering enabled
- Daemon mode (no GUI)

#### MCP Server

- Input validation on all tool parameters
- Error sanitization (no sensitive data leakage)
- Session isolation

### 3. Data Security

#### Report Organization

- Domain-based directory structure
- No cross-domain data leakage
- Consistent file naming conventions

#### Session Management

- UUID-based session tracking
- Automatic cleanup on disconnect
- No persistent session storage

## Deployment Architecture

### 1. Development Environment

```
Developer Machine
├── Docker Desktop
├── Cursor IDE / VS Code
├── Git Repository
├── Development Scripts
│   ├── dev-setup.sh
│   ├── dev-start.sh
│   └── dev-stop.sh
└── Local Testing
```

### 2. Production Considerations

#### Scaling

- Horizontal scaling via multiple MCP server instances
- Load balancing for high-throughput scanning
- ZAP cluster configuration for enterprise use

#### Monitoring

- Health check endpoints
- Structured logging
- Metrics collection points

#### Security Hardening

- API key authentication (production)
- Network policies
- Resource limits

## Configuration Management

### 1. Environment Variables

```bash
# Core Configuration
LOG_LEVEL=INFO
ZAP_BASE_URL=http://zap:8080
ZAP_API_KEY=

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=3000

# Feature Flags
ENABLE_DETAILED_LOGGING=false
MAX_SCAN_DURATION=3600
```

### 2. MCP Client Configuration

**Cursor IDE (`.cursor/mcp.json`)**

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

**VS Code (`.vscode/mcp.json`)**

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

## Error Handling Strategy

### 1. Error Categories

#### Connection Errors

- ZAP unavailable
- Network timeouts
- Container failures

#### Protocol Errors

- Invalid MCP messages
- Malformed requests
- Version mismatches

#### Application Errors

- Invalid scan parameters
- ZAP API errors
- Resource limitations

### 2. Error Response Format

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32603,
    "message": "Internal error",
    "data": {
      "type": "ZAPConnectionError",
      "details": "Unable to connect to ZAP API"
    }
  }
}
```

### 3. Fallback Strategies

#### MCP Failure

- Direct ZAP API access
- Command-line tools
- Manual scanning procedures

#### ZAP Failure

- Health check validation
- Container restart procedures
- Alternative scanning tools

## Performance Considerations

### 1. Optimization Points

#### Connection Pooling

- HTTP client connection reuse
- ZAP API session management
- Resource cleanup

#### Caching

- Tool definitions
- ZAP capabilities
- Session metadata

#### Async Processing

- Non-blocking I/O
- Concurrent scan handling
- Background report generation

### 2. Resource Limits

#### Memory Usage

- ZAP: 2GB default heap
- MCP Server: 512MB typical
- Report storage: Configurable

#### CPU Usage

- Scan intensity configuration
- Concurrent scan limits
- Background processing

## Monitoring and Observability

### 1. Health Checks

#### ZAP Health

```bash
curl http://localhost:8080/JSON/core/view/version/
```

#### MCP Server Health

```bash
curl http://localhost:3000/health
curl http://localhost:3000/status
```

### 2. Logging Strategy

#### Structured Logging

```python
logger.info("Tool executed", extra={
    "tool": "zap_spider_scan",
    "session_id": session_id,
    "url": target_url,
    "duration": execution_time
})
```

#### Log Levels

- ERROR: System failures, critical issues
- WARN: Recoverable errors, degraded performance
- INFO: Normal operations, tool executions
- DEBUG: Detailed tracing, development

### 3. Metrics Collection

#### Key Metrics

- Tool execution count
- Success/failure rates
- Response times
- Active sessions
- Scan completion rates

## Future Architecture Considerations

### 1. Scalability Enhancements

#### Multi-ZAP Support

- ZAP cluster management
- Load balancing
- Scan distribution

#### Cloud Integration

- Container orchestration (Kubernetes)
- Managed services
- Auto-scaling

### 2. Feature Extensions

#### Additional Scanners

- Nuclei integration
- Custom tool support
- Third-party APIs

#### Enhanced Reporting

- Real-time dashboards
- Trend analysis
- Compliance reporting

### 3. Security Enhancements

#### Authentication

- API key management
- OAuth integration
- Role-based access

#### Audit Logging

- Scan history
- User activity
- Compliance tracking

---

**Author**: Mat Davies ([@ashmere](https://github.com/ashmere/))  
**Project**: [owasp-zap-mcp](https://github.com/ashmere/owasp-zap-mcp)

This architecture provides a robust, scalable foundation for AI-powered security testing while maintaining security best practices and operational simplicity.
