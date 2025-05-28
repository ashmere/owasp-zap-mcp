# DevContainer Setup for OWASP ZAP MCP

This devcontainer provides a complete development environment for the OWASP ZAP MCP server with proper file permissions and Docker integration.

## Features

- ✅ **Proper File Permissions**: Files can be saved and edited without permission issues
- ✅ **Docker Integration**: Full Docker access from within the container
- ✅ **Port Forwarding**: Automatic forwarding of ZAP (8080) and MCP (3000) ports
- ✅ **Python Environment**: Pre-configured Python with formatting and linting
- ✅ **Service Integration**: Automatic startup of ZAP and MCP services

## Quick Start

1. **Open in DevContainer**
   ```bash
   # In Cursor/VS Code, use Command Palette:
   # "Dev Containers: Reopen in Container"
   ```

2. **Verify Setup**
   ```bash
   # Check file permissions
   ls -la /workspace
   
   # Check Docker access
   docker --version
   docker ps
   
   # Check services
   docker compose ps
   ```

3. **Start Services** (if not auto-started)
   ```bash
   docker compose up -d
   ```

## File Structure

```
.devcontainer/
├── devcontainer.json       # Main devcontainer configuration
├── docker-compose.yml      # Service definitions
└── README.md              # This file
```

## Configuration Details

### Workspace Mounting
- **Host**: `${localWorkspaceFolder}` 
- **Container**: `/workspace`
- **Type**: Bind mount with cached consistency
- **Permissions**: Owned by `codespace` user

### User Configuration
- **User**: `codespace` (non-root)
- **UID**: Automatically updated to match host
- **Permissions**: Full read/write access to workspace

### Port Forwarding
- **3000**: MCP Server (auto-notify)
- **8080**: ZAP API (auto-notify)  
- **8090**: ZAP Web UI (ignored)

## Troubleshooting

### File Permission Issues

If you still can't save files:

```bash
# Check current permissions
ls -la /workspace

# Fix permissions manually
sudo chown -R codespace:codespace /workspace
sudo chmod -R 755 /workspace

# Verify fix
touch /workspace/test.txt
echo "test" > /workspace/test.txt
rm /workspace/test.txt
```

### Docker Access Issues

```bash
# Check Docker daemon
docker --version
docker info

# Check Docker socket permissions
ls -la /var/run/docker.sock

# Test Docker functionality
docker run hello-world
```

### Service Startup Issues

```bash
# Check service status
docker compose ps

# View service logs
docker compose logs zap
docker compose logs owasp-zap-mcp

# Restart services
docker compose restart

# Full rebuild
docker compose down
docker compose build --no-cache
docker compose up -d
```

### MCP Integration Issues

```bash
# Test MCP server
curl http://localhost:3000/health
curl http://localhost:3000/status

# Test ZAP API
curl http://localhost:8080/JSON/core/view/version/

# Check MCP configuration
cat /workspace/.cursor/mcp.json
cat /workspace/.vscode/mcp.json
```

## Development Workflow

1. **Edit Files**: All files in `/workspace` are editable with proper permissions
2. **Run Commands**: Use integrated terminal for Docker and Python commands
3. **Test Changes**: Services auto-reload on code changes
4. **Debug**: Use VS Code debugging with Python extension

## Environment Variables

The devcontainer sets up these environment variables:

```bash
LOCAL_WORKSPACE_FOLDER=/workspace
PYTHONPATH=/workspace
```

## Extensions

Pre-installed VS Code extensions:
- Python support with IntelliSense
- Black formatter for code formatting
- Flake8 for linting
- JSON support for configuration files

## Performance Tips

- **File Watching**: Reports directory excluded from file watching
- **Cached Mounts**: Workspace uses cached consistency for better performance
- **Network Mode**: Host networking for optimal container communication

## Security Notes

- Container runs as non-root `codespace` user
- Docker socket mounted for Docker-in-Docker functionality
- No sensitive data exposed outside container
- Services isolated on Docker network

---

If you continue to experience issues, please check the main project README.md for additional troubleshooting steps. 
