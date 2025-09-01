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
from typing import Any

import httpx
from loguru import logger
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import GetPromptResult, PromptMessage, TextContent

# Import tools
from .services import PromptService
from .tools import GetPromptsToolHandler, GetPromptTextToolHandler, ToolRegistry

# Configure loguru
logger.add(sys.stderr, level="INFO", format="{time} | {level} | {name}:{function}:{line} | {message}")


class HaivenMCPServer:
    """MCP Server for Haiven Prompts API."""

    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        session_cookie: str | None = None,
        api_key: str | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.server = Server("haiven-prompts")

        # Setup authentication
        headers: dict[str, str] = {"Content-Type": "application/json"}
        cookies: dict[str, str] = {}
        disable_auth = os.getenv("HAIVEN_DISABLE_AUTH", "false").lower() == "true"

        if api_key:
            # Use API key authentication (if implemented)
            headers["Authorization"] = f"Bearer {api_key}"
            logger.info("Using API key authentication")
        elif disable_auth:
            logger.info("Authentication disabled via HAIVEN_DISABLE_AUTH=true")
        else:
            logger.warning("No authentication provided. Ensure HAIVEN_DISABLE_AUTH=true on Haiven server")

        self.client = httpx.AsyncClient(timeout=60.0, headers=headers, cookies=cookies)
        # Add base_url to the client for tools to use
        self.client.base_url = self.base_url

        # Initialize prompt service
        self.prompt_service = PromptService(self.client, self.base_url)

        # Initialize tool registry with server reference for caching
        self.tool_registry = ToolRegistry(self.client, self)
        self._register_tools()

        # Register tool handlers using the new decorator API
        self._register_handlers()

    def _register_tools(self) -> None:
        """Register all available tools."""
        self.tool_registry.register_tool(GetPromptsToolHandler)
        self.tool_registry.register_tool(GetPromptTextToolHandler)

    async def _register_prompts(self) -> None:
        """Register all prompts from the API as MCP prompts."""
        await self.prompt_service.register_prompts()

    def _register_handlers(self) -> None:
        """Register MCP tool handlers using the new decorator API."""

        @self.server.list_tools()
        async def list_tools() -> list[Any]:
            """List available tools."""
            return self.tool_registry.get_all_tools()

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
            """Handle tool calls."""
            try:
                return await self.tool_registry.execute_tool(name, arguments)
            except ValueError as e:
                logger.error(f"Tool error: {str(e)}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

        @self.server.list_prompts()
        async def list_prompts() -> list[Any]:
            """List available prompts."""
            return self.prompt_service.get_all_prompt_descriptions()

        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: dict[str, Any] | None = None) -> GetPromptResult:
            """Get prompt content by name."""
            if not self.prompt_service.is_prompt_loaded(name):
                return GetPromptResult(
                    description="Prompt not found",
                    messages=[PromptMessage(role="assistant", content=TextContent(type="text", text=f"Error: Prompt '{name}' not found"))],
                )

            try:
                # Get full prompt data from the prompt service
                prompt_data = await self.prompt_service.get_prompt_content(name)

                if prompt_data is None:
                    return GetPromptResult(
                        description="Prompt content not found",
                        messages=[
                            PromptMessage(
                                role="assistant", content=TextContent(type="text", text=f"Error: Content for prompt '{name}' not found")
                            )
                        ],
                    )

                # Extract just the content field for the MCP response
                content = prompt_data["content"]

                # Get metadata for description
                description = self.prompt_service.format_prompt_description(name)

                return GetPromptResult(
                    description=description, messages=[PromptMessage(role="assistant", content=TextContent(type="text", text=content))]
                )

            except Exception as e:
                error_msg = f"Error fetching prompt content: {str(e)}"
                logger.error(error_msg)
                return GetPromptResult(
                    description="Error fetching prompt",
                    messages=[PromptMessage(role="assistant", content=TextContent(type="text", text=f"Error: {error_msg}"))],
                )

    async def run(self) -> None:
        """Run the MCP server."""
        # CRITICAL: Load prompts BEFORE accepting MCP connections to avoid race conditions
        logger.info("Initializing prompts before starting MCP server...")
        await self._register_prompts()

        if self.prompt_service.prompts_loaded:
            logger.info(
                f"MCP server ready with {self.prompt_service.get_prompts_count()} prompts and {len(self.tool_registry.tools)} tools"
            )
        else:
            logger.warning("MCP server starting with 0 prompts due to loading failure")

        # Now safe to accept MCP connections
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream, self.server.create_initialization_options())


async def main() -> None:
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
