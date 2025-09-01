# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
"""
Tool registry for Haiven MCP Server.
"""

from typing import Any

from loguru import logger
from mcp.types import TextContent, Tool

from .base_tool import BaseTool


class ToolRegistry:
    """Registry for MCP tools."""

    def __init__(self, client: Any = None, server: Any = None) -> None:
        """Initialize the tool registry.

        Args:
            client: The HTTP client to use for API requests
            server: The MCP server instance for accessing cached data
        """
        self.tools: dict[str, BaseTool] = {}
        self.client = client
        self.server = server

    def register_tool(self, tool_class: type[BaseTool]) -> None:
        """Register a tool with the registry.

        Args:
            tool_class: The tool class to register
        """
        tool_instance = tool_class(self.client, self.server)
        self.tools[tool_instance.name] = tool_instance
        logger.info(f"Registered tool: {tool_instance.name}")

    def get_tool(self, name: str) -> BaseTool:
        """Get a tool by name.

        Args:
            name: The name of the tool to get

        Returns:
            The tool instance

        Raises:
            ValueError: If the tool is not found
        """
        if name not in self.tools:
            raise ValueError(f"Tool not found: {name}")
        return self.tools[name]

    def get_all_tools(self) -> list[Tool]:
        """Get all registered tools.

        Returns:
            A list of all registered tool definitions
        """
        return [tool.get_tool_definition() for tool in self.tools.values()]

    async def execute_tool(self, name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Execute a tool by name.

        Args:
            name: The name of the tool to execute
            arguments: The arguments to pass to the tool

        Returns:
            The tool's response

        Raises:
            ValueError: If the tool is not found
        """
        tool = self.get_tool(name)
        return await tool.execute(arguments)
