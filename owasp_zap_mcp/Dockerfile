# OWASP ZAP MCP Server Dockerfile
# Builds a containerized version of the ZAP MCP server

FROM python:3.12-slim

LABEL maintainer="Mat Davies <mat.davies@ashmere.dev>"
LABEL description="OWASP ZAP MCP Server for AI-powered security testing"
LABEL version="0.2.0"
LABEL repository="https://github.com/ashmere/owasp-zap-mcp"

# Set working directory
WORKDIR /app

# Set default environment variables for configuration
ENV LOG_LEVEL=INFO
ENV ZAP_BASE_URL=http://zap:8080
ENV SERVER_HOST=0.0.0.0
ENV SERVER_PORT=3000

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy source code
COPY . .

# Verify the package structure
RUN echo "Verifying package structure..." && \
    ls -la && \
    test -f pyproject.toml && echo "✅ pyproject.toml found" || (echo "❌ pyproject.toml missing" && exit 1) && \
    test -d src/owasp_zap_mcp && echo "✅ Source directory found" || (echo "❌ Source directory missing" && exit 1)

# Install Python dependencies and package
RUN echo "Installing Python dependencies and package..." && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir uv && \
    uv pip install --system . && \
    pip list && \
    pip show owasp-zap-mcp && \
    echo "Dependencies and package installed successfully"

# Create non-root user
RUN useradd --create-home --shell /bin/bash zapuser

# Test the installation
RUN echo "Testing package installation..." && \
    python -c "import owasp_zap_mcp; print('✅ Package imports successfully')" && \
    python -c "from owasp_zap_mcp.main import run_main_sync; print('✅ Main module imports successfully')" && \
    echo "Installation test passed"

# Switch to non-root user
USER zapuser

# Expose port for SSE mode
EXPOSE 3000

# Health check that actually tests the package
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import owasp_zap_mcp; import sys; sys.exit(0)"

# Default command (stdio mode)
CMD ["owasp-zap-mcp"]

# Alternative commands:
# For stdio mode: docker run owasp-zap-mcp owasp-zap-mcp
# For SSE mode: docker run -p 3000:3000 owasp-zap-mcp python -m owasp_zap_mcp.main --sse
