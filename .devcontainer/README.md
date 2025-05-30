# DevContainer Setup

This directory contains VS Code DevContainer configuration for containerized development.

## Quick Start

1. **Open in VS Code**: Open this repository in VS Code
2. **Reopen in Container**: Command palette → "Dev Containers: Reopen in Container"
3. **Wait for setup**: Container builds and development environment is ready
4. **Start ZAP**: Run `./scripts/start.sh --type dev` in terminal
5. **Develop**: Edit code, run tests, debug in isolated container environment

The development environment uses **Docker Compose profiles** to provide different deployment scenarios:

- ✅ **Consistent Environment**: Same setup across all developers
- ✅ **Isolated Dependencies**: No conflicts with host system
- ✅ **Quick Setup**: One command to get running
- ✅ **VS Code Integration**: Full IDE support with extensions

## Development Workflow

Once the container is running:

```bash
# Start development environment
./scripts/start.sh --type dev

# Start local MCP server for development  
cd owasp_zap_mcp && python -m owasp_zap_mcp.main --sse

# Stop when done
./scripts/stop.sh
```

## Features

- **Full Python Environment**: Python 3.12+ with all dependencies
- **Docker Access**: Docker socket mounted for container operations
- **ZAP Integration**: Containerized ZAP for security testing
- **VS Code Extensions**: Pre-configured extensions for Python, Docker, etc.
- **Port Forwarding**: Automatic forwarding of ZAP and MCP server ports

## Container Benefits vs Host Development

✅ **Zero Code Duplication**: Single `docker-compose.yml` with profiles  
✅ **No Permission Issues**: Container handles all file permissions properly  
✅ **Simpler Setup**: Just `docker compose --profile dev up -d zap`  
✅ **Isolated Environment**: Dependencies don't conflict with host  
✅ **Consistent**: Same environment for all developers  

## Configuration Files

- `devcontainer.json`: VS Code DevContainer configuration
- `docker-compose.yml`: Service definitions with profiles

## Docker Compose Profiles

The devcontainer uses the following profiles:

### Development Profile
```bash
docker compose --profile dev up -d zap
```
- **Purpose**: Local development with containerized ZAP
- **What runs**: ZAP container only
- **MCP Server**: Run locally for development

### DevContainer Profile  
```bash
docker compose --profile devcontainer up -d
```
- **Purpose**: Full container development
- **What runs**: ZAP + Development container
- **MCP Server**: Run inside development container

### Services Profile
```bash
docker compose --profile services up -d
```
- **Purpose**: Complete production-like setup
- **What runs**: ZAP + Pre-built MCP server
- **MCP Server**: Pre-built container image

## Common Issues

### Avoid These Patterns

- ❌ Separate development docker-compose files  
- ❌ Duplicate docker-compose files
- ❌ Host permission issues with mounted volumes
- ❌ Complex multi-container development setups

### Debugging

```bash
# Check container status
docker compose ps

# View logs  
docker compose logs zap

# Test ZAP connectivity
curl http://localhost:8080/JSON/core/view/version/
```

## Quick Reference

### Development Commands
1. **Start environment**: `./scripts/start.sh --type dev`
2. **Run MCP locally**: `cd owasp_zap_mcp && python -m owasp_zap_mcp.main --sse`
3. **Test**: `curl http://localhost:3000/health`
4. **Stop**: `./scripts/stop.sh`

### Container Development  
1. **Start container**: `./scripts/start.sh --type devcontainer`
2. **Attach**: `docker exec -it owasp-zap-mcp-devcontainer bash`
3. **Run MCP**: `cd /workspace && python -m owasp_zap_mcp.main --sse`
4. **Stop**: `./scripts/stop.sh`

For more information, see the main [README.md](../README.md).

---

**Author**: Mat Davies ([@ashmere](https://github.com/ashmere/))  
**Project**: [owasp-zap-mcp](https://github.com/ashmere/owasp-zap-mcp)
