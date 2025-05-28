#!/bin/bash

# Fix permissions script for OWASP ZAP MCP DevContainer
# This script ensures proper file permissions for the workspace

echo "🔧 Fixing file permissions in devcontainer..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Running as root, switching to codespace user..."
    TARGET_USER="codespace"
else
    TARGET_USER=$(whoami)
    echo "👤 Running as user: $TARGET_USER"
fi

# Set workspace permissions
echo "📁 Setting workspace permissions..."
sudo chown -R $TARGET_USER:$TARGET_USER /workspace
sudo chmod -R 755 /workspace

# Ensure specific directories are writable
echo "📝 Ensuring writable directories..."
mkdir -p /workspace/reports
mkdir -p /workspace/logs
sudo chown -R $TARGET_USER:$TARGET_USER /workspace/reports
sudo chown -R $TARGET_USER:$TARGET_USER /workspace/logs
chmod -R 755 /workspace/reports
chmod -R 755 /workspace/logs

# Test file creation
echo "🧪 Testing file permissions..."
TEST_FILE="/workspace/permission-test.txt"
if echo "test" > "$TEST_FILE" 2>/dev/null; then
    echo "✅ File creation successful"
    rm -f "$TEST_FILE"
else
    echo "❌ File creation failed"
    exit 1
fi

# Check Docker socket permissions
echo "🐳 Checking Docker socket permissions..."
if [ -S /var/run/docker.sock ]; then
    sudo chmod 666 /var/run/docker.sock
    echo "✅ Docker socket permissions fixed"
else
    echo "⚠️  Docker socket not found"
fi

# Test Docker access
echo "🔍 Testing Docker access..."
if docker --version >/dev/null 2>&1; then
    echo "✅ Docker access working"
else
    echo "❌ Docker access failed"
fi

echo "🎉 Permission fix complete!"
echo ""
echo "Current workspace permissions:"
ls -la /workspace | head -10 
