#!/bin/bash
set -e

echo "🔧 Starting OWASP ZAP development environment..."

# Start ZAP service
docker compose --profile dev up -d zap

echo "✅ ZAP started successfully!"
echo ""
echo "🎯 Next steps:"
echo "  • ZAP API: http://localhost:8080"
echo "  • ZAP Web UI: http://localhost:8090"
echo "  • Run MCP server: cd owasp_zap_mcp && python -m owasp_zap_mcp.main --sse"
echo ""
echo "🛑 To stop: ./scripts/dev-stop.sh" 
