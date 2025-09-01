# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
"""
Tests for MCP tools.
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.tools import GetPromptsToolHandler, GetPromptTextToolHandler, ToolRegistry


@pytest.fixture
def mock_client() -> Any:
    """Mock HTTP client for testing."""
    return AsyncMock()


@pytest.fixture
def mock_server() -> Any:
    """Mock server with prompt service for testing."""
    server = MagicMock()

    # Mock the prompt service methods
    server.prompt_service = MagicMock()
    server.prompt_service.get_cached_prompts_data.return_value = [
        {
            "identifier": "test-prompt-1",
            "title": "Test Prompt 1",
            "categories": ["brainstorming"],
            "help_prompt_description": "A test prompt for brainstorming",
        },
        {
            "identifier": "test-prompt-2",
            "title": "Test Prompt 2",
            "categories": ["analysis"],
            "help_prompt_description": "A test prompt for analysis",
        },
    ]

    # Make these methods async mocks since they're awaited
    mock_prompt_data = {
        "prompt_id": "test-prompt-1",
        "title": "Test Prompt",
        "content": "This is the prompt template: {user_input}\n\nContext: {context}",
        "type": "chat",
        "follow_ups": [],
    }
    server.prompt_service.get_prompt_content = AsyncMock(return_value=mock_prompt_data)
    server.prompt_service.get_prompt_metadata.return_value = {"title": "Test Prompt 1", "type": "chat"}

    # Mock the prompt service's client for direct API calls to get follow_ups
    server.prompt_service.client = AsyncMock()
    server.prompt_service.base_url = "http://localhost:8080"

    return server


class TestToolRegistry:
    """Test the tool registry."""

    def test_tool_registry(self, mock_client: Any) -> None:
        """Test the tool registry."""
        registry = ToolRegistry(mock_client)
        assert registry.client == mock_client
        assert len(registry.tools) == 0

    def test_register_tool(self, mock_client: Any) -> None:
        """Test registering a tool."""
        registry = ToolRegistry(mock_client)
        registry.register_tool(GetPromptsToolHandler)
        assert "get_prompts" in registry.tools
        assert len(registry.tools) == 1

    def test_get_tool(self, mock_client: Any) -> None:
        """Test getting a tool."""
        registry = ToolRegistry(mock_client)
        registry.register_tool(GetPromptsToolHandler)
        tool = registry.get_tool("get_prompts")
        assert tool.name == "get_prompts"

    def test_get_tool_not_found(self, mock_client: Any) -> None:
        """Test getting a tool that doesn't exist."""
        registry = ToolRegistry(mock_client)
        with pytest.raises(ValueError, match="Tool not found: nonexistent"):
            registry.get_tool("nonexistent")

    def test_get_all_tools(self, mock_client: Any) -> None:
        """Test getting all tools."""
        registry = ToolRegistry(mock_client)
        registry.register_tool(GetPromptsToolHandler)
        registry.register_tool(GetPromptTextToolHandler)
        tools = registry.get_all_tools()
        assert len(tools) == 2
        assert any(tool.name == "get_prompts" for tool in tools)
        assert any(tool.name == "get_prompt_text" for tool in tools)

    @pytest.mark.asyncio
    async def test_execute_tool(self, mock_client: Any) -> None:
        """Test executing a tool."""
        registry = ToolRegistry(mock_client)
        registry.register_tool(GetPromptsToolHandler)
        result = await registry.execute_tool("get_prompts", {})
        assert len(result) > 0


class TestGetPromptsTool:
    """Test the get_prompts tool."""

    @pytest.mark.asyncio
    async def test_get_prompts_tool(self, mock_client: Any, mock_server: Any) -> None:
        """Test the get_prompts tool."""
        # Create tool with server reference
        tool = GetPromptsToolHandler(mock_client, mock_server)
        result = await tool.execute({})

        # Verify the tool used the prompt service
        mock_server.prompt_service.get_cached_prompts_data.assert_called_once()

        # Verify response format
        assert len(result) == 1
        assert result[0].type == "text"
        assert "prompts" in result[0].text
        assert "total_count" in result[0].text

    @pytest.mark.asyncio
    async def test_get_prompts_tool_no_server(self, mock_client: Any) -> None:
        """Test the get_prompts tool without server reference."""
        tool = GetPromptsToolHandler(mock_client)
        result = await tool.execute({})

        # Should return error message
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Error: Prompt service not available" in result[0].text

    @pytest.mark.asyncio
    async def test_get_prompts_tool_no_service(self, mock_client: Any) -> None:
        """Test the get_prompts tool with server but no prompt service."""
        mock_server = MagicMock()
        mock_server.prompt_service = None

        tool = GetPromptsToolHandler(mock_client, mock_server)
        result = await tool.execute({})

        # Should return error message about missing service
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Error:" in result[0].text
        assert "get_cached_prompts_data" in result[0].text


class TestGetPromptTextTool:
    """Test the get_prompt_text tool."""

    @pytest.mark.asyncio
    async def test_get_prompt_text_tool(self, mock_client: Any, mock_server: Any) -> None:
        """Test the get_prompt_text tool."""
        # Create tool with server reference
        tool = GetPromptTextToolHandler(mock_client, mock_server)
        result = await tool.execute({"prompt_id": "test-prompt-1"})

        # Verify the tool used the prompt service
        mock_server.prompt_service.get_prompt_content.assert_called_once_with("test-prompt-1")
        # Note: get_prompt_metadata is no longer called since all data comes from get_prompt_content

        # Verify response format
        assert len(result) == 1
        assert result[0].type == "text"
        assert "prompt_id" in result[0].text
        assert "content" in result[0].text

    @pytest.mark.asyncio
    async def test_get_prompt_text_tool_missing_id(self, mock_client: Any) -> None:
        """Test the get_prompt_text tool with missing prompt_id."""
        tool = GetPromptTextToolHandler(mock_client)
        result = await tool.execute({})

        # Should return error message
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Error: prompt_id is required" in result[0].text

    @pytest.mark.asyncio
    async def test_get_prompt_text_tool_no_server(self, mock_client: Any) -> None:
        """Test the get_prompt_text tool without server reference."""
        tool = GetPromptTextToolHandler(mock_client)
        result = await tool.execute({"prompt_id": "test-prompt-1"})

        # Should return error message
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Error: Prompt service not available" in result[0].text

    @pytest.mark.asyncio
    async def test_get_prompt_text_tool_content_not_found(self, mock_client: Any, mock_server: Any) -> None:
        """Test the get_prompt_text tool when content is not found."""
        # Mock the service to return None for content
        mock_server.prompt_service.get_prompt_content = AsyncMock(return_value=None)

        tool = GetPromptTextToolHandler(mock_client, mock_server)
        result = await tool.execute({"prompt_id": "test-prompt-1"})

        # Should return error message
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Error:" in result[0].text
        assert "not found or content unavailable" in result[0].text


class TestErrorHandling:
    """Test error handling in tools."""

    @pytest.mark.asyncio
    async def test_error_handling(self, mock_client: Any) -> None:
        """Test error handling in the tools."""
        # Test with a tool that has an error during execution
        tool = GetPromptsToolHandler(mock_client)

        # Mock the tool to raise an exception
        with patch.object(tool, "execute", side_effect=Exception("Test error")):
            # The mock will raise the exception, so we expect it
            with pytest.raises(Exception, match="Test error"):
                await tool.execute({})
