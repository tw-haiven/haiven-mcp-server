# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
"""
Get prompts tool for Haiven MCP Server.
"""

import json
from typing import Any

import httpx
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
            base_url = self.client.base_url if hasattr(self.client, "base_url") else ""
            response = await self.client.get(f"{base_url}/api/prompts")
            response.raise_for_status()

            prompts_data = response.json()

            # Filter prompts to only include the specified fields
            filtered_prompts = []
            for prompt in prompts_data:
                filtered_prompt = {
                    "identifier": prompt.get("identifier", ""),
                    "title": prompt.get("title", ""),
                    "categories": prompt.get("categories", []),
                    "help_prompt_description": prompt.get("help_prompt_description", ""),
                    "help_user_input": prompt.get("help_user_input", ""),
                    "help_sample_input": prompt.get("help_sample_input", ""),
                    "type": prompt.get("type", ""),
                }
                filtered_prompts.append(filtered_prompt)

            # Format the response with instructions for the LLM
            formatted_response = {
                "prompts": filtered_prompts,
                "total_count": len(filtered_prompts) if isinstance(filtered_prompts, list) else 0,
            }

            return [TextContent(type="text", text=json.dumps(formatted_response, indent=2))]

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error from Haiven API: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            return [TextContent(type="text", text=f"Error: {error_msg}")]
        except Exception as e:
            error_msg = f"Error fetching prompts: {str(e)}"
            logger.error(error_msg)
            return [TextContent(type="text", text=f"Error: {error_msg}")]
