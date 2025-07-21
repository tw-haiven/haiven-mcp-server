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

            base_url = self.client.base_url if hasattr(self.client, "base_url") else ""

            # Call the Haiven API to get the prompt with content
            response = await self.client.get(f"{base_url}/api/download-prompt?prompt_id={prompt_id}")
            response.raise_for_status()

            prompt_data = response.json()

            # Handle case where prompt is not found
            if not prompt_data:
                return [
                    TextContent(
                        type="text",
                        text=f"Error: Prompt with ID '{prompt_id}' not found",
                    )
                ]

            # If the response is a list (array of prompts), get the first one
            if isinstance(prompt_data, list):
                if len(prompt_data) == 0:
                    return [
                        TextContent(
                            type="text",
                            text=f"Error: Prompt with ID '{prompt_id}' not found",
                        )
                    ]
                prompt_data = prompt_data[0]

            # Format the response for better readability
            formatted_response = {
                "prompt_id": prompt_data.get("identifier", prompt_id),
                "title": prompt_data.get("title", "Unknown"),
                "content": prompt_data.get("content", "No content available"),
                "type": prompt_data.get("type", "chat"),
                "follow_ups": prompt_data.get("follow_ups", []),
            }

            return [TextContent(type="text", text=json.dumps(formatted_response, indent=2))]
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error from Haiven API: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            return [TextContent(type="text", text=f"Error: {error_msg}")]
        except Exception as e:
            error_msg = f"Error fetching prompt text: {str(e)}"
            logger.error(error_msg)
            return [TextContent(type="text", text=f"Error: {error_msg}")]
