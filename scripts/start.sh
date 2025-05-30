#!/bin/bash

# OWASP ZAP MCP Start Script
# This script starts the OWASP ZAP MCP solution with different configuration options

set -e  # Exit on any error

# Default values
TYPE="image"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --type)
            TYPE="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [--type image|build|dev|devcontainer]"
            echo ""
            echo "Options:"
            echo "  --type image        Use pre-built image with security profile (default)"
            echo "  --type build        Use built-from-source with build-dev profile"
            echo "  --type dev          Use development profile (ZAP + dev container)"
            echo "  --type devcontainer Use devcontainer profile (full container dev)"
            echo "  -h, --help          Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                         # Use pre-built image (default)"
            echo "  $0 --type image            # Use pre-built image"
            echo "  $0 --type build            # Use built from source"
            echo "  $0 --type dev              # Use development setup"
            echo "  $0 --type devcontainer     # Use container development"
            echo ""
            echo "Services will be available at:"
            echo "  - ZAP API: http://localhost:8080"
            echo "  - ZAP Web UI: http://localhost:8090"
            echo "  - MCP Server: http://localhost:3000"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Validate type parameter
if [[ "$TYPE" != "image" && "$TYPE" != "build" && "$TYPE" != "dev" && "$TYPE" != "devcontainer" ]]; then
    echo "Error: --type must be one of: image, build, dev, devcontainer"
    exit 1
fi

# Function to print colored output
print_status() {
    echo -e "\033[1;34m$1\033[0m"
}

print_success() {
    echo -e "\033[1;32m$1\033[0m"
}

print_error() {
    echo -e "\033[1;31m$1\033[0m"
}

echo "🚀 OWASP ZAP MCP Start Script"
echo "============================="
echo "Starting in $TYPE mode..."

# Start services based on type
case $TYPE in
    "image")
        print_status "🔒 Starting security profile (pre-built image)..."
        docker compose --profile security up -d
        CONTAINER_NAME="owasp-zap-mcp-image"
        ;;
    "build")
        print_status "🔨 Starting build-dev profile (built from source)..."
        docker compose --profile build-dev up -d
        CONTAINER_NAME="owasp-zap-mcp-build"
        ;;
    "dev")
        print_status "🛠️ Starting dev profile (development setup)..."
        docker compose --profile dev up -d
        CONTAINER_NAME="dev-python"
        echo ""
        print_status "📝 Development mode: Run MCP server locally with:"
        echo "  cd owasp_zap_mcp && pip install -e . && python -m owasp_zap_mcp.main --sse"
        ;;
    "devcontainer")
        print_status "📦 Starting devcontainer profile (container development)..."
        docker compose --profile devcontainer up -d
        CONTAINER_NAME="owasp-zap-mcp-devcontainer"
        echo ""
        print_status "📝 Container development: Attach to container with:"
        echo "  docker exec -it owasp-zap-mcp-devcontainer bash"
        ;;
esac

# Wait for services to be ready
print_status "⏳ Waiting for ZAP to be ready..."
timeout=120
counter=0
while [ $counter -lt $timeout ]; do
    if docker compose ps | grep -q "healthy"; then
        print_success "✅ ZAP is healthy!"
        break
    fi
    echo -n "."
    sleep 2
    counter=$((counter + 2))
done

if [ $counter -ge $timeout ]; then
    print_error "❌ Timeout waiting for ZAP to become healthy"
    echo "Check logs with: docker compose logs zap"
    exit 1
fi

# Additional wait for MCP server (except dev mode)
if [[ "$TYPE" != "dev" && "$TYPE" != "devcontainer" ]]; then
    echo "Waiting for MCP server to start..."
    sleep 5
fi

print_success "🎉 Services started successfully!"
echo ""
echo "Services running in $TYPE mode:"
echo "  - ZAP API: http://localhost:8080"
echo "  - ZAP Web UI: http://localhost:8090"

if [[ "$TYPE" == "image" || "$TYPE" == "build" ]]; then
    echo "  - MCP Server: http://localhost:3000"
    echo ""
    echo "Health checks:"
    echo "  curl http://localhost:3000/health"
    echo "  curl http://localhost:3000/status"
elif [[ "$TYPE" == "dev" ]]; then
    echo "  - MCP Server: Run locally (see instructions above)"
elif [[ "$TYPE" == "devcontainer" ]]; then
    echo "  - Development Container: owasp-zap-mcp-devcontainer"
fi

echo ""
echo "To view logs:"
echo "  docker compose logs -f zap"
if [[ "$TYPE" == "image" || "$TYPE" == "build" ]]; then
    echo "  docker compose logs -f $CONTAINER_NAME"
fi
echo ""
echo "To stop services:"
echo "  ./scripts/stop.sh"
