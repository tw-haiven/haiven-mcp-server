# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
#!/usr/bin/env python3
"""
Test script for Haiven MCP Server

This script tests the MCP server implementation to ensure it works correctly
with the Haiven API endpoints.
"""

import asyncio
import json
import sys
from unittest.mock import AsyncMock, MagicMock, patch


async def test_mcp_server_creation() -> None:
    """Test that the MCP server can be created successfully."""

    with patch("httpx.AsyncClient"):
        from src.mcp_server import HaivenMCPServer

        # Test with default parameters
        server = HaivenMCPServer()
        assert server.base_url == "http://localhost:8080"
        assert server.server.name == "haiven-prompts"

        # Test with custom parameters
        server = HaivenMCPServer("http://custom:9000", api_key="test-key")
        assert server.base_url == "http://custom:9000"

        print("✓ MCP server creation test passed")


async def test_get_prompts_tool() -> None:
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

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = mock_prompts
        mock_response.raise_for_status.return_value = None
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        from src.mcp_server import HaivenMCPServer

        server = HaivenMCPServer("http://localhost:8000")
        tool = server.tool_registry.get_tool("get_prompts")
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


async def test_error_handling() -> None:
    """Test error handling in the get_prompts tool."""

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("Connection error")
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        from src.mcp_server import HaivenMCPServer

        server = HaivenMCPServer("http://localhost:8000")
        tool = server.tool_registry.get_tool("get_prompts")
        result = await tool.execute({})

        # Verify error is handled gracefully
        assert len(result) == 1
        content = result[0]
        assert content.type == "text"
        assert "Error" in content.text

        print("✓ Error handling test passed")


async def test_get_prompt_text_tool() -> None:
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

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = mock_prompt
        mock_response.raise_for_status.return_value = None
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        from src.mcp_server import HaivenMCPServer

        server = HaivenMCPServer("http://localhost:8000")
        tool = server.tool_registry.get_tool("get_prompt_text")

        # Test getting prompt text
        arguments = {"prompt_id": "test-prompt-1"}
        result = await tool.execute(arguments)

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


async def test_get_prompt_text_tool_not_found() -> None:
    """Test the get_prompt_text tool when prompt is not found."""

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = None
        mock_response.raise_for_status.return_value = None
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        from src.mcp_server import HaivenMCPServer

        server = HaivenMCPServer("http://localhost:8000")
        tool = server.tool_registry.get_tool("get_prompt_text")

        # Test getting prompt text for non-existent prompt
        arguments = {"prompt_id": "non-existent-prompt"}
        result = await tool.execute(arguments)

        # Verify response contains error message
        assert len(result) == 1
        content = result[0]
        assert content.type == "text"
        assert "Error" in content.text
        assert "not found" in content.text

        print("✓ get_prompt_text tool not found test passed")


async def main() -> None:
    """Run all tests."""
    try:
        print("Running Haiven MCP Server tests...")

        await test_mcp_server_creation()
        await test_get_prompts_tool()
        await test_error_handling()
        await test_get_prompt_text_tool()
        await test_get_prompt_text_tool_not_found()

        print("\n🎉 All tests passed!")
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
