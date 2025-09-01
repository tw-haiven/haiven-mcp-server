# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
"""
Base tool class for Haiven MCP Server.
"""

import abc
from typing import Any

from mcp.types import TextContent, Tool


class BaseTool(abc.ABC):
    """Base class for all tool handlers."""

    def __init__(self, client: Any = None, server: Any = None) -> None:
        """Initialize the tool handler.

        Args:
            client: The HTTP client to use for API requests
            server: The MCP server instance for accessing cached data
        """
        self.client = client
        self.server = server

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Get the name of the tool."""
        pass

    @property
    @abc.abstractmethod
    def description(self) -> str:
        """Get the description of the tool."""
        pass

    @property
    @abc.abstractmethod
    def input_schema(self) -> dict[str, Any]:
        """Get the input schema for the tool."""
        pass

    def get_tool_definition(self) -> Tool:
        """Get the tool definition for MCP."""
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema=self.input_schema,
        )

    @abc.abstractmethod
    async def execute(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Execute the tool with the given arguments.

        Args:
            arguments: The arguments to pass to the tool

        Returns:
            A list of TextContent objects with the tool's response
        """
        pass
