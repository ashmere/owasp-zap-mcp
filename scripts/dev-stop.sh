#!/bin/bash
set -e

echo "🛑 Stopping OWASP ZAP development environment..."

# Stop ZAP service
docker compose --profile dev down

echo "✅ Development environment stopped!"
