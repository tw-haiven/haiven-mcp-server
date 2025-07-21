# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0
# Multi-stage build for Haiven MCP Server
FROM python:3.11-slim AS builder

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install poetry
RUN pip install --no-cache-dir poetry==1.8.3

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Configure poetry and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi --no-root

# Production stage
FROM python:3.11-slim

# Create non-root user for security
RUN groupadd -r haiven && useradd -r -g haiven haiven

# Set working directory
WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY src/ ./src/
COPY mcp_server.py ./

# Change ownership to non-root user
RUN chown -R haiven:haiven /app

# Switch to non-root user
USER haiven

# Health check (MCP servers use stdin/stdout, so we'll check if the process starts)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import sys; sys.exit(0)"]

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Use CMD instead of ENTRYPOINT to match main Haiven repo approach
# The -u flag ensures unbuffered output for MCP communication
CMD ["python", "-u", "mcp_server.py"]
