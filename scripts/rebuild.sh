#!/bin/bash

# OWASP ZAP MCP Rebuild Script
# This script automates the process of rebuilding and restarting the OWASP ZAP MCP solution

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
            echo "Usage: $0 [--type image|build]"
            echo ""
            echo "Options:"
            echo "  --type image    Use pre-built image from registry (default)"
            echo "  --type build    Build from source code"
            echo "  -h, --help      Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Use pre-built image (default)"
            echo "  $0 --type image       # Use pre-built image"
            echo "  $0 --type build       # Build from source"
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
if [[ "$TYPE" != "image" && "$TYPE" != "build" ]]; then
    echo "Error: --type must be either 'image' or 'build'"
    exit 1
fi

echo "🔧 OWASP ZAP MCP Rebuild Script"
echo "================================"
echo "Mode: $TYPE"

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

# Step 1: Shutdown existing containers
print_status "🛑 Step 1: Shutting down existing containers..."
docker compose down || true

# Step 2: Clean up any orphaned containers
print_status "🧹 Step 2: Cleaning up orphaned containers..."
docker compose down --remove-orphans || true

# Step 3: Remove any existing images (optional - uncomment if needed)
# print_status "🗑️ Step 3: Removing existing images..."
# if [[ "$TYPE" == "build" ]]; then
#     docker rmi owasp-zap-mcp_owasp-zap-mcp-build || true
# fi

# Step 4: Build image if using build mode
if [[ "$TYPE" == "build" ]]; then
    print_status "🔨 Step 4: Building OWASP ZAP MCP image from source..."
    docker compose build --no-cache owasp-zap-mcp-build
else
    print_status "⏭️ Step 4: Skipping build (using pre-built image)..."
fi

# Step 5: Start containers with appropriate profile
if [[ "$TYPE" == "build" ]]; then
    print_status "🚀 Step 5: Starting containers with build-dev profile..."
    docker compose --profile build-dev up -d
else
    print_status "🚀 Step 5: Starting containers with security profile..."
    docker compose --profile security up -d
fi

# Step 6: Wait for services to be ready
print_status "⏳ Step 6: Waiting for services to be ready..."
echo "Waiting for ZAP to start (this may take 60-90 seconds)..."

# Wait for ZAP health check
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

# Wait a bit more for MCP server
echo "Waiting for MCP server to start..."
sleep 10

# Step 7: Run tests
print_status "🧪 Step 7: Running tests..."
if [ -f "./scripts/test.sh" ]; then
    ./scripts/test.sh
else
    print_error "❌ Test script not found at ./scripts/test.sh"
fi

print_success "🎉 Rebuild complete!"
echo ""
echo "Services are running in $TYPE mode:"
if [[ "$TYPE" == "build" ]]; then
    echo "  - ZAP: http://localhost:8080"
    echo "  - MCP Server (built from source): http://localhost:3000"
    echo "  - Container: owasp-zap-mcp-build"
else
    echo "  - ZAP: http://localhost:8080"
    echo "  - MCP Server (pre-built image): http://localhost:3000"
    echo "  - Container: owasp-zap-mcp-image"
fi
echo ""
echo "To view logs:"
if [[ "$TYPE" == "build" ]]; then
    echo "  docker compose logs -f owasp-zap-mcp-build"
else
    echo "  docker compose logs -f owasp-zap-mcp-image"
fi
echo "  docker compose logs -f zap"
echo ""
echo "To stop services:"
echo "  docker compose down"
