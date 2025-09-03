#!/bin/bash

# Test script for Haiven MCP Server Docker image
# Usage: ./scripts/test_docker_image.sh [api_key] [api_url]

set -e

# Default values
API_KEY=${1:-"test-key"}
API_URL=${2:-"http://host.docker.internal:8080"}

echo "🧪 Testing Haiven MCP Server Docker Image"
echo "API Key: $API_KEY"
echo "API URL: $API_URL"
echo ""

# Test basic container startup
echo "📦 Testing container startup..."
docker run --rm --pull=always \
  -e HAIVEN_API_KEY="$API_KEY" \
  -e HAIVEN_API_URL="$API_URL" \
  --add-host=host.docker.internal:host-gateway \
  ghcr.io/tw-haiven/haiven-mcp-server:latest \
  python -c "import sys; print('✅ Container startup test passed')"

echo ""
echo "🔧 Testing MCP server functionality..."
# Test MCP server with a simple JSON-RPC request
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0.0"}}}' | \
docker run -i --rm --pull=always \
  -e HAIVEN_API_KEY="$API_KEY" \
  -e HAIVEN_API_URL="$API_URL" \
  --add-host=host.docker.internal:host-gateway \
  ghcr.io/tw-haiven/haiven-mcp-server:latest

echo ""
echo "✅ Docker image test completed successfully!"
echo ""
echo "To use with your AI tool, configure it with:"
echo "ghcr.io/tw-haiven/haiven-mcp-server:latest"
