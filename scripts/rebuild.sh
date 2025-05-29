#!/bin/bash

# OWASP ZAP MCP Rebuild Script
# This script automates the process of rebuilding and restarting the OWASP ZAP MCP solution

set -e  # Exit on any error

echo "🔧 OWASP ZAP MCP Rebuild Script"
echo "================================"

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
# docker rmi owasp-zap-mcp_owasp-zap-mcp-build || true

# Step 4: Rebuild the image
print_status "🔨 Step 4: Rebuilding OWASP ZAP MCP image..."
docker compose build --no-cache owasp-zap-mcp-build

# Step 5: Start containers with security profile
print_status "🚀 Step 5: Starting containers with security profile..."
docker compose --profile security up -d

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
echo "Services are running:"
echo "  - ZAP: http://localhost:8080"
echo "  - MCP Server: http://localhost:3000"
echo ""
echo "To view logs:"
echo "  docker compose logs -f"
echo ""
echo "To stop services:"
echo "  docker compose down"
