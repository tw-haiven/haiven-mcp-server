# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
"""
Get prompts tool for Haiven MCP Server.
"""

import json
from typing import Any

from loguru import logger
from mcp.types import TextContent

from .base_tool import BaseTool


class GetPromptsToolHandler(BaseTool):
    """Handler for the get_prompts tool."""

    @property
    def name(self) -> str:
        """Get the name of the tool."""
        return "get_prompts"

    @property
    def description(self) -> str:
        """Get the description of the tool."""
        return "Get all available prompts with their metadata and follow-ups"

    @property
    def input_schema(self) -> dict[str, Any]:
        """Get the input schema for the tool."""
        return {
            "type": "object",
            "properties": {},
            "required": [],
        }

    async def execute(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Execute the tool with the given arguments.

        Args:
            arguments: The arguments to pass to the tool

        Returns:
            A list of TextContent objects with the tool's response
        """
        try:
            # Use the prompt service to get cached data
            if self.server and hasattr(self.server, "prompt_service"):
                prompts_data = self.server.prompt_service.get_cached_prompts_data()
                if prompts_data:
                    logger.debug("Using cached prompts data for get_prompts tool")
                else:
                    logger.warning("No prompts available - service may not be initialized")
                    prompts_data = []
            else:
                logger.warning("No prompt service available - tool cannot function properly")
                return [TextContent(type="text", text="Error: Prompt service not available")]

            # Format the response with instructions for the LLM
            formatted_response = {
                "prompts": prompts_data,
                "total_count": len(prompts_data) if isinstance(prompts_data, list) else 0,
            }

            return [TextContent(type="text", text=json.dumps(formatted_response, indent=2))]

        except Exception as e:
            error_msg = f"Error fetching prompts: {str(e)}"
            logger.error(error_msg)
            return [TextContent(type="text", text=f"Error: {error_msg}")]
