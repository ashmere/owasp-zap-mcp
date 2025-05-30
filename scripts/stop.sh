#!/bin/bash

# OWASP ZAP MCP Stop Script
# This script stops OWASP ZAP MCP services with automatic detection or specified type

set -e  # Exit on any error

# Default values
TYPE=""
AUTO_DETECT=true

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --type)
            TYPE="$2"
            AUTO_DETECT=false
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [--type image|build|dev|devcontainer]"
            echo ""
            echo "Options:"
            echo "  --type image        Stop security profile services"
            echo "  --type build        Stop build-dev profile services"
            echo "  --type dev          Stop dev profile services"
            echo "  --type devcontainer Stop devcontainer profile services"
            echo "  -h, --help          Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                  # Auto-detect and stop running services"
            echo "  $0 --type image     # Stop security profile"
            echo "  $0 --type build     # Stop build-dev profile"
            echo ""
            echo "Auto-detection will identify which profile is running and stop it."
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

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

print_warning() {
    echo -e "\033[1;33m$1\033[0m"
}

echo "🛑 OWASP ZAP MCP Stop Script"
echo "============================"

# Auto-detect running profile if not specified
if [[ "$AUTO_DETECT" == "true" ]]; then
    print_status "🔍 Auto-detecting running services..."
    
    RUNNING_CONTAINERS=$(docker compose ps --format "table {{.Service}}" | tail -n +2)
    
    if echo "$RUNNING_CONTAINERS" | grep -q "owasp-zap-mcp-image"; then
        TYPE="image"
        print_status "📦 Detected: Security profile (pre-built image)"
    elif echo "$RUNNING_CONTAINERS" | grep -q "owasp-zap-mcp-build"; then
        TYPE="build"
        print_status "🔨 Detected: Build-dev profile (built from source)"
    elif echo "$RUNNING_CONTAINERS" | grep -q "dev-python"; then
        TYPE="dev"
        print_status "🛠️ Detected: Dev profile (development setup)"
    elif echo "$RUNNING_CONTAINERS" | grep -q "owasp-zap-mcp-devcontainer"; then
        TYPE="devcontainer"
        print_status "📦 Detected: Devcontainer profile"
    elif echo "$RUNNING_CONTAINERS" | grep -q "zap"; then
        # Only ZAP is running, might be orphaned or minimal setup
        print_warning "⚠️ Only ZAP container detected, stopping all services"
        TYPE="all"
    else
        print_warning "⚠️ No OWASP ZAP MCP services detected"
        echo "Running containers:"
        docker compose ps
        exit 0
    fi
else
    # Validate specified type parameter
    if [[ "$TYPE" != "image" && "$TYPE" != "build" && "$TYPE" != "dev" && "$TYPE" != "devcontainer" ]]; then
        echo "Error: --type must be one of: image, build, dev, devcontainer"
        exit 1
    fi
    print_status "🎯 Stopping specified profile: $TYPE"
fi

# Stop services based on detected or specified type
case $TYPE in
    "image")
        print_status "🔒 Stopping security profile services..."
        docker compose --profile security down
        ;;
    "build")
        print_status "🔨 Stopping build-dev profile services..."
        docker compose --profile build-dev down
        ;;
    "dev")
        print_status "🛠️ Stopping dev profile services..."
        docker compose --profile dev down
        ;;
    "devcontainer")
        print_status "📦 Stopping devcontainer profile services..."
        docker compose --profile devcontainer down
        ;;
    "all")
        print_status "🧹 Stopping all services..."
        docker compose down --remove-orphans
        ;;
esac

# Additional cleanup
print_status "🧹 Cleaning up orphaned containers..."
docker compose down --remove-orphans > /dev/null 2>&1 || true

print_success "✅ Services stopped successfully!"

# Show remaining containers if any
REMAINING=$(docker compose ps --quiet)
if [[ -n "$REMAINING" ]]; then
    echo ""
    print_warning "ℹ️ Some containers are still running:"
    docker compose ps
    echo ""
    echo "To stop all containers: docker compose down --remove-orphans"
else
    echo ""
    echo "All OWASP ZAP MCP services have been stopped."
fi 
