# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
"""
Get prompt text tool for Haiven MCP Server.
"""

import json
from typing import Any

import httpx
from loguru import logger
from mcp.types import TextContent

from .base_tool import BaseTool


class GetPromptTextToolHandler(BaseTool):
    """Handler for the get_prompt_text tool."""

    @property
    def name(self) -> str:
        """Get the name of the tool."""
        return "get_prompt_text"

    @property
    def description(self) -> str:
        """Get the description of the tool."""
        return "Get the prompt text content by prompt ID"

    @property
    def input_schema(self) -> dict[str, Any]:
        """Get the input schema for the tool."""
        return {
            "type": "object",
            "properties": {
                "prompt_id": {
                    "type": "string",
                    "description": "ID of the prompt to retrieve text for",
                }
            },
            "required": ["prompt_id"],
        }

    async def execute(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Execute the tool with the given arguments.

        Args:
            arguments: The arguments to pass to the tool

        Returns:
            A list of TextContent objects with the tool's response
        """
        try:
            prompt_id = arguments.get("prompt_id")
            if not prompt_id:
                return [TextContent(type="text", text="Error: prompt_id is required")]

            # Use the prompt service to get content
            if self.server and hasattr(self.server, "prompt_service"):
                prompt_data = await self.server.prompt_service.get_prompt_content(prompt_id)

                if prompt_data is None:
                    return [
                        TextContent(
                            type="text",
                            text=f"Error: Prompt with ID '{prompt_id}' not found or content unavailable",
                        )
                    ]

                # Extract content and metadata from the structured response
                content = prompt_data["content"]
                title = prompt_data["title"]
                prompt_type = prompt_data["type"]
                follow_ups = prompt_data["follow_ups"]

                # Format the response for better readability
                formatted_response = {
                    "prompt_id": prompt_id,
                    "title": title,
                    "content": content,
                    "type": prompt_type,
                    "follow_ups": follow_ups,
                }

                return [TextContent(type="text", text=json.dumps(formatted_response, indent=2))]
            else:
                logger.warning("No prompt service available - tool cannot function properly")
                return [TextContent(type="text", text="Error: Prompt service not available")]
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error from Haiven API: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            return [TextContent(type="text", text=f"Error: {error_msg}")]
        except Exception as e:
            error_msg = f"Error fetching prompt text: {str(e)}"
            logger.error(error_msg)
            return [TextContent(type="text", text=f"Error: {error_msg}")]
