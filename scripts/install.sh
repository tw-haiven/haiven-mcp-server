#!/bin/bash

echo ""
echo "========================================"
echo "  Haiven MCP Server Quick Install"
echo "  for AI Tools Integration"
echo "  (https://github.com/thoughtworks/haiven-mcp-server)"
echo "========================================"
echo ""

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "🐳 Docker found!"
    echo ""
    echo "🎯 RECOMMENDED: Use Docker setup (easier and more reliable)"
    echo "   Docker setup doesn't require Python or Poetry installation."
    echo "   Just configure your AI tool with the Docker command."
    echo ""
    echo "📋 Docker Configuration Example:"
    echo "   command: docker"
    echo "   args: [run, -i, --rm, -e, HAIVEN_API_KEY=your-key, -e, HAIVEN_API_URL=your-url, ghcr.io/tw-haiven/haiven-mcp-server:latest]"
    echo ""
    echo "💡 See docs/USER_SETUP_GUIDE.md for detailed Docker setup instructions."
    echo ""
    echo "🖥️  Mac users: Consider using Colima as a lighter alternative to Docker Desktop"
    echo "   Install with: brew install colima && colima start"
    echo ""
    read -p "Press Enter to continue with Python setup anyway, or Ctrl+C to exit and use Docker..."
    echo ""
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python is not installed"
    echo "Please install Python from https://python.org"
    echo "or use your system package manager:"
    echo "  macOS: brew install python"
    echo "  Ubuntu: sudo apt install python3"
    echo ""
    echo "💡 Alternatively, consider using Docker setup (see docs/USER_SETUP_GUIDE.md)"
    exit 1
fi

# Use python3 if available, otherwise python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

echo "✅ Python found"
echo ""

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed"
    echo "Please install Poetry first: brew install poetry"
    echo ""
    echo "💡 Alternatively, consider using Docker setup (see docs/USER_SETUP_GUIDE.md)"
    exit 1
fi

echo "✅ Poetry found"
echo ""

# Configure Poetry to use in-project virtual environments
echo "🔧 Configuring Poetry for in-project virtual environments..."
poetry config virtualenvs.in-project true

# Install dependencies and create virtual environment
echo "📦 Installing dependencies..."
poetry install

echo "✅ Dependencies installed"
echo ""

# Run the configuration generator using the virtual environment's Python
echo "Starting configuration generator..."
poetry run python scripts/generate_config.py

echo ""
echo "Configuration generated!"
echo "Please copy the generated config to your AI tool's configuration file."
echo "Then restart your AI tool (Claude Desktop, VS Code, Cursor, etc.) to see the changes."

# Wait for user input on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    read -p "Press any key to continue..."
fi
