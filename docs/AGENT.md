## Haiven MCP Server

This is a standalone MCP (Model Context Protocol) server that provides AI tools with access to Haiven's prompts API.

## Project Structure
- **Main server**: `src/mcp_server.py` - The core MCP server implementation
- **Root launcher**: `mcp_server.py` - Thin wrapper for tools that do not support 'cwd' or '-m'
- **Tests**: `test_*.py` files - Unit and integration tests
- **Installation**: `install.sh` and `generate_config.py` - User-friendly installation scripts
- **Documentation**: Multiple `.md` files covering setup, authentication, and troubleshooting
- **Examples**: `examples/` directory with configuration files for different AI tools
- **Development**: `dev_setup.sh` for developer setup

## Development Guidelines
- We use Python 3.11+ with Poetry for dependency management
- The server communicates with Haiven via HTTP API calls only
- Authentication supports session cookies, API keys, and development mode (auth disabled)
- We prioritize ease of installation and setup for end users
- The server follows MCP protocol standards for AI tool integration

## Testing
- Run tests with: `poetry run pytest`
- Run the server with: `poetry run python -m src.mcp_server` or `poetry run python mcp_server.py`
> **Note:** The root-level 'mcp_server.py' allows running the server from the project root, which is helpful for tools that do not support 'cwd' or '-m'.
- Integration tests verify connectivity with Haiven API
- Tests cover different authentication methods and AI tool configurations

## When making changes
- Test with multiple AI tools (Claude Desktop, VS Code, Cursor)
- Verify installation scripts work on different platforms
- Update documentation if adding new features or changing setup process
- Ensure backward compatibility with existing Haiven API versions
