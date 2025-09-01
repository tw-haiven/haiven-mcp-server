# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
"""
Prompt service for Haiven MCP Server.

This service handles all prompt-related operations including API calls, caching, and data formatting.
"""

from typing import Any, TypedDict

import httpx
from loguru import logger


class PromptMetadata(TypedDict):
    """Type definition for prompt metadata."""

    title: str
    categories: list[str]
    help_prompt_description: str
    help_user_input: str
    help_sample_input: str
    type: str


class PromptData(TypedDict):
    """Type definition for prompt data from API."""

    identifier: str
    title: str
    categories: list[str]
    help_prompt_description: str
    help_user_input: str
    help_sample_input: str
    type: str
    download_restricted: bool


class PromptDescription(TypedDict):
    """Type definition for prompt descriptions in MCP format."""

    name: str
    description: str


class PromptContentResponse(TypedDict):
    """Type definition for prompt content response."""

    prompt_id: str
    title: str
    content: str
    type: str
    follow_ups: list[str]


class PromptService:
    """Service for handling prompt operations."""

    def __init__(self, client: httpx.AsyncClient, base_url: str):
        """Initialize the prompt service.

        Args:
            client: The HTTP client to use for API requests
            base_url: The base URL for the Haiven API
        """
        self.client = client
        self.base_url = base_url.rstrip("/")
        self.prompts_loaded = False
        self.loaded_prompts: dict[str, PromptMetadata] = {}
        self.prompt_content_cache: dict[str, PromptContentResponse] = {}

    async def load_prompts_from_api(self) -> list[PromptData]:
        """Load prompts from the Haiven API.

        Returns:
            List of prompt metadata from the API

        Raises:
            httpx.HTTPStatusError: If API call fails
            Exception: For other errors during prompt loading
        """
        try:
            logger.info("Loading prompts from Haiven API...")
            response = await self.client.get(f"{self.base_url}/api/prompts")
            response.raise_for_status()

            # Filter out prompts with download_restricted set to true
            prompts_data: list[PromptData] = response.json()
            prompts_data = [prompt for prompt in prompts_data if not prompt.get("download_restricted", False)]

            logger.info(f"Successfully loaded {len(prompts_data)} prompts from API")
            return prompts_data

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error loading prompts: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error loading prompts from API: {str(e)}")
            raise

    async def register_prompts(self) -> None:
        """Register all prompts from the API and store metadata."""
        try:
            prompts_data: list[PromptData] = await self.load_prompts_from_api()

            for prompt in prompts_data:
                prompt_id = prompt["identifier"]
                if not prompt_id:
                    logger.warning("Skipping prompt with missing identifier")
                    continue

                # Store prompt metadata using the proper type structure
                self.loaded_prompts[prompt_id] = PromptMetadata(
                    title=prompt["title"],
                    categories=prompt["categories"],
                    help_prompt_description=prompt["help_prompt_description"],
                    help_user_input=prompt["help_user_input"],
                    help_sample_input=prompt["help_sample_input"],
                    type=prompt["type"],
                )

            self.prompts_loaded = True
            logger.info(f"Successfully registered {len(self.loaded_prompts)} prompts")

        except Exception as e:
            logger.error(f"Failed to register prompts: {str(e)}")
            # Continue with empty prompts - graceful degradation
            self.prompts_loaded = True
            logger.warning("Continuing with 0 prompts due to loading failure")

    def get_cached_prompts_data(self) -> list[PromptData]:
        """Get cached prompts metadata.

        Returns:
            List of prompt metadata in the format expected by tools
        """
        if not self.prompts_loaded:
            return []

        # Convert cached metadata back to the format expected by tools
        cached_data: list[PromptData] = []
        for prompt_id, metadata in self.loaded_prompts.items():
            cached_data.append(
                PromptData(
                    identifier=prompt_id,
                    title=metadata["title"],
                    categories=metadata["categories"],
                    help_prompt_description=metadata["help_prompt_description"],
                    help_user_input=metadata["help_user_input"],
                    help_sample_input=metadata["help_sample_input"],
                    type=metadata["type"],
                    download_restricted=False,  # Cached prompts are already filtered
                )
            )

        return cached_data

    async def get_prompt_content(self, prompt_id: str) -> PromptContentResponse | None:
        """Get prompt content with full metadata, fetching if not cached.

        Args:
            prompt_id: The ID of the prompt to fetch

        Returns:
            The full prompt data including content, title, type, and follow_ups, or None if not found
        """
        if prompt_id in self.prompt_content_cache:
            logger.debug(f"Using cached content for prompt: {prompt_id}")
            return self.prompt_content_cache[prompt_id]

        try:
            # Fetch and cache the content
            logger.debug(f"Fetching and caching content for prompt: {prompt_id}")
            response = await self.client.get(f"{self.base_url}/api/download-prompt?prompt_id={prompt_id}")
            response.raise_for_status()

            prompt_data = response.json()

            if not prompt_data:
                return None

            # If the response is a list, get the first one
            if isinstance(prompt_data, list):
                if len(prompt_data) == 0:
                    return None
                prompt_data = prompt_data[0]

            # Format the response for better readability
            formatted_response: PromptContentResponse = {
                "prompt_id": prompt_data.get("identifier", prompt_id),
                "title": prompt_data.get("title", "Unknown"),
                "content": prompt_data.get("content", "No content available"),
                "type": prompt_data.get("type", "chat"),
                "follow_ups": prompt_data.get("follow_ups", []),
            }

            self.prompt_content_cache[prompt_id] = formatted_response
            logger.debug(f"Cached content for prompt: {prompt_id}")
            return formatted_response

        except Exception as e:
            logger.error(f"Error fetching prompt content for {prompt_id}: {str(e)}")
            return None

    def get_prompt_metadata(self, prompt_id: str) -> PromptMetadata | None:
        """Get prompt metadata by ID.

        Args:
            prompt_id: The ID of the prompt

        Returns:
            The prompt metadata or None if not found
        """
        return self.loaded_prompts.get(prompt_id)

    def format_prompt_description(self, prompt_id: str) -> str:
        """Format a prompt description for display.

        Args:
            prompt_id: The ID of the prompt

        Returns:
            Formatted description string
        """
        metadata: PromptMetadata | dict[str, Any] = self.loaded_prompts.get(prompt_id, {})
        title = metadata.get("title", "")
        description = metadata.get("help_prompt_description", "")
        categories = metadata.get("categories", [])

        categories_str = ", ".join(categories) if categories else ""
        formatted_desc = f"{title}: {description}"

        if categories_str:
            formatted_desc += f" (Categories: {categories_str})"

        return formatted_desc

    def get_all_prompt_descriptions(self) -> list[PromptDescription]:
        """Get all prompt descriptions for MCP list_prompts.

        Returns:
            List of prompt descriptions in MCP format
        """
        if not self.prompts_loaded:
            return []

        prompts: list[PromptDescription] = []
        for prompt_id in self.loaded_prompts:
            prompts.append(
                PromptDescription(
                    name=prompt_id,
                    description=self.format_prompt_description(prompt_id),
                )
            )

        return prompts

    def is_prompt_loaded(self, prompt_id: str) -> bool:
        """Check if a prompt is loaded.

        Args:
            prompt_id: The ID of the prompt to check

        Returns:
            True if the prompt is loaded, False otherwise
        """
        return prompt_id in self.loaded_prompts

    def get_prompts_count(self) -> int:
        """Get the total number of loaded prompts.

        Returns:
            The number of loaded prompts
        """
        return len(self.loaded_prompts) if self.prompts_loaded else 0
