# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
"""
Generate working MCP configuration for your system
Fixes common "cwd" path issues
"""

import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any


def get_python_path() -> str:
    """Get the best Python path to use, preferring virtual environment if available"""
    # Check if we're running in a virtual environment
    if hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix):
        # We're in a virtual environment - use the current executable
        return sys.executable

    # Check for .venv in the project directory
    project_dir = Path(__file__).parent.parent
    venv_python = project_dir / ".venv" / "bin" / "python"
    if venv_python.exists():
        return str(venv_python)

    # Check for .venv/Scripts/python.exe on Windows
    venv_python_windows = project_dir / ".venv" / "Scripts" / "python.exe"
    if venv_python_windows.exists():
        return str(venv_python_windows)

    # Fallback to system Python
    python_path = "/opt/homebrew/opt/python@3.11/bin/python3.11"
    which_python311 = shutil.which("python3.11")
    if which_python311:
        python_path = which_python311

    return python_path


def check_docker_available() -> bool:
    """Check if Docker is available on the system"""
    return shutil.which("docker") is not None


def get_tool_config_location(tool_name: str) -> str:
    """Get the configuration file location for the specified AI tool"""
    config_locations = {
        "claude": {
            "macos": "~/Library/Application Support/Claude/claude_desktop_config.json",
            "linux": "~/.config/claude/config.json",
            "windows": "%APPDATA%\\Claude\\claude_desktop_config.json",
        },
        "cursor": {"macos": "~/.cursor/config.json", "linux": "~/.cursor/config.json", "windows": "%APPDATA%\\Cursor\\config.json"},
        "vscode": {
            "macos": "~/Library/Application Support/Code/User/settings.json",
            "linux": "~/.config/Code/User/settings.json",
            "windows": "%APPDATA%\\Code\\User\\settings.json",
        },
        "zed": {
            "macos": "~/Library/Application Support/Zed/User/settings.json",
            "linux": "~/.config/Zed/User/settings.json",
            "windows": "%APPDATA%\\Zed\\User\\settings.json",
        },
    }

    # Detect OS
    if sys.platform == "darwin":
        os_name = "macos"
    elif sys.platform.startswith("linux"):
        os_name = "linux"
    elif sys.platform == "win32":
        os_name = "windows"
    else:
        os_name = "linux"  # Default fallback

    if tool_name in config_locations and os_name in config_locations[tool_name]:
        return config_locations[tool_name][os_name]

    return "Check your tool's documentation for config location"


def main() -> None:
    print("🔧 MCP Configuration Generator")
    print("=" * 35)
    print()

    # Ask which AI tool the user is using
    print("🎯 Which AI tool are you setting up?")
    print("1. Claude Desktop")
    print("2. Cursor")
    print("3. VS Code")
    print("4. Zed")
    print("5. Other MCP-compatible tool")

    tool_choice = input("Enter choice (1-5): ").strip()

    tool_names = {"1": "claude", "2": "cursor", "3": "vscode", "4": "zed", "5": "other"}

    selected_tool = tool_names.get(tool_choice, "other")

    if selected_tool != "other":
        config_location = get_tool_config_location(selected_tool)
        print(f"✅ Config location for {selected_tool.title()}: {config_location}")
    else:
        config_location = "Check your tool's documentation"
        print("✅ You'll need to check your tool's documentation for the config location")

    print()

    # Check if Python 3.11+ is available, else suggest installation instructions
    print("✅ Python found")

    # Check if Docker is available
    docker_available = check_docker_available()
    if docker_available:
        print("✅ Docker found")
    else:
        print("⚠️  Docker not found (will use Python setup only)")
        print("💡 Mac users: Consider installing Colima as a lighter alternative to Docker Desktop")
        print("   Install with: brew install colima && colima start")

    # Get the root folder for the project
    project_dir = Path(__file__).parent.parent
    script_path = project_dir / "mcp_server.py"

    print(f"📁 Project directory: {project_dir}")
    print("📄 Looking for: mcp_server.py")

    # Check if files exist
    if not script_path.exists():
        print("❌ mcp_server.py not found in project root directory")
        print("   Make sure you're running this from the haiven-mcp-server/scripts directory")
        sys.exit(1)

    print("✅ mcp_server.py found")
    print()

    # Ask for configuration type
    print("🎯 What type of setup?")
    print("1. Local development (auth disabled)")
    print("2. Remote server (with API key)")

    choice = input("Enter choice (1 or 2): ").strip()

    if choice == "1":
        # Local development
        haiven_url = "http://localhost:8080"
        use_auth = False
        api_key = None
        print("✅ Local development configuration")
    elif choice == "2":
        # Remote server
        haiven_url = input("Enter Haiven server URL: ").strip()
        if not haiven_url.startswith(("http://", "https://")):
            print("❌ Please enter a complete URL starting with http:// or https://")
            sys.exit(1)

        # take api key from env variable
        if haiven_url.startswith("http://localhost") or haiven_url.startswith("https://0.0.0.0"):
            # does not require api key
            use_auth = False
            api_key = None
            print("✅ Local development configuration")
        else:
            # requires api key
            # take api key from env variable
            print("🔑 Checking for API key in environment variables...")
            api_key = os.getenv("HAIVEN_API_KEY")
            # if api key is not set, ask for it
            if not api_key:
                api_key = input("Enter API key: ").strip()
                if len(api_key) < 10:
                    print("❌ Please enter a valid API key")
                    sys.exit(1)
            use_auth = True
            print("✅ Remote server configuration")
    else:
        print("❌ Invalid choice")
        sys.exit(1)

    print()

    # Generate configurations
    print("📋 Generated Configurations:")
    print("=" * 30)

    # Docker configuration (if available)
    if docker_available:
        config_docker: dict[str, Any] = {
            "mcpServers": {
                "haiven-prompts": {
                    "command": "docker",
                    "args": ["run", "-i", "--rm", "--pull=always", "ghcr.io/tw-haiven/haiven-mcp-server:latest"],
                    "env": {"HAIVEN_API_URL": haiven_url},
                }
            }
        }

        if use_auth:
            config_docker["mcpServers"]["haiven-prompts"]["args"].extend(["-e", f"HAIVEN_API_KEY={api_key}"])
        else:
            config_docker["mcpServers"]["haiven-prompts"]["args"].extend(["-e", "HAIVEN_DISABLE_AUTH=true"])

        print("\n🎯 Option 1: Docker (RECOMMENDED - easiest setup)")
        print(json.dumps(config_docker, indent=2))

        # Write Docker config to file
        with open("mcp-config-docker.json", "w") as f:
            json.dump(config_docker, f, indent=2)

    # Get the best Python path to use
    python_path = get_python_path()
    print(f"✅ Using Python: {python_path}")

    # 1. Configuration with full path (most reliable)
    config_fullpath: dict[str, Any] = {
        "mcpServers": {
            "haiven": {
                "command": python_path,
                "args": [str(script_path)],
                "env": {"HAIVEN_API_URL": haiven_url},
            }
        }
    }

    if use_auth:
        config_fullpath["mcpServers"]["haiven"]["env"]["HAIVEN_API_KEY"] = api_key
    else:
        config_fullpath["mcpServers"]["haiven"]["env"]["HAIVEN_DISABLE_AUTH"] = "true"

    option_number = "2" if docker_available else "1"
    print(f"\n✅ Option {option_number}: Full path (Python - most reliable)")
    print(json.dumps(config_fullpath, indent=2))

    # 2. Configuration with module import
    config_module: dict[str, Any] = {
        "mcpServers": {
            "haiven": {
                "command": python_path,
                "args": ["-m", "src.mcp_server"],
                "cwd": str(project_dir),
                "env": {"HAIVEN_API_URL": haiven_url},
            }
        }
    }

    if use_auth:
        config_module["mcpServers"]["haiven"]["env"]["HAIVEN_API_KEY"] = api_key
    else:
        config_module["mcpServers"]["haiven"]["env"]["HAIVEN_DISABLE_AUTH"] = "true"

    option_number = "3" if docker_available else "2"
    print(f"\n✅ Option {option_number}: Module import (if your tool supports it)")
    print(json.dumps(config_module, indent=2))

    # 3. Configuration with Poetry
    config_poetry: dict[str, Any] = {
        "mcpServers": {
            "haiven": {
                "command": "poetry",
                "args": ["run", "python", str(script_path)],
                "cwd": str(project_dir),
                "env": {"HAIVEN_API_URL": haiven_url},
            }
        }
    }

    if use_auth:
        config_poetry["mcpServers"]["haiven"]["env"]["HAIVEN_API_KEY"] = api_key
    else:
        config_poetry["mcpServers"]["haiven"]["env"]["HAIVEN_DISABLE_AUTH"] = "true"

    option_number = "4" if docker_available else "3"
    print(f"\n✅ Option {option_number}: With Poetry (if you prefer)")
    print(json.dumps(config_poetry, indent=2))

    # Write to files
    with open("mcp-config-fullpath.json", "w") as f:
        json.dump(config_fullpath, f, indent=2)

    with open("mcp-config-module.json", "w") as f:
        json.dump(config_module, f, indent=2)

    with open("mcp-config-poetry.json", "w") as f:
        json.dump(config_poetry, f, indent=2)

    print("\n📁 Configuration files created:")
    if docker_available:
        print("   - mcp-config-docker.json (RECOMMENDED)")
    print("   - mcp-config-fullpath.json")
    print("   - mcp-config-module.json")
    print("   - mcp-config-poetry.json")
    print()

    print("📋 How to use:")
    if docker_available:
        print("🎯 RECOMMENDED: Use Option 1 (Docker) - it's the easiest setup!")
        print("   Just copy the Docker configuration and you're done.")
        print()
    print("1. Copy the content from one of the options above")
    print("2. Paste it into your AI tool's MCP configuration")
    print("3. Restart your AI tool")
    print("4. Test: Ask 'What Haiven prompts are available?'")
    print()

    print(f"📱 Configuration location for {selected_tool.title()}:")
    print(f"   {config_location}")
    print()

    if selected_tool == "claude":
        print("💡 For Claude Desktop, the config file should contain your MCP servers configuration.")
        print("   If the file doesn't exist, create it with the content from one of the options above.")
    elif selected_tool == "vscode":
        print("💡 For VS Code, add the MCP configuration to your settings.json file.")
        print("   You can access this via: Cmd+Shift+P → 'Preferences: Open Settings (JSON)'")
    elif selected_tool == "cursor":
        print("💡 For Cursor, the config file should contain your MCP servers configuration.")
        print("   If the file doesn't exist, create it with the content from one of the options above.")

    if docker_available:
        print("🎯 Start with Option 1 (Docker) - it's the easiest and most reliable!")
    else:
        print("🎯 Start with Option 1 (full path) - it's the most reliable!")


if __name__ == "__main__":
    main()
