# Scripts Documentation

This document provides detailed information about all the scripts available in the OWASP ZAP MCP project and their usage.

## 📁 Script Overview

All scripts are located in the `scripts/` directory and are designed to simplify common development and deployment tasks.

| Script | Purpose | Target Users |
|--------|---------|--------------|
| `start.sh` | Start OWASP ZAP MCP services | All users |
| `stop.sh` | Stop OWASP ZAP MCP services | All users |
| `rebuild.sh` | Rebuild and restart services | Developers |
| `dev-setup.sh` | One-time development setup | Developers |
| `test.sh` | Run comprehensive tests | Developers |

## 🚀 start.sh

**Purpose**: Start OWASP ZAP MCP services with different configuration options.

### Usage
```bash
./scripts/start.sh [--type TYPE] [--help]
```

### Options
- `--type image` (default): Use pre-built image with security profile
- `--type build`: Use built-from-source with build-dev profile  
- `--type dev`: Use development profile (ZAP + dev container)
- `--type devcontainer`: Use devcontainer profile for container development
- `--help`: Show help message

### Examples
```bash
# Quick start for security scanning (most common)
./scripts/start.sh

# Use pre-built image explicitly
./scripts/start.sh --type image

# Use built from source
./scripts/start.sh --type build

# Development setup (run MCP server locally)
./scripts/start.sh --type dev

# Full container development
./scripts/start.sh --type devcontainer
```

### What Each Type Does

#### `--type image` (Default)
- **Profile**: `security`
- **Container**: `owasp-zap-mcp-image`
- **Use Case**: Ready-to-use security scanning
- **Services**: ZAP + Pre-built MCP server
- **Access**: http://localhost:3000

#### `--type build`
- **Profile**: `build-dev`
- **Container**: `owasp-zap-mcp-build`
- **Use Case**: Testing builds from source
- **Services**: ZAP + MCP server built from source
- **Access**: http://localhost:3000

#### `--type dev`
- **Profile**: `dev`
- **Container**: `dev-python`
- **Use Case**: Local development
- **Services**: ZAP + Python dev container
- **Note**: Run MCP server locally: `cd owasp_zap_mcp && python -m owasp_zap_mcp.main --sse`

#### `--type devcontainer`
- **Profile**: `devcontainer`
- **Container**: `owasp-zap-mcp-devcontainer`
- **Use Case**: VS Code container development
- **Services**: ZAP + Full development container
- **Access**: `docker exec -it owasp-zap-mcp-devcontainer bash`

### Service URLs
All types provide these services:
- **ZAP API**: http://localhost:8080
- **ZAP Web UI**: http://localhost:8090
- **MCP Server**: http://localhost:3000 (except dev mode)

## 🛑 stop.sh

**Purpose**: Stop OWASP ZAP MCP services with automatic detection or specified type.

### Usage
```bash
./scripts/stop.sh [--type TYPE] [--help]
```

### Options
- `--type image`: Stop security profile services
- `--type build`: Stop build-dev profile services
- `--type dev`: Stop dev profile services
- `--type devcontainer`: Stop devcontainer profile services
- `--help`: Show help message

### Examples
```bash
# Auto-detect and stop (most common)
./scripts/stop.sh

# Stop specific profile
./scripts/stop.sh --type image
./scripts/stop.sh --type build
```

### Auto-Detection Logic

The script automatically detects which profile is running by checking for these containers:

1. **owasp-zap-mcp-image** → Security profile (`--type image`)
2. **owasp-zap-mcp-build** → Build-dev profile (`--type build`)
3. **dev-python** → Dev profile (`--type dev`)
4. **owasp-zap-mcp-devcontainer** → Devcontainer profile (`--type devcontainer`)
5. **zap only** → Stops all services with cleanup

### Features
- **Smart Detection**: Identifies running profile automatically
- **Clean Shutdown**: Removes orphaned containers
- **Status Reporting**: Shows remaining containers if any
- **Error Handling**: Graceful handling of missing containers

## 🔨 rebuild.sh

**Purpose**: Complete rebuild and restart of OWASP ZAP MCP solution with testing.

### Usage
```bash
./scripts/rebuild.sh [--type TYPE] [--help]
```

### Options
- `--type image` (default): Use pre-built image with security profile
- `--type build`: Build from source with build-dev profile
- `--help`: Show help message

### Examples
```bash
# Rebuild with pre-built image (fastest)
./scripts/rebuild.sh

# Rebuild from source code
./scripts/rebuild.sh --type build
```

### Process Steps
1. **Shutdown**: Stop existing containers
2. **Cleanup**: Remove orphaned containers
3. **Build**: Build images if using `--type build`
4. **Start**: Start services with appropriate profile
5. **Health Check**: Wait for services to be ready
6. **Test**: Run comprehensive test suite

### When to Use
- After code changes (use `--type build`)
- After Docker configuration changes
- When containers are in inconsistent state
- For CI/CD pipelines
- For testing complete setup

## ⚙️ dev-setup.sh

**Purpose**: One-time development environment setup and configuration.

### Usage
```bash
./scripts/dev-setup.sh
```

### What It Does
1. **Prerequisites Check**: Verifies Docker and Python are available
2. **Python Setup**: Installs package in development mode (`pip install -e .`)
3. **Dependencies**: Installs development dependencies if available
4. **Environment**: Creates `.env` from `.env.example`
5. **Permissions**: Makes all scripts executable
6. **Guidance**: Provides next steps and usage instructions

### When to Use
- **First Time Setup**: After cloning the repository
- **New Development Machine**: Setting up development environment
- **After Clean Install**: Resetting development environment
- **CI/CD Setup**: Preparing automation environment

### Prerequisites
- Docker installed and running
- Python 3.12+ available
- Git repository cloned

## 🧪 test.sh

**Purpose**: Run comprehensive test suite across all components.

### Usage
```bash
./scripts/test.sh
```

### Test Coverage
1. **Container Health**: Verify all containers are healthy
2. **ZAP Connectivity**: Test ZAP API endpoints
3. **MCP Server**: Test MCP server health and tools
4. **Tool Registration**: Verify all 10 tools are available
5. **Functional Tests**: Basic functionality tests
6. **Integration Tests**: End-to-end workflow tests

### Test Output
- **✅ Green**: Tests passing
- **❌ Red**: Tests failing
- **⏳ Yellow**: Tests in progress
- **Summary**: Total tests run and results

### When to Use
- **After Changes**: Verify functionality after code changes
- **Before Deployment**: Ensure system is ready for production
- **Troubleshooting**: Diagnose system issues
- **CI/CD Validation**: Automated testing in pipelines

## 🔄 Workflow Patterns

### Quick Start Workflow
```bash
# One-time setup
./scripts/dev-setup.sh

# Start services
./scripts/start.sh

# Stop when done
./scripts/stop.sh
```

### Development Workflow
```bash
# Setup development environment
./scripts/dev-setup.sh

# Start development services
./scripts/start.sh --type dev

# In another terminal, run MCP server locally
cd owasp_zap_mcp && python -m owasp_zap_mcp.main --sse

# Test changes
./scripts/test.sh

# Stop when done
./scripts/stop.sh
```

### Build Testing Workflow
```bash
# Test complete build process
./scripts/rebuild.sh --type build

# Verify everything works
./scripts/test.sh

# Clean up
./scripts/stop.sh
```

### Container Development Workflow
```bash
# Start container development
./scripts/start.sh --type devcontainer

# Attach to container
docker exec -it owasp-zap-mcp-devcontainer bash

# Inside container: develop and test
cd /workspace
python -m owasp_zap_mcp.main --sse

# Stop when done
./scripts/stop.sh
```

## 🚨 Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Check what's using the ports
lsof -i :8080 -i :3000 -i :8090

# Stop conflicting services or change ports in docker-compose.yml
```

#### Permission Denied
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Or use dev-setup.sh which fixes permissions
./scripts/dev-setup.sh
```

#### Docker Issues
```bash
# Check Docker daemon
docker info

# Check container status
docker compose ps

# View logs
docker compose logs
```

#### Container Detection Issues
```bash
# Manual cleanup
docker compose down --remove-orphans

# Force restart
./scripts/rebuild.sh
```

### Debug Commands

#### Check Running Services
```bash
# List all containers
docker compose ps

# Check specific profile
docker compose --profile security ps
docker compose --profile build-dev ps
```

#### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f zap
docker compose logs -f owasp-zap-mcp-image
```

#### Manual Service Control
```bash
# Start specific profile
docker compose --profile security up -d

# Stop specific profile
docker compose --profile security down
```

## 💡 Best Practices

### Script Usage
1. **Use start.sh for daily work**: Simplest way to start services
2. **Use stop.sh without parameters**: Auto-detection is reliable
3. **Use rebuild.sh for testing**: Ensures clean state
4. **Run dev-setup.sh once**: After cloning or major changes

### Development Tips
1. **Type Selection**: Choose the right type for your workflow
2. **Log Monitoring**: Use `docker compose logs -f` to monitor services
3. **Health Checks**: Wait for services to be healthy before testing
4. **Clean Rebuilds**: Use rebuild.sh when containers misbehave

### Production Deployment
1. **Use image type**: Pre-built images are more reliable
2. **Run tests**: Always run test.sh before deployment
3. **Monitor logs**: Set up log monitoring for production
4. **Environment variables**: Configure .env appropriately

---

For more information, see:
- [Docker Configuration](docker.md)
- [Development Tips](development-tips.ai.md)
- [Main README](../README.md) 
