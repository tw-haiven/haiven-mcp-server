# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
"""
Get Casper workflow tool for Haiven MCP Server.

This tool provides the Casper workflow methodology as rules/instructions that can be accessed
via MCP by tools like VS Code, Cursor, etc.
"""

import json
from pathlib import Path
from typing import Any

from loguru import logger
from mcp.types import TextContent

from .base_tool import BaseTool


class GetCasperWorkflowToolHandler(BaseTool):
    """Handler for the get_casper_workflow tool."""

    # Constants
    CASPER_RULE_ID = "casper-workflow"
    SECTIONS = ["explore", "craft", "polish", "full"]
    MODES = ["share", "save"]
    TOOL_CONTEXTS = ["cursor", "vscode", "generic"]

    # Section markers for content extraction
    SECTION_MARKERS = {
        "explore": ("# 🔍 Casper's Collaborative Exploration Phase", "# 🎨 Casper's Craft Phase"),
        "craft": ("# 🎨 Casper's Craft Phase (TDD)", "# ✨ Casper's Polish Phase"),
        "polish": ("# ✨ Casper's Polish Phase", None),  # Polish is the last section
    }

    # Tool directory mappings
    TOOL_DIRECTORY_MAPPING = {"cursor": ".cursor/rules", "vscode": ".github/instructions", "generic": "."}

    @property
    def name(self) -> str:
        """Get the name of the tool."""
        return "get_casper_workflow"

    @property
    def description(self) -> str:
        """Get the description of the tool."""
        return (
            "Get or save the Casper workflow methodology as rules/instructions for AI development guidance. "
            "Supports two modes: 'share' (returns content to LLM) or 'save' (saves to appropriate tool directory "
            "like .cursor/rules or .github/instructions)"
        )

    @property
    def input_schema(self) -> dict[str, Any]:
        """Get the input schema for the tool."""
        return {
            "type": "object",
            "properties": {
                "section": {
                    "type": "string",
                    "description": "Optional section to retrieve (explore, craft, polish, or full). Defaults to 'full'.",
                    "enum": self.SECTIONS,
                },
                "mode": {
                    "type": "string",
                    "description": (
                        "Mode of operation: 'share' returns content to LLM, 'save' saves to appropriate directory. Defaults to 'share'."
                    ),
                    "enum": self.MODES,
                },
                "tool_context": {
                    "type": "string",
                    "description": (
                        "Optional tool context for save mode to determine target directory (cursor, vscode, etc.). "
                        "Auto-detected if not provided."
                    ),
                    "enum": self.TOOL_CONTEXTS,
                },
                "project_directory": {
                    "type": "string",
                    "description": (
                        "Optional project directory path. When provided, the tool will save files relative to "
                        "this directory instead of the current working directory."
                    ),
                },
            },
            "required": [],
        }

    async def _load_casper_workflow(self) -> str:
        """Load the Casper workflow content from the Haiven API."""
        try:
            # Use the prompt service to get rules content
            if self.server and hasattr(self.server, "prompt_service"):
                content = await self.server.prompt_service.get_rules_content(self.CASPER_RULE_ID)

                if content is None:
                    error_msg = (
                        f"Casper workflow rules not found for rule_id '{self.CASPER_RULE_ID}'. "
                        "Please ensure the rules endpoint is available."
                    )
                    logger.error(error_msg)
                    return f"Error: {error_msg}"

                logger.info("Successfully loaded Casper workflow from API rules endpoint")
                return str(content)
            else:
                error_msg = "No prompt service available - tool cannot function properly"
                logger.error(error_msg)
                return f"Error: {error_msg}"

        except Exception as e:
            error_msg = f"Error loading Casper workflow from API: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"

    def _extract_section(self, content: str, section: str) -> str:
        """Extract a specific section from the Casper workflow content."""
        if section == "full":
            return content

        if section not in self.SECTION_MARKERS:
            return content

        start_marker, end_marker = self.SECTION_MARKERS[section]

        # Find the start of the section
        start_index = content.find(start_marker)
        if start_index == -1:
            logger.warning(f"Section marker '{start_marker}' not found")
            return content

        # Find the end of the section (if specified)
        if end_marker:
            end_index = content.find(end_marker, start_index)
            if end_index == -1:
                logger.warning(f"End marker '{end_marker}' not found")
                return content[start_index:]
            return content[start_index:end_index]
        else:
            # For the last section (polish), return everything from start to end
            return content[start_index:]

    def _get_tool_directory_mapping(self) -> dict[str, str]:
        """Get the directory mapping for different AI tools."""
        return self.TOOL_DIRECTORY_MAPPING

    def _detect_tool_context(self) -> str:
        """Auto-detect the tool context based on the environment or directory structure."""
        current_path = Path.cwd()

        # Check for Cursor-specific indicators in the current directory or parents
        for path in [current_path] + list(current_path.parents):
            if (path / ".cursor").exists() or (path / ".cursorrules").exists():
                return "cursor"
            if (path / ".vscode").exists() or (path / ".github").exists():
                return "vscode"
            # Stop at project root indicators
            if (path / ".git").exists() or (path / "pyproject.toml").exists() or (path / "package.json").exists():
                break

        # Default to generic
        return "generic"

    def _get_target_directory(self, tool_context: str, project_directory: str | None = None) -> Path:
        """Get the target directory for saving the casper workflow file."""
        mapping = self._get_tool_directory_mapping()
        target_dir = mapping.get(tool_context, mapping["generic"])

        # For tool-specific directories, ensure we're in a project context
        if tool_context in ["cursor", "vscode"]:
            # Use project_directory if provided, otherwise fall back to current working directory
            if project_directory:
                base_path = Path(project_directory).resolve()
            else:
                base_path = Path.cwd()

            # Check if the base path is a project directory (has .git, pyproject.toml, or package.json)
            has_git = (base_path / ".git").exists()
            has_pyproject = (base_path / "pyproject.toml").exists()
            has_package = (base_path / "package.json").exists()

            if has_git or has_pyproject or has_package:
                target_path = base_path / target_dir
                logger.debug(f"Using project directory: {target_path}")
                return target_path

            # If not in a project directory, look for existing tool directories in parent directories
            for path in list(base_path.parents):
                tool_dir = path / target_dir
                if tool_dir.exists():
                    logger.debug(f"Found existing tool directory: {tool_dir}")
                    return tool_dir
                # Also check if we should create the directory in a parent project
                if (path / ".git").exists() or (path / "pyproject.toml").exists() or (path / "package.json").exists():
                    logger.debug(f"Found parent project directory: {path / target_dir}")
                    return path / target_dir

        result = Path(target_dir).resolve()
        logger.info(f"Using generic target directory: {result}")
        return result

    def _get_filename_for_section(self, section: str, tool_context: str) -> str:
        """Get the appropriate filename for the section and tool context."""
        if tool_context == "cursor":
            # Cursor uses .mdc files for rules
            return f"casper-{section}.mdc"
        elif tool_context == "vscode":
            # VS Code uses .instructions.md files
            return f"casper-{section}.instructions.md"
        else:
            # Generic fallback
            return f"casper-{section}.md"

    def _add_cursor_frontmatter(self, content: str, section: str) -> str:
        """Add Cursor-specific frontmatter to content."""
        frontmatter = f"""---
description: Casper workflow methodology - {section.title()} phase
globs: ["**/*"]
alwaysApply: false
---

"""

        # Check if content already has YAML frontmatter
        if content.startswith("---\n"):
            # Extract existing frontmatter and content
            parts = content.split("---\n", 2)
            if len(parts) >= 3:
                # Use the main content after the existing frontmatter
                main_content = parts[2]
                return frontmatter + main_content
            else:
                # Fallback if frontmatter parsing fails
                return frontmatter + content
        else:
            # No existing frontmatter, add our metadata
            return frontmatter + content

    def _save_casper_workflow(self, content: str, section: str, tool_context: str, project_directory: str | None = None) -> dict[str, Any]:
        """Save the casper workflow content to the appropriate directory."""
        try:
            # Get target directory
            target_dir = self._get_target_directory(tool_context, project_directory)

            # Create directory if it doesn't exist
            target_dir.mkdir(parents=True, exist_ok=True)

            # Get filename
            filename = self._get_filename_for_section(section, tool_context)
            file_path = target_dir / filename

            # Add metadata header for Cursor .mdc files
            if tool_context == "cursor" and filename.endswith(".mdc"):
                content = self._add_cursor_frontmatter(content, section)

            # Write the file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            logger.info(f"Successfully saved Casper workflow to {file_path}")

            return {
                "status": "success",
                "file_path": str(file_path.absolute()),
                "tool_context": tool_context,
                "section": section,
                "content_preview": content[:200] + "..." if len(content) > 200 else content,
            }

        except Exception as e:
            error_msg = f"Error saving Casper workflow: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "error": error_msg}

    async def execute(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Execute the tool with the given arguments.

        Args:
            arguments: The arguments to pass to the tool

        Returns:
            A list of TextContent objects with the tool's response
        """
        try:
            section = arguments.get("section", "full")
            mode = arguments.get("mode", "share")
            tool_context = arguments.get("tool_context")
            project_directory = arguments.get("project_directory")

            # Auto-detect tool context if not provided
            if not tool_context:
                tool_context = self._detect_tool_context()

            # Load the Casper workflow content
            full_content = await self._load_casper_workflow()

            if full_content.startswith("Error:"):
                return [TextContent(type="text", text=full_content)]

            # Extract the requested section
            section_content = self._extract_section(full_content, section)

            if mode == "save":
                # Save mode: Save to appropriate directory
                save_result = self._save_casper_workflow(section_content, section, tool_context, project_directory)

                if save_result["status"] == "error":
                    return [TextContent(type="text", text=f"Error: {save_result['error']}")]

                # Format the save response
                formatted_response = {
                    "tool": "get_casper_workflow",
                    "mode": "save",
                    "section": section,
                    "tool_context": tool_context,
                    "file_path": save_result["file_path"],
                    "content_preview": save_result["content_preview"],
                    "status": "success",
                    "usage": (
                        f"Casper workflow saved to {save_result['file_path']}. "
                        "The file is now available as rules/instructions for your AI tool."
                    ),
                    "sections_available": self.SECTIONS,
                }
            else:
                # Share mode: Return content to LLM (original behavior)
                formatted_response = {
                    "tool": "get_casper_workflow",
                    "mode": "share",
                    "section": section,
                    "content": section_content,
                    "usage": (
                        "This content provides the Casper workflow methodology for AI development guidance. "
                        "Use it as rules/instructions for development processes."
                    ),
                    "sections_available": self.SECTIONS,
                }

            return [TextContent(type="text", text=json.dumps(formatted_response, indent=2))]

        except Exception as e:
            error_msg = f"Error executing get_casper_workflow tool: {str(e)}"
            logger.error(error_msg)
            return [TextContent(type="text", text=f"Error: {error_msg}")]
