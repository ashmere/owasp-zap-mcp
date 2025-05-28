#!/bin/bash
set -e

echo "🚀 Setting up OWASP ZAP MCP development environment..."

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required"; exit 1; }

# Start ZAP service only (for development)
echo "🔧 Starting ZAP service..."
docker compose --profile dev up -d zap

# Wait for ZAP to be healthy
echo "⏳ Waiting for ZAP to be ready..."
timeout 120 bash -c 'until docker compose ps zap | grep -q "healthy"; do sleep 2; done' || {
    echo "❌ ZAP failed to start within 120 seconds"
    docker compose logs zap
    exit 1
}

# Install Python dependencies from the owasp_zap_mcp directory
echo "📦 Installing Python dependencies..."
cd owasp_zap_mcp
pip install -e .

# Check if dev requirements exist and install them
if [ -f "requirements-dev.txt" ]; then
    echo "📦 Installing development dependencies..."
    pip install -r requirements-dev.txt
fi

# Return to project root
cd ..

echo "✅ Development environment ready!"
echo ""
echo "🎯 Next steps:"
echo "  • ZAP API: http://localhost:8080"
echo "  • ZAP Web UI: http://localhost:8090"
echo "  • Run MCP server: cd owasp_zap_mcp && python -m owasp_zap_mcp.main --sse"
echo "  • Run tests: cd owasp_zap_mcp && pytest"
echo ""
echo "🛑 To stop: docker compose --profile dev down" 
