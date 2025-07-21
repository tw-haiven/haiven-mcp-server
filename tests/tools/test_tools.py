# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
#!/usr/bin/env python3
"""
Test script for Haiven MCP Server Tools

This script tests the individual tool implementations to ensure they work correctly.
"""

import json
import os

# Add the src directory to the Python path for imports
import sys
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from tools import GetPromptsToolHandler, GetPromptTextToolHandler, ToolRegistry


@pytest.fixture
def mock_client() -> AsyncMock:
    """Create a mock HTTP client."""
    client = AsyncMock()
    client.base_url = "http://localhost:8000"
    return client


async def test_tool_registry(mock_client: Any) -> None:
    """Test the tool registry functionality."""
    registry = ToolRegistry(mock_client)

    # Register tools
    registry.register_tool(GetPromptsToolHandler)
    registry.register_tool(GetPromptTextToolHandler)

    # Check that tools are registered
    assert len(registry.tools) == 2
    assert "get_prompts" in registry.tools
    assert "get_prompt_text" in registry.tools

    # Get tool definitions
    tools = registry.get_all_tools()
    assert len(tools) == 2

    # Check tool retrieval
    get_prompts_tool = registry.get_tool("get_prompts")
    assert isinstance(get_prompts_tool, GetPromptsToolHandler)

    # Check error on unknown tool
    with pytest.raises(ValueError):
        registry.get_tool("unknown_tool")

    print("✓ Tool registry test passed")


async def test_get_prompts_tool(mock_client: Any) -> None:
    """Test the get_prompts tool."""
    # Mock response data
    mock_prompts = [
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

    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = mock_prompts
    mock_response.raise_for_status.return_value = None
    mock_client.get.return_value = mock_response

    # Create and execute tool
    tool = GetPromptsToolHandler(mock_client)
    result = await tool.execute({})

    # Verify API call
    mock_client.get.assert_called_once_with("http://localhost:8000/api/prompts")

    # Verify response format
    assert len(result) == 1
    content = result[0]
    assert content.type == "text"

    response_data = json.loads(content.text)
    assert "prompts" in response_data
    assert "total_count" in response_data
    assert response_data["total_count"] == 2
    # Compare only the fields that are included in the filtered output
    expected_prompts = [
        {
            "identifier": "test-prompt-1",
            "title": "Test Prompt 1",
            "categories": ["brainstorming"],
            "help_prompt_description": "A test prompt for brainstorming",
            "help_user_input": "",
            "help_sample_input": "",
            "type": "",
        },
        {
            "identifier": "test-prompt-2",
            "title": "Test Prompt 2",
            "categories": ["analysis"],
            "help_prompt_description": "A test prompt for analysis",
            "help_user_input": "",
            "help_sample_input": "",
            "type": "",
        },
    ]
    assert response_data["prompts"] == expected_prompts

    print("✓ get_prompts tool test passed")


async def test_get_prompt_text_tool(mock_client: Any) -> None:
    """Test the get_prompt_text tool."""
    # Mock response data for a prompt with content
    mock_prompt = {
        "identifier": "test-prompt-1",
        "title": "Test Prompt 1",
        "categories": ["brainstorming"],
        "help_prompt_description": "A test prompt for brainstorming",
        "content": "This is the prompt template: {user_input}\n\nContext: {context}",
        "follow_ups": [],
    }

    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = mock_prompt
    mock_response.raise_for_status.return_value = None
    mock_client.get.return_value = mock_response

    # Create and execute tool
    tool = GetPromptTextToolHandler(mock_client)
    result = await tool.execute({"prompt_id": "test-prompt-1"})

    # Verify API call
    mock_client.get.assert_called_once_with("http://localhost:8000/api/download-prompt?prompt_id=test-prompt-1")

    # Verify response format
    assert len(result) == 1
    content = result[0]
    assert content.type == "text"

    response_data = json.loads(content.text)
    assert "prompt_id" in response_data
    assert "title" in response_data
    assert "content" in response_data
    assert response_data["prompt_id"] == "test-prompt-1"
    assert response_data["title"] == "Test Prompt 1"
    assert response_data["content"] == "This is the prompt template: {user_input}\n\nContext: {context}"

    print("✓ get_prompt_text tool test passed")


async def test_get_prompt_text_tool_missing_id(mock_client: Any) -> None:
    """Test the get_prompt_text tool with missing prompt_id."""
    tool = GetPromptTextToolHandler(mock_client)
    result = await tool.execute({})

    # Verify error response
    assert len(result) == 1
    content = result[0]
    assert content.type == "text"
    assert "Error: prompt_id is required" in content.text

    print("✓ get_prompt_text tool missing ID test passed")


async def test_error_handling(mock_client: Any) -> None:
    """Test error handling in tools."""
    # Setup mock response with error
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("Connection error")
    mock_client.get.return_value = mock_response

    # Test get_prompts tool error handling
    prompts_tool = GetPromptsToolHandler(mock_client)
    result = await prompts_tool.execute({})

    # Verify error is handled gracefully
    assert len(result) == 1
    content = result[0]
    assert content.type == "text"
    assert "Error" in content.text

    print("✓ Error handling test passed")


async def main() -> None:
    """Run all tests."""
    try:
        print("Running Haiven MCP Server Tools tests...")

        mock_client = AsyncMock()
        mock_client.base_url = "http://localhost:8000"

        await test_tool_registry(mock_client)
        await test_get_prompts_tool(mock_client)
        await test_get_prompt_text_tool(mock_client)
        await test_get_prompt_text_tool_missing_id(mock_client)
        await test_error_handling(mock_client)

        print("\n🎉 All tool tests passed!")
    except Exception as e:
        print(f"Test failed: {e}")
        import sys

        sys.exit(1)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
