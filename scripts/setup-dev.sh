#!/bin/bash
# Development setup script for OWASP ZAP MCP Tooling

set -e

echo "🔧 Setting up development environment for OWASP ZAP MCP Tooling..."

# Check if we're in the right directory
if [ ! -f ".pre-commit-config.yaml" ]; then
    echo "❌ Error: .pre-commit-config.yaml not found. Please run this script from the project root."
    exit 1
fi

# Install Python development dependencies
echo "📦 Installing Python development dependencies..."
cd owasp_zap_mcp
pip install -e ".[dev]"
cd ..

# Install pre-commit hooks
echo "🪝 Installing pre-commit hooks..."
pre-commit install

# Run pre-commit on all files to ensure everything is set up correctly
echo "🧹 Running pre-commit on all files..."
pre-commit run --all-files || {
    echo "⚠️  Some pre-commit checks failed. This is normal for the first run."
    echo "   The hooks have been installed and will run on future commits."
}

echo "✅ Development environment setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Make your changes"
echo "   2. Commit your changes (pre-commit hooks will run automatically)"
echo "   3. If hooks fail, fix the issues and commit again"
echo ""
echo "🔧 Useful commands:"
echo "   - Run pre-commit manually: pre-commit run --all-files"
echo "   - Update pre-commit hooks: pre-commit autoupdate"
echo "   - Skip pre-commit for a commit: git commit --no-verify" 
