# OWASP ZAP MCP Development Environment

This directory contains the development container configuration for the OWASP ZAP MCP project. The new design eliminates code duplication and complex permission management while providing flexible development options.

## Architecture

The development environment uses **Docker Compose profiles** to provide different deployment scenarios:

- **`dev` profile**: Host-based development (recommended)
- **`devcontainer` profile**: Container-based development (optional)
- **`services` profile**: Production/testing deployment

## Quick Start

### Option 1: Host Development (Recommended)

This is the fastest and most flexible approach:

```bash
# One-time setup
./scripts/dev-setup.sh

# Daily workflow
./scripts/dev-start.sh
cd owasp_zap_mcp && python -m owasp_zap_mcp.main --sse

# When done
./scripts/dev-stop.sh
```

### Option 2: DevContainer Development

If you prefer container-based development:

1. Open the project in VS Code
2. Use "Reopen in Container" command
3. The devcontainer will automatically start ZAP
4. Run the MCP server: `cd owasp_zap_mcp && python -m owasp_zap_mcp.main --sse`

## Benefits of New Design

✅ **Zero Code Duplication**: Single `docker-compose.yml` with profiles  
✅ **No Permission Issues**: Host development uses native permissions  
✅ **Simpler Setup**: Just `docker compose --profile dev up -d zap`  
✅ **Faster Development**: No container overhead for code changes  
✅ **Better IDE Integration**: Native file watching, debugging, etc.  
✅ **Flexible**: Can use devcontainer if preferred  

## Available Services

- **ZAP API**: http://localhost:8080
- **ZAP Web UI**: http://localhost:8090  
- **MCP Server**: http://localhost:3000 (when running locally)

## Docker Compose Profiles

### Development Profile (`dev`)
```bash
docker compose --profile dev up -d zap
```
Starts only ZAP for host-based development.

### DevContainer Profile (`devcontainer`)
```bash
docker compose --profile devcontainer up -d
```
Starts ZAP + development container.

### Services Profile (`services`)
```bash
docker compose --profile services up -d
```
Starts ZAP + MCP server for production/testing.

## Migration from Old Setup

The old setup had these issues:
- ❌ Duplicate docker-compose files
- ❌ Complex permission management scripts
- ❌ Container-in-container complexity

The new setup eliminates all these problems while maintaining the same functionality.

## Troubleshooting

### ZAP not starting
```bash
docker compose logs zap
```

### Permission issues
With host development, you use native file permissions - no special setup needed!

### Port conflicts
Make sure ports 8080, 8090, and 3000 are available.

## Development Workflow

1. **Start environment**: `./scripts/dev-start.sh`
2. **Develop**: Edit code with your favorite editor
3. **Test**: `cd owasp_zap_mcp && python -m owasp_zap_mcp.main --sse`
4. **Stop**: `./scripts/dev-stop.sh`

No complex permission fixes or container rebuilds needed!

---

**Author**: Mat Davies ([@ashmere](https://github.com/ashmere/))  
**Project**: [owasp-zap-mcp](https://github.com/ashmere/owasp-zap-mcp)
