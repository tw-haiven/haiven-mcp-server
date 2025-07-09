# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
#!/usr/bin/env python3
"""
Haiven MCP Server

This server provides access to Haiven's prompts API through the Model Context Protocol (MCP).
It allows AI assistants to discover and execute prompts from your Haiven instance.
"""

import asyncio
import os
import sys
from typing import Any, Dict, List, Optional

import httpx
from loguru import logger
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent

# Import tools - use relative imports since we're in the src directory
from .tools import (
    GetPromptsToolHandler,
    GetPromptTextToolHandler,
    ToolRegistry,
)

# Configure loguru
logger.add(sys.stderr, level="INFO", format="{time} | {level} | {name}:{function}:{line} | {message}")


class HaivenMCPServer:
    """MCP Server for Haiven Prompts API."""

    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        session_cookie: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.server = Server("haiven-prompts")

        # Setup authentication
        headers = {"Content-Type": "application/json"}
        cookies = {}
        disable_auth = os.getenv("HAIVEN_DISABLE_AUTH", "false").lower() == "true"

        if session_cookie:
            # Use session cookie for authentication (from browser session)
            cookies["session"] = session_cookie
            logger.info("Using session cookie authentication")
        elif api_key:
            # Use API key authentication (if implemented)
            headers["Authorization"] = f"Bearer {api_key}"
            logger.info("Using API key authentication")
        elif disable_auth:
            logger.info("Authentication disabled via HAIVEN_DISABLE_AUTH=true")
        else:
            logger.warning("No authentication provided. Ensure HAIVEN_DISABLE_AUTH=true on Haiven server")

        self.client = httpx.AsyncClient(timeout=60.0, headers=headers, cookies=cookies)
        # Add base_url to client for tools to use
        self.client.base_url = self.base_url

        # Initialize tool registry
        self.tool_registry = ToolRegistry(self.client)
        self._register_tools()

        # Register tool handlers using new decorator API
        self._register_handlers()

    def _register_tools(self):
        """Register all available tools."""
        self.tool_registry.register_tool(GetPromptsToolHandler)
        self.tool_registry.register_tool(GetPromptTextToolHandler)

    def _register_handlers(self):
        """Register MCP tool handlers using the new decorator API."""

        @self.server.list_tools()
        async def list_tools() -> List[Any]:
            """List available tools."""
            return self.tool_registry.get_all_tools()

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls."""
            try:
                return await self.tool_registry.execute_tool(name, arguments)
            except ValueError as e:
                logger.error(f"Tool error: {str(e)}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream, self.server.create_initialization_options())


async def main():
    """Main entry point."""

    # Parse command line arguments and environment variables
    base_url = os.getenv("HAIVEN_API_URL", "http://localhost:8080")
    session_cookie = os.getenv("HAIVEN_SESSION_COOKIE")
    api_key = os.getenv("HAIVEN_API_KEY")

    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    if len(sys.argv) > 2:
        session_cookie = sys.argv[2]

    logger.info("Starting Haiven MCP Server")
    logger.info(f"API URL: {base_url}")

    # Authentication info (don't log sensitive data)
    if session_cookie:
        logger.info("Authentication: Session cookie provided")
    elif api_key:
        logger.info("Authentication: API key provided")
    else:
        logger.info("Authentication: None (requires HAIVEN_DISABLE_AUTH=true)")

    server = HaivenMCPServer(base_url, session_cookie, api_key)
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
