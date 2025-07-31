# 🚀 Haiven MCP Server

**Seamlessly connect any MCP-compatible AI tool to your organization’s Haiven servers and access expertly crafted prompts directly within your tools.**

## 📋 **Prerequisites**

| Mode | Prerequisites | Use Case | Setup |
|------|--------------|----------|-------|
| **🐳 Docker (Recommended)** | Docker | End users, production | `docker run` |
| **🐍 Python Local** | Python 3.11+, Poetry | Developers | `poetry install` |
| **🏢 Enterprise** | Docker, Kubernetes | IT teams | Container orchestration |

**Available Docker Images:**
- `ghcr.io/tw-haiven/haiven-mcp-server:latest` - Latest stable release
- `ghcr.io/tw-haiven/haiven-mcp-server:main-<sha>` - Specific commit builds
- `ghcr.io/tw-haiven/haiven-mcp-server:v1.0.0` - Versioned releases (when available)

**Test the Docker image:**
```bash
./scripts/test_docker_image.sh [your-api-key] [your-api-url]
```

> **Note**: Images are built with multi-architecture support (AMD64 + ARM64) using Docker Buildx for optimal compatibility across different platforms.

## 🚀 **Quick Start**

> **💡 Automated Setup (Recommended)**:
> ```bash
> ./scripts/install.sh
> ```
> This detects your system and generates the perfect configuration automatically!

**For detailed setup instructions, see:**
- **End Users**: [USER_SETUP_GUIDE.md](docs/USER_SETUP_GUIDE.md)
- **Developers**: [DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

## 🔑 **Getting Your API Key**

1. Open Haiven in your browser
2. Login with your work credentials
3. Click "API Keys" in the navigation
4. Click "Generate New API Key"
5. Copy the key immediately

![a.gif](./docs/api-keys.gif)

## 🎯 **Compatible AI Tools**

- **Claude Desktop** - Anthropic's desktop app
- **VS Code** - With AI extensions (Claude, Codeium, etc.)
- **Cursor** - AI-powered code editor
- **Any MCP-compatible tool** - Following the Model Context Protocol standard

## 🎉 **What Users Get**

After setup, users can:
- 💬 Ask their AI tool: "What Haiven prompts are available?"
- 🚀 Execute haiven prompts implicitly : "Using Haiven prompt create user story splitup for the jira ticket JIRA-1234"

## 🔧 **For IT Teams**

This MCP server:
- ✅ Uses standard MCP protocol (JSON-RPC 2.0 over stdin/stdout)
- ✅ Supports API key authentication
- ✅ No data stored locally - all queries go to your Haiven server
- ✅ Works with **any MCP-compatible AI tool**
- ✅ **Multi-architecture Docker support** (AMD64 and ARM64)

### **Deployment Options**
- **Docker**: Container available for enterprise deployment (recommended)
- **Individual install**: Users run Docker commands on their machines
- **Centralized**: Deploy via software distribution systems

## 🆘 **Need Help?**

- **End Users**: See [USER_SETUP_GUIDE.md](USER_SETUP_GUIDE.md) for detailed setup instructions
- **Developers**: See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for local development setup
- **IT Teams**: See [DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) for deployment details
- **Troubleshooting**: Check the appropriate guide for common issues
- **Can't find your API key?** Ask your Haiven administrator

---

**Ready to connect your team to Haiven AI? Works with any MCP-compatible tool! 🚀**

## Overview

This MCP server provides a bridge between AI applications (IDEs, editors, AI assistants) and the Haiven AI prompts API. It enables seamless integration with tools like Claude Desktop, VS Code with MCP extensions, and other AI-powered development environments.

## Features

- **Standalone Service**: Independent from the main Haiven application
- **Standard MCP Protocol**: Uses JSON-RPC 2.0 over stdin/stdout
- **Two Main Tools**:
  - `get_prompts`: Retrieve all available prompts with metadata
  - `get_prompt_text`: Get the specific prompt content by ID
- **Comprehensive Error Handling**: Robust error handling and logging
- **Easy Configuration**: Simple setup and deployment
- **Docker Support**: Multi-architecture container deployment
- **Security Hardened**: Comprehensive security scanning and validation

## API Tools

### get_prompts

Retrieves all available prompts with their metadata and follow-ups.

**Parameters**: None

**Returns**: JSON object with prompts array and total count

**Example**:
```json
{
  "prompts": [
    {
      "identifier": "adr-9e6a21eb",
      "title": "Architecture Decision Record",
      "categories": [
        "architecture"
      ],
      "help_prompt_description": "..",
      "help_user_input": "..",
      "help_sample_input": "..",
      "type": "chat"
    }
  ],
  "total_count": 1
}
```

### get_prompt_text

fetches the content of a specific prompt

**Parameters**:
- `promptid` (required): ID of the prompt to fetch

**Returns**: json object containing the prompt content

**Example**:
```json
{
  "prompt_id": "prd-template-ideate",
  "title": "Draft PRD",
  "content": "...",
  "type": "chat",
  "follow_ups": []
}
```

## License

This project is licensed under the same terms as the main Haiven project.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Pre-commit Hooks

This repository uses [pre-commit](https://pre-commit.com/) to enforce code quality and security checks.

**All contributors must:**
1. Install pre-commit: `pip install pre-commit`
2. Run `pre-commit install` after cloning the repo (this sets up the git hooks).
3. Ensure all pre-commit hooks pass before pushing code: `pre-commit run --all-files`

Pre-commit will automatically run on every commit. If any hook fails, the commit will be blocked until you fix the issues.
