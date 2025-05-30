#!/bin/bash
set -e

echo "🚀 Setting up OWASP ZAP MCP development environment..."

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required"; exit 1; }

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker daemon is not running. Please start Docker and try again."
    exit 1
fi

echo "📦 Installing Python dependencies..."
cd owasp_zap_mcp

# Install main package in development mode
pip install -e .

# Check if dev requirements exist and install them
if [ -f "requirements-dev.txt" ]; then
    echo "📦 Installing development dependencies..."
    pip install -r requirements-dev.txt
fi

# Return to project root
cd ..

# Set up environment configuration
echo "⚙️  Setting up environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "📝 Created .env from .env.example"
        echo "💡 Note: .env is configured for local development (ZAP_BASE_URL=http://localhost:8080)"
    else
        echo "⚠️  No .env.example found, you may need to set ZAP_BASE_URL=http://localhost:8080 manually"
    fi
else
    echo "📝 .env file already exists"
fi

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x scripts/*.sh

echo "✅ Development environment setup complete!"
echo ""
echo "🎯 Next steps:"
echo ""
echo "1. Start services:"
echo "   • For security scanning: ./scripts/start.sh"
echo "   • For development: ./scripts/start.sh --type dev"
echo "   • For container dev: ./scripts/start.sh --type devcontainer"
echo ""
echo "2. If using development mode (--type dev):"
echo "   • Run MCP server locally: cd owasp_zap_mcp && python -m owasp_zap_mcp.main --sse"
echo ""
echo "3. Access points:"
echo "   • ZAP API: http://localhost:8080"
echo "   • ZAP Web UI: http://localhost:8090"
echo "   • MCP Server: http://localhost:3000"
echo ""
echo "4. Test your setup:"
echo "   • Health check: curl http://localhost:3000/health"
echo "   • Run tests: cd owasp_zap_mcp && pytest"
echo ""
echo "🛑 To stop services: ./scripts/stop.sh"
echo ""
echo "📚 For more information:"
echo "   • Scripts documentation: docs/scripts.md"
echo "   • Docker setup: docs/docker.md"
echo "   • Development guide: docs/development-tips.ai.md"
