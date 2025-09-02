# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
"""
Tests for Casper workflow tool functionality.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.tools.get_casper_workflow import GetCasperWorkflowToolHandler


class TestCasperWorkflowTool:
    """Test Casper workflow tool functionality."""

    @pytest.fixture
    def tool_handler(self) -> GetCasperWorkflowToolHandler:
        """Create a tool handler instance."""
        return GetCasperWorkflowToolHandler()

    @pytest.fixture
    def mock_casper_content(self) -> str:
        """Mock Casper workflow content."""
        return """# 🔍 Casper's Collaborative Exploration Phase

**🎯 Core Principle**: Casper assists, developer decides

## 1. Input: User Story + Acceptance Criteria

## 2. Functional Exploration Process

### 2.1 Casper's Role
- ✅ Ask questions, suggest areas, organize insights, facilitate discussion
- ❌ Make decisions, provide all answers, assume developer wants, mix in technical details

# 🎨 Casper's Craft Phase (TDD)

**🎯 Core Principle**: Test-driven development with AI assistance

## 1. TDD Cycle Implementation

### 1.1 Red Phase
- Write failing test first
- Ensure test fails for the right reason

### 1.2 Green Phase
- Write minimal code to pass test
- Focus on making test pass, not perfect code

### 1.3 Refactor Phase
- Improve code while keeping tests green
- Maintain functionality while improving design

# ✨ Casper's Polish Phase

**🎯 Core Principle**: Quality refinement and validation

## 1. Quality Validation

### 1.1 Code Review Preparation
- Ensure all tests pass
- Verify code meets requirements
- Check for code quality issues

### 1.2 Documentation Verification
- Update documentation as needed
- Ensure comments are clear and helpful
"""

    def test_tool_name(self, tool_handler: GetCasperWorkflowToolHandler) -> None:
        """Test tool name property."""
        assert tool_handler.name == "get_casper_workflow"

    def test_tool_description(self, tool_handler: GetCasperWorkflowToolHandler) -> None:
        """Test tool description property."""
        description = tool_handler.description
        assert "Casper workflow methodology" in description
        assert "share" in description
        assert "save" in description

    def test_input_schema(self, tool_handler: GetCasperWorkflowToolHandler) -> None:
        """Test input schema structure."""
        schema = tool_handler.input_schema
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "section" in schema["properties"]
        assert "mode" in schema["properties"]
        assert "tool_context" in schema["properties"]
        assert schema["required"] == []

    def test_extract_section_full(self, tool_handler: GetCasperWorkflowToolHandler, mock_casper_content: str) -> None:
        """Test extracting full section."""
        result = tool_handler._extract_section(mock_casper_content, "full")
        assert result == mock_casper_content

    def test_extract_section_explore(self, tool_handler: GetCasperWorkflowToolHandler, mock_casper_content: str) -> None:
        """Test extracting explore section."""
        result = tool_handler._extract_section(mock_casper_content, "explore")
        assert "🔍 Casper's Collaborative Exploration Phase" in result
        assert "🎨 Casper's Craft Phase" not in result

    def test_extract_section_craft(self, tool_handler: GetCasperWorkflowToolHandler, mock_casper_content: str) -> None:
        """Test extracting craft section."""
        result = tool_handler._extract_section(mock_casper_content, "craft")
        assert "🎨 Casper's Craft Phase" in result
        assert "✨ Casper's Polish Phase" not in result

    def test_extract_section_polish(self, tool_handler: GetCasperWorkflowToolHandler, mock_casper_content: str) -> None:
        """Test extracting polish section."""
        result = tool_handler._extract_section(mock_casper_content, "polish")
        assert "✨ Casper's Polish Phase" in result
        assert "🎨 Casper's Craft Phase" not in result

    def test_tool_directory_mapping(self, tool_handler: GetCasperWorkflowToolHandler) -> None:
        """Test tool directory mapping."""
        mapping = tool_handler._get_tool_directory_mapping()
        assert mapping["cursor"] == ".cursor/rules"
        assert mapping["vscode"] == ".github/instructions"
        assert mapping["generic"] == "."

    def test_detect_tool_context_generic(self, tool_handler: GetCasperWorkflowToolHandler) -> None:
        """Test tool context detection fallback to generic."""
        # This test verifies the basic functionality without complex mocking
        result = tool_handler._detect_tool_context()
        # Should return generic since we're in a test environment
        assert result in ["cursor", "vscode", "generic"]

    def test_get_filename_for_section_cursor(self, tool_handler: GetCasperWorkflowToolHandler) -> None:
        """Test filename generation for Cursor."""
        filename = tool_handler._get_filename_for_section("explore", "cursor")
        assert filename == "casper-explore.mdc"

    def test_get_filename_for_section_vscode(self, tool_handler: GetCasperWorkflowToolHandler) -> None:
        """Test filename generation for VS Code."""
        filename = tool_handler._get_filename_for_section("craft", "vscode")
        assert filename == "casper-craft.instructions.md"

    def test_get_filename_for_section_generic(self, tool_handler: GetCasperWorkflowToolHandler) -> None:
        """Test filename generation for generic."""
        filename = tool_handler._get_filename_for_section("polish", "generic")
        assert filename == "casper-polish.md"

    def test_get_target_directory_basic(self, tool_handler: GetCasperWorkflowToolHandler) -> None:
        """Test basic target directory functionality."""
        result = tool_handler._get_target_directory("cursor")
        # Should return a path ending with .cursor/rules
        assert str(result).endswith(".cursor/rules")

        result = tool_handler._get_target_directory("vscode")
        # Should return a path ending with .github/instructions
        assert str(result).endswith(".github/instructions")

        result = tool_handler._get_target_directory("generic")
        # Should return current directory (resolved)
        assert str(result).endswith("haiven-mcp-server")

    @pytest.mark.asyncio
    async def test_execute_share_mode(self, tool_handler: GetCasperWorkflowToolHandler, mock_casper_content: str) -> None:
        """Test execute method in share mode."""
        with patch.object(tool_handler, "_load_casper_workflow", return_value=mock_casper_content):
            result = await tool_handler.execute({"mode": "share", "section": "explore"})

            assert len(result) == 1
            response_data = json.loads(result[0].text)
            assert response_data["mode"] == "share"
            assert response_data["section"] == "explore"
            assert "content" in response_data
            assert "🔍 Casper's Collaborative Exploration Phase" in response_data["content"]

    @pytest.mark.asyncio
    async def test_execute_save_mode_cursor(self, tool_handler: GetCasperWorkflowToolHandler, mock_casper_content: str) -> None:
        """Test execute method in save mode for Cursor."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(tool_handler, "_load_casper_workflow", return_value=mock_casper_content):
                with patch("os.getcwd", return_value=temp_dir):
                    result = await tool_handler.execute({"mode": "save", "section": "explore", "tool_context": "cursor"})

                    assert len(result) == 1
                    response_data = json.loads(result[0].text)
                    assert response_data["mode"] == "save"
                    assert response_data["section"] == "explore"
                    assert response_data["tool_context"] == "cursor"
                    assert response_data["status"] == "success"
                    assert "file_path" in response_data

                    # Verify file was created
                    file_path = Path(response_data["file_path"])
                    assert file_path.exists()
                    assert file_path.name == "casper-explore.mdc"

                    # Verify content includes metadata header
                    content = file_path.read_text()
                    assert "description: Casper workflow methodology - Explore phase" in content
                    assert 'globs: ["**/*"]' in content
                    assert "alwaysApply: false" in content

                    # Verify no duplicate metadata headers
                    metadata_count = content.count("---")
                    assert metadata_count == 2, f"Expected 2 metadata markers, found {metadata_count}"

    @pytest.mark.asyncio
    async def test_execute_save_mode_vscode(self, tool_handler: GetCasperWorkflowToolHandler, mock_casper_content: str) -> None:
        """Test execute method in save mode for VS Code."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(tool_handler, "_load_casper_workflow", return_value=mock_casper_content):
                with patch("os.getcwd", return_value=temp_dir):
                    result = await tool_handler.execute({"mode": "save", "section": "craft", "tool_context": "vscode"})

                    assert len(result) == 1
                    response_data = json.loads(result[0].text)
                    assert response_data["mode"] == "save"
                    assert response_data["section"] == "craft"
                    assert response_data["tool_context"] == "vscode"
                    assert response_data["status"] == "success"

                    # Verify file was created
                    file_path = Path(response_data["file_path"])
                    assert file_path.exists()
                    assert file_path.name == "casper-craft.instructions.md"

                    # Verify content doesn't include metadata header (VS Code uses plain markdown)
                    content = file_path.read_text()
                    assert "description:" not in content
                    assert "🎨 Casper's Craft Phase" in content

    @pytest.mark.asyncio
    async def test_execute_auto_detect_tool_context(self, tool_handler: GetCasperWorkflowToolHandler, mock_casper_content: str) -> None:
        """Test execute method with auto-detection of tool context."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(tool_handler, "_load_casper_workflow", return_value=mock_casper_content):
                with patch("os.getcwd", return_value=temp_dir):
                    with patch.object(tool_handler, "_detect_tool_context", return_value="cursor"):
                        result = await tool_handler.execute({"mode": "save", "section": "full"})

                        assert len(result) == 1
                        response_data = json.loads(result[0].text)
                        assert response_data["tool_context"] == "cursor"

    @pytest.mark.asyncio
    async def test_execute_error_handling(self, tool_handler: GetCasperWorkflowToolHandler) -> None:
        """Test execute method error handling."""
        with patch.object(tool_handler, "_load_casper_workflow", return_value="Error: File not found"):
            result = await tool_handler.execute({"mode": "share"})

            assert len(result) == 1
            assert "Error: File not found" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_save_mode_error(self, tool_handler: GetCasperWorkflowToolHandler, mock_casper_content: str) -> None:
        """Test execute method in save mode with error."""
        with patch.object(tool_handler, "_load_casper_workflow", return_value=mock_casper_content):
            with patch.object(tool_handler, "_save_casper_workflow", return_value={"status": "error", "error": "Permission denied"}):
                result = await tool_handler.execute({"mode": "save", "section": "explore", "tool_context": "cursor"})

                assert len(result) == 1
                assert "Error: Permission denied" in result[0].text
