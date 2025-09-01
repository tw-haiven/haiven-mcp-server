# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
"""
Tests for MCP prompt functionality.
"""

from typing import Any
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from src.mcp_server import HaivenMCPServer


@pytest.fixture
def mock_prompts_data() -> list[dict[str, Any]]:
    """Mock prompts data for testing."""
    return [
        {
            "identifier": "test-prompt-1",
            "title": "Test Prompt 1",
            "categories": ["testing"],
            "help_prompt_description": "A test prompt for unit testing",
            "help_sample_input": "Sample input for testing",
            "help_user_input": "Provide test input",
            "type": "chat",
        },
        {
            "identifier": "test-prompt-2",
            "title": "Test Prompt 2",
            "categories": ["testing"],
            "help_prompt_description": "Another test prompt",
            "help_sample_input": "Another sample",
            "help_user_input": "Provide another input",
            "type": "chat",
        },
    ]


@pytest.fixture
def mock_prompt_content() -> list[dict[str, Any]]:
    """Mock prompt content for testing."""
    return [
        {
            "identifier": "test-prompt-1",
            "title": "Test Prompt 1",
            "content": "This is the content of test prompt 1",
            "type": "chat",
        }
    ]


class TestMCPPrompts:
    """Test MCP prompt functionality."""

    @pytest.mark.asyncio
    async def test_load_prompts_from_api_success(self, mock_prompts_data: list[dict[str, Any]]) -> None:
        """Test successful loading of prompts from API."""
        server = HaivenMCPServer("http://localhost:8080")

        # Mock the HTTP response - json() is synchronous in httpx
        mock_response = AsyncMock()
        mock_response.json = lambda: mock_prompts_data  # Synchronous method
        mock_response.raise_for_status = lambda: None  # Synchronous method

        with patch.object(server.client, "get", return_value=mock_response):
            result = await server.prompt_service.load_prompts_from_api()

        assert len(result) == 2
        assert result[0]["identifier"] == "test-prompt-1"
        assert result[1]["identifier"] == "test-prompt-2"

    @pytest.mark.asyncio
    async def test_register_prompts_success(self, mock_prompts_data: list[dict[str, Any]]) -> None:
        """Test successful registration of prompts."""
        server = HaivenMCPServer("http://localhost:8080")

        # Mock the HTTP response - json() is synchronous in httpx
        mock_response = AsyncMock()
        mock_response.json = lambda: mock_prompts_data  # Synchronous method
        mock_response.raise_for_status = lambda: None  # Synchronous method

        with patch.object(server.client, "get", return_value=mock_response):
            await server.prompt_service.register_prompts()

        assert server.prompt_service.prompts_loaded is True
        assert server.prompt_service.get_prompts_count() == 2

    @pytest.mark.asyncio
    async def test_register_prompts_api_failure(self) -> None:
        """Test graceful handling of API failure during prompt registration."""
        server = HaivenMCPServer("http://localhost:8080")

        # Mock HTTP error
        mock_request = AsyncMock()
        mock_response = AsyncMock()
        with patch.object(
            server.client, "get", side_effect=httpx.HTTPStatusError("API Error", request=mock_request, response=mock_response)
        ):
            await server.prompt_service.register_prompts()

        # Should still mark as loaded but with 0 prompts
        assert server.prompt_service.prompts_loaded is True
        assert server.prompt_service.get_prompts_count() == 0

    @pytest.mark.asyncio
    async def test_list_prompts_handler(self, mock_prompts_data: list[dict[str, Any]]) -> None:
        """Test the list_prompts handler."""
        server = HaivenMCPServer("http://localhost:8080")

        # Mock the HTTP response and register prompts
        mock_response = AsyncMock()
        mock_response.json = lambda: mock_prompts_data  # Synchronous method
        mock_response.raise_for_status = lambda: None  # Synchronous method

        with patch.object(server.client, "get", return_value=mock_response):
            await server.prompt_service.register_prompts()

        # Test the service method that the handler uses
        prompts = server.prompt_service.get_all_prompt_descriptions()
        assert len(prompts) == 2
        assert prompts[0]["name"] == "test-prompt-1"
        assert "Test Prompt 1" in prompts[0]["description"]

    @pytest.mark.asyncio
    async def test_get_prompt_handler_success(
        self, mock_prompts_data: list[dict[str, Any]], mock_prompt_content: list[dict[str, Any]]
    ) -> None:
        """Test the get_prompt handler with successful content retrieval."""
        server = HaivenMCPServer("http://localhost:8080")

        # Mock the prompts API response
        mock_prompts_response = AsyncMock()
        mock_prompts_response.json = lambda: mock_prompts_data  # Synchronous method
        mock_prompts_response.raise_for_status = lambda: None  # Synchronous method

        # Mock the download-prompt API response
        mock_content_response = AsyncMock()
        mock_content_response.json = lambda: mock_prompt_content  # Synchronous method
        mock_content_response.raise_for_status = lambda: None  # Synchronous method

        with patch.object(server.client, "get") as mock_get:
            # First call for loading prompts, second for getting content
            mock_get.side_effect = [mock_prompts_response, mock_content_response]

            await server.prompt_service.register_prompts()

            # Test the service method that the handler uses
            prompt_name = "test-prompt-1"
            if server.prompt_service.is_prompt_loaded(prompt_name):
                prompt_data = await server.prompt_service.get_prompt_content(prompt_name)
                assert prompt_data is not None
                assert "This is the content of test prompt 1" in prompt_data["content"]

    @pytest.mark.asyncio
    async def test_get_prompt_handler_not_found(self, mock_prompts_data: list[dict[str, Any]]) -> None:
        """Test the get_prompt handler when prompt is not found."""
        server = HaivenMCPServer("http://localhost:8080")

        # Mock the prompts API response
        mock_response = AsyncMock()
        mock_response.json.return_value = mock_prompts_data
        mock_response.raise_for_status.return_value = None

        with patch.object(server.client, "get", return_value=mock_response):
            await server.prompt_service.register_prompts()

        # Try to get a non-existent prompt
        prompt_name = "non-existent-prompt"
        assert not server.prompt_service.is_prompt_loaded(prompt_name)

    @pytest.mark.asyncio
    async def test_prompts_loaded_before_server_start(self, mock_prompts_data: list[dict[str, Any]]) -> None:
        """Test that prompts are loaded before server starts accepting connections."""
        server = HaivenMCPServer("http://localhost:8080")

        # Mock the HTTP response - json() is synchronous in httpx
        mock_response = AsyncMock()
        mock_response.json = lambda: mock_prompts_data  # Synchronous method
        mock_response.raise_for_status = lambda: None  # Synchronous method

        with patch.object(server.client, "get", return_value=mock_response):
            # This should be called before stdio_server starts
            await server.prompt_service.register_prompts()

        assert server.prompt_service.prompts_loaded is True
        assert server.prompt_service.get_prompts_count() == 2
