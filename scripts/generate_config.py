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


def get_python_path():
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


def main():
    print("🔧 MCP Configuration Generator")
    print("=" * 35)
    print()

    # Check if Python 3.11+ is available, else suggest installation instructions
    if sys.version_info < (3, 11):
        print("❌ Python 3.11 or newer is required")
        print("Please install Python 3.11+ from https://python.org")
        print("or use your system package manager:")
        print("  macOS: brew install python")
        print("  Ubuntu: sudo apt install python3")
        sys.exit(1)
    else:
        print("✅ Python found")

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

    # Get the best Python path to use
    python_path = get_python_path()
    print(f"✅ Using Python: {python_path}")

    # Generate configurations
    print("📋 Generated Configurations:")
    print("=" * 30)

    # 1. Configuration with full path (most reliable)
    config_fullpath = {
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

    print("\n✅ Option 1: Full path (RECOMMENDED - most reliable)")
    print(json.dumps(config_fullpath, indent=2))

    # 2. Configuration with cwd (if supported)
    config_cwd = {
        "mcpServers": {
            "haiven": {
                "command": "python",
                "args": ["mcp_server.py"],
                "cwd": str(project_dir),
                "env": {"HAIVEN_API_URL": haiven_url},
            }
        }
    }

    if use_auth:
        config_cwd["mcpServers"]["haiven"]["env"]["HAIVEN_API_KEY"] = api_key
    else:
        config_cwd["mcpServers"]["haiven"]["env"]["HAIVEN_DISABLE_AUTH"] = "true"

    print("\n✅ Option 2: With cwd (if your AI tool supports it)")
    print(json.dumps(config_cwd, indent=2))

    # 3. Configuration with Poetry
    config_poetry = {
        "mcpServers": {
            "haiven": {
                "command": "poetry",
                "args": ["run", "python", "mcp_server.py"],
                "cwd": str(project_dir),
                "env": {"HAIVEN_API_URL": haiven_url},
            }
        }
    }

    if use_auth:
        config_poetry["mcpServers"]["haiven"]["env"]["HAIVEN_API_KEY"] = api_key
    else:
        config_poetry["mcpServers"]["haiven"]["env"]["HAIVEN_DISABLE_AUTH"] = "true"

    print("\n✅ Option 3: With Poetry (if you prefer)")
    print(json.dumps(config_poetry, indent=2))

    # Write to files
    with open("mcp-config-fullpath.json", "w") as f:
        json.dump(config_fullpath, f, indent=2)

    with open("mcp-config-cwd.json", "w") as f:
        json.dump(config_cwd, f, indent=2)

    with open("mcp-config-poetry.json", "w") as f:
        json.dump(config_poetry, f, indent=2)

    print("\n📁 Configuration files created:")
    print("   - mcp-config-fullpath.json (recommended)")
    print("   - mcp-config-cwd.json")
    print("   - mcp-config-poetry.json")
    print()

    print("📋 How to use:")
    print("1. Copy the content from one of the options above")
    print("2. Paste it into your AI tool's MCP configuration")
    print("3. Restart your AI tool")
    print("4. Test: Ask 'What Haiven prompts are available?'")
    print()

    print("📱 Configuration locations:")
    print("   Claude Desktop: ~/.config/claude/config.json")
    print("   VS Code: Settings → search for 'mcp'")
    print("   Cursor: ~/.cursor/config.json")
    print()

    print("🎯 Start with Option 1 (full path) - it's the most reliable!")


if __name__ == "__main__":
    main()
