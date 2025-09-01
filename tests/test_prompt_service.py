# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
"""
Tests for PromptService functionality.
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.services.prompt_service import PromptContentResponse, PromptService


@pytest.fixture
def mock_client() -> MagicMock:
    """Mock HTTP client for testing."""
    client = MagicMock()
    client.get = AsyncMock()
    return client


@pytest.fixture
def prompt_service(mock_client: MagicMock) -> PromptService:
    """Create a PromptService instance for testing."""
    return PromptService(mock_client, "http://localhost:8080")


@pytest.fixture
def sample_prompts_data() -> list[dict[str, Any]]:
    """Sample prompts data for testing."""
    return [
        {
            "identifier": "test-prompt-1",
            "title": "Test Prompt 1",
            "categories": ["brainstorming", "testing"],
            "help_prompt_description": "A test prompt for brainstorming",
            "help_user_input": "Provide your brainstorming input",
            "help_sample_input": "Sample brainstorming input",
            "type": "chat",
            "download_restricted": False,
        },
        {
            "identifier": "test-prompt-2",
            "title": "Test Prompt 2",
            "categories": ["analysis"],
            "help_prompt_description": "A test prompt for analysis",
            "help_user_input": "Provide your analysis input",
            "help_sample_input": "Sample analysis input",
            "type": "chat",
            "download_restricted": False,
        },
        {
            "identifier": "restricted-prompt",
            "title": "Restricted Prompt",
            "categories": ["restricted"],
            "help_prompt_description": "This prompt should be filtered out",
            "help_user_input": "Restricted input",
            "help_sample_input": "Restricted sample",
            "type": "chat",
            "download_restricted": True,  # This should be filtered out
        },
    ]


class TestPromptServiceInitialization:
    """Test PromptService initialization."""

    def test_initialization(self, mock_client: MagicMock) -> None:
        """Test that PromptService initializes correctly."""
        service = PromptService(mock_client, "http://localhost:8080")

        assert service.client == mock_client
        assert service.base_url == "http://localhost:8080"
        assert service.prompts_loaded is False
        assert service.loaded_prompts == {}
        assert service.prompt_content_cache == {}

    def test_base_url_stripping(self, mock_client: MagicMock) -> None:
        """Test that base_url is properly stripped of trailing slashes."""
        service = PromptService(mock_client, "http://localhost:8080/")
        assert service.base_url == "http://localhost:8080"


class TestLoadPromptsFromAPI:
    """Test loading prompts from API."""

    @pytest.mark.asyncio
    async def test_load_prompts_success(self, prompt_service: PromptService, sample_prompts_data: list[dict[str, Any]]) -> None:
        """Test successful loading of prompts from API."""
        # Mock the HTTP response - httpx response methods are synchronous
        mock_response = MagicMock()
        mock_response.json.return_value = sample_prompts_data
        mock_response.raise_for_status.return_value = None

        with patch.object(prompt_service.client, "get", return_value=mock_response) as mock_get:
            result = await prompt_service.load_prompts_from_api()

            # Verify API call
            mock_get.assert_called_once_with("http://localhost:8080/api/prompts")

        # Verify result (should filter out restricted prompts)
        assert len(result) == 2
        assert result[0]["identifier"] == "test-prompt-1"
        assert result[1]["identifier"] == "test-prompt-2"
        assert "restricted-prompt" not in [p["identifier"] for p in result]

    @pytest.mark.asyncio
    async def test_load_prompts_http_error(self, prompt_service: PromptService) -> None:
        """Test handling of HTTP errors when loading prompts."""
        # Mock HTTP error
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"

        http_error = httpx.HTTPStatusError("Not Found", request=MagicMock(), response=mock_response)

        with patch.object(prompt_service.client, "get", side_effect=http_error):
            with pytest.raises(httpx.HTTPStatusError):
                await prompt_service.load_prompts_from_api()


class TestRegisterPrompts:
    """Test prompt registration."""

    @pytest.mark.asyncio
    async def test_register_prompts_success(self, prompt_service: PromptService, sample_prompts_data: list[dict[str, Any]]) -> None:
        """Test successful registration of prompts."""
        # Mock the API call
        with patch.object(prompt_service, "load_prompts_from_api", return_value=sample_prompts_data):
            await prompt_service.register_prompts()

        # Verify prompts were registered (should include all prompts, including restricted)
        assert prompt_service.prompts_loaded is True
        assert len(prompt_service.loaded_prompts) == 3  # All 3 prompts, including restricted

        # Verify metadata was stored correctly
        prompt1 = prompt_service.loaded_prompts["test-prompt-1"]
        assert prompt1["title"] == "Test Prompt 1"
        assert prompt1["categories"] == ["brainstorming", "testing"]
        assert prompt1["type"] == "chat"

        # Verify restricted prompt is also stored
        assert "restricted-prompt" in prompt_service.loaded_prompts

    @pytest.mark.asyncio
    async def test_register_prompts_api_failure(self, prompt_service: PromptService) -> None:
        """Test graceful handling of API failure during registration."""
        # Mock API failure
        with patch.object(prompt_service, "load_prompts_from_api", side_effect=Exception("API Error")):
            await prompt_service.register_prompts()

        # Should still mark as loaded but with 0 prompts
        assert prompt_service.prompts_loaded is True
        assert len(prompt_service.loaded_prompts) == 0


class TestGetCachedPromptsData:
    """Test getting cached prompts data."""

    def test_get_cached_prompts_data_not_loaded(self, prompt_service: PromptService) -> None:
        """Test getting cached data when prompts are not loaded."""
        result = prompt_service.get_cached_prompts_data()
        assert result == []

    def test_get_cached_prompts_data_loaded(self, prompt_service: PromptService) -> None:
        """Test getting cached data when prompts are loaded."""
        # Set up some test data
        prompt_service.prompts_loaded = True
        prompt_service.loaded_prompts = {
            "test-1": {
                "title": "Test 1",
                "categories": ["test"],
                "help_prompt_description": "Description 1",
                "help_user_input": "Input 1",
                "help_sample_input": "Sample 1",
                "type": "chat",
            },
        }

        result = prompt_service.get_cached_prompts_data()

        assert len(result) == 1
        assert result[0]["identifier"] == "test-1"
        assert result[0]["title"] == "Test 1"


class TestGetPromptContent:
    """Test getting prompt content."""

    @pytest.mark.asyncio
    async def test_get_prompt_content_cached(self, prompt_service: PromptService) -> None:
        """Test getting prompt content from cache."""
        # Set up cached content
        cached_response: PromptContentResponse = {
            "prompt_id": "test-prompt",
            "title": "Test Prompt",
            "content": "Cached content",
            "type": "chat",
            "follow_ups": [],
        }
        prompt_service.prompt_content_cache["test-prompt"] = cached_response

        result = await prompt_service.get_prompt_content("test-prompt")
        assert result is not None
        assert result == cached_response
        assert result["content"] == "Cached content"

    @pytest.mark.asyncio
    async def test_get_prompt_content_fetch_success(self, prompt_service: PromptService) -> None:
        """Test fetching and caching prompt content."""
        # Mock the HTTP response - these methods are synchronous in httpx
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "content": "Test content",
            "identifier": "test-prompt-1",
            "title": "Test Prompt",
            "type": "chat",
            "follow_ups": [],
        }
        mock_response.raise_for_status.return_value = None

        with patch.object(prompt_service.client, "get", return_value=mock_response) as mock_get:
            result = await prompt_service.get_prompt_content("test-prompt-1")

            # Verify API call
            mock_get.assert_called_once_with("http://localhost:8080/api/download-prompt?prompt_id=test-prompt-1")

        # Verify result
        assert result is not None
        assert result["content"] == "Test content"
        assert result["prompt_id"] == "test-prompt-1"
        assert result["type"] == "chat"

        # Verify content was cached
        assert "test-prompt-1" in prompt_service.prompt_content_cache


class TestUtilityMethods:
    """Test utility methods."""

    def test_is_prompt_loaded_true(self, prompt_service: PromptService) -> None:
        """Test is_prompt_loaded when prompt exists."""
        prompt_service.loaded_prompts["test-prompt"] = {
            "title": "Test",
            "categories": [],
            "help_prompt_description": "",
            "help_user_input": "",
            "help_sample_input": "",
            "type": "chat",
        }
        assert prompt_service.is_prompt_loaded("test-prompt") is True

    def test_is_prompt_loaded_false(self, prompt_service: PromptService) -> None:
        """Test is_prompt_loaded when prompt doesn't exist."""
        assert prompt_service.is_prompt_loaded("non-existent") is False

    def test_get_prompts_count_not_loaded(self, prompt_service: PromptService) -> None:
        """Test get_prompts_count when prompts are not loaded."""
        assert prompt_service.get_prompts_count() == 0

    def test_get_prompts_count_loaded(self, prompt_service: PromptService) -> None:
        """Test get_prompts_count when prompts are loaded."""
        prompt_service.prompts_loaded = True
        prompt_service.loaded_prompts = {
            "prompt-1": {
                "title": "Prompt 1",
                "categories": [],
                "help_prompt_description": "",
                "help_user_input": "",
                "help_sample_input": "",
                "type": "chat",
            },
            "prompt-2": {
                "title": "Prompt 2",
                "categories": [],
                "help_prompt_description": "",
                "help_user_input": "",
                "help_sample_input": "",
                "type": "chat",
            },
        }
        assert prompt_service.get_prompts_count() == 2
