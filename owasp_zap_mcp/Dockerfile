# OWASP ZAP MCP Server Dockerfile
# Builds a containerized version of the ZAP MCP server

FROM python:3.12-slim

LABEL maintainer="Mat Davies <mat.davies@ashmere.dev>"
LABEL description="OWASP ZAP MCP Server for AI-powered security testing"
LABEL version="0.2.0"
LABEL repository="https://github.com/ashmere/owasp-zap-mcp"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies and the package in one layer
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Install the package in development mode and create non-root user
RUN pip install -e . && \
    useradd --create-home --shell /bin/bash zapuser
USER zapuser

# Expose port for SSE mode
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command (stdio mode)
CMD ["owasp-zap-mcp"]

# Alternative commands:
# For stdio mode: docker run owasp-zap-mcp owasp-zap-mcp
# For SSE mode: docker run -p 3000:3000 owasp-zap-mcp python -m owasp_zap_mcp.main --sse
