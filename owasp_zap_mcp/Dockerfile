# OWASP ZAP MCP Server Dockerfile
# Builds a containerized version of the ZAP MCP server

FROM python:3.12-slim

LABEL maintainer="ZAP-MCP-Tooling Team"
LABEL description="OWASP ZAP MCP Server - Native MCP server for security scanning"
LABEL version="0.1.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire package structure
COPY src/ src/
COPY pyproject.toml .
COPY .env.example .env

# Install the package in development mode
RUN pip install -e .

# Create non-root user for security
RUN useradd -m -u 1000 zapuser && chown -R zapuser:zapuser /app
USER zapuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command uses the new CLI entry point
CMD ["owasp-zap-mcp"]

# Alternative commands:
# For stdio mode: docker run owasp-zap-mcp owasp-zap-mcp
# For SSE mode: docker run -p 3000:3000 owasp-zap-mcp python -m owasp_zap_mcp.main --sse 
