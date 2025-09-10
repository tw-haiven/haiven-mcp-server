# Haiven MCP Server

Connect your AI tools directly to your organization's Haiven prompts. Use expertly crafted prompts from Claude Desktop, VS Code, Cursor, and other AI tools without switching apps.

## What You Get

- ✅ **Access your organization's expert prompts** directly in your AI tools
- ✅ **Ready-to-use prompts** for user stories, code reviews, architecture decisions, PRDs, and more
- ✅ **No app switching** - stay in your current workflow
- ✅ **Works with any MCP-compatible tool** - Claude Desktop, VS Code, Cursor, and more
- ✅ **Seamless integration** - prompts appear as if they're built into your AI tool
- ✅ **Context preservation** - your conversations continue uninterrupted
- ✅ **Native MCP prompts** - each Haiven prompt appears as a first-class MCP prompt
- ✅ **Smart caching** - faster performance with intelligent content caching
- ✅ **Backward compatibility** - existing tools still work alongside new prompt interface

## Quick Start

**Prerequisites**: Docker installed on your machine

1. **Get your API key** from your Haiven web interface (API Keys → Generate New API Key)

   **🔒 Security note**: Store your API key securely and never commit it to version control

   **For detailed steps:** See [Get Your API Key](#get-your-api-key) section below

2. **Add this configuration to your AI tool's MCP settings**:
   ```json
   "haiven-prompts": {
     "command": "docker",
     "args": [
       "run", "-i", "--rm", "--pull=always",
       "-e", "HAIVEN_API_KEY=your-api-key-here",
       "-e", "HAIVEN_API_URL=https://your-haiven-server.com",
       "ghcr.io/tw-haiven/haiven-mcp-server:latest"
     ]
   }
   ```

   **Where to add it:**
   - **Claude Desktop**: `~/Library/Application Support/Claude/config.json` (Mac) or `%APPDATA%\Claude\config.json` (Windows)
   - **VS Code**: Settings → Extensions → search "mcp" → Configure MCP servers
   - **Cursor**: `~/Library/Application Support/Cursor/config.json` (Mac) or `%APPDATA%\Cursor\config.json` (Windows)

3. **Replace the values**:
   - `your-api-key-here` → Your API key from step 1
   - `https://your-haiven-server.com` → Your organization's Haiven server URL

4. **Restart your AI tool**

## Test Your Setup

After completing the setup, verify everything works:

1. **Check MCP connection**: In your AI tool, look for "haiven-prompts" in the connected servers list
2. **Test prompt access**: Ask your AI tool: `"What Haiven prompts are available?"`
3. **Verify response**: You should see a list of prompts from your organization's Haiven system

**✅ Success indicators:**
- Your AI tool shows "haiven-prompts" as connected
- You can see your organization's prompts listed
- No authentication errors in the AI tool's logs

## Basic Usage

After setup, you can access your Haiven prompts in two ways:

### **Native MCP Prompts (Recommended)**
Each Haiven prompt appears as a first-class MCP prompt in your AI tool:

**Direct prompt invocation:**
> "Use the ADR prompt to help me document this architecture decision"

**Browse available prompts:**
> "Show me all available Haiven prompts"

**Use prompts with context:**
> "Use the user story prompt to break down this feature request"

### **Legacy Tools (Backward Compatibility)**
For clients that need the tool-based interface:

**List all prompts:**
> "What Haiven prompts are available?"

**Use a specific prompt:**
> "Use the Haiven prompt for creating user stories and help me break down this feature request"

**Execute prompts with context:**
> "Execute the Haiven code review prompt on my current file"

## Common Issues

**🔧 Quick fixes for the most common problems:**

- **"Docker not found"**: Install Docker Desktop from [docker.com](https://docker.com) and ensure it's running
- **"Authentication failed"**: Double-check your API key and Haiven server URL are correct
- **"MCP server not connecting"**: Restart your AI tool and verify the configuration file syntax

**For more help:** See [Complete Troubleshooting Guide](docs/TROUBLESHOOTING.md)

## Get Your API Key

1. **Open Haiven in your browser** (the web version your organization uses)
2. **Login** with your work credentials (OKTA/SSO)
3. **Click "API Keys"** in the top navigation menu
4. **Click "Generate New API Key"**
5. **Fill out the form:**
   - Name: "AI Tool Integration"
   - Expiration: 30 days (or your preference)
6. **Copy the generated key** - **Save it immediately!** You won't see it again
7. **Store it safely** (password manager recommended)

![API Keys Generation](./docs/api-keys.gif)

## Detailed Documentation

- **[Complete Setup Guide](docs/USER_SETUP_GUIDE.md)** - Step-by-step instructions for all AI tools
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)** - Local development and contributing

---

## Technical Details & IT Information

### Architecture

This MCP server provides a bridge between AI applications and the Haiven AI prompts API using the Model Context Protocol.

**Key Features:**
- **Standard MCP Protocol**: JSON-RPC 2.0 over stdin/stdout
- **Native MCP Prompts**: Each Haiven prompt appears as a first-class MCP prompt
- **Smart Caching**: Two-tier caching (metadata + content) for optimal performance
- **API Key Authentication**: Secure connection to your Haiven server
- **Backward Compatibility**: Legacy tools still work alongside new prompt interface
- **Multi-Architecture Docker**: Supports AMD64 and ARM64
- **Security Hardened**: Comprehensive security scanning and validation

### Available Interfaces

#### **Native MCP Prompts (Primary Interface)**
Each Haiven prompt is registered as a native MCP prompt with:
- **Direct invocation** by prompt identifier (e.g., `/adr-9e6a21eb`)
- **Rich metadata** including title, description, and categories
- **Smart caching** for optimal performance
- **Seamless integration** with MCP-compatible AI tools

#### **MCP Tools**

`get_prompts`
Retrieves all available prompts with their metadata from the cached prompt service.

**Parameters**: None

**Returns**: JSON object with prompts array and total count

**Example Response**:
```json
{
  "prompts": [
    {
      "identifier": "adr-9e6a21eb",
      "title": "Architecture Decision Record",
      "categories": ["architecture"],
      "help_prompt_description": "Create structured ADRs",
      "help_user_input": "Describe the decision context",
      "help_sample_input": "We need to choose a database for our new service",
      "type": "chat"
    }
  ],
  "total_count": 1
}
```

`get_prompt_text`
Fetches the content of a specific prompt by ID with full metadata.

**Parameters**:
- `prompt_id` (required): ID of the prompt to fetch

**Returns**: JSON object containing the prompt content

**Example Response**:
```json
{
  "prompt_id": "prd-template-ideate",
  "title": "Draft PRD",
  "content": "You are a product manager. Help create a comprehensive Product Requirements Document...",
  "type": "chat",
  "follow_ups": ["What metrics should we track?", "How do we prioritize features?"]
}
```

`get_casper_workflow`
Provides the Casper workflow methodology for AI development guidance, supporting both sharing with LLMs and saving to tool-specific directories.

**Parameters:**
- `section` (optional): "explore", "craft", "polish", or "full" (default)
- `mode` (optional): "share" (default) or "save"
- `tool_context` (optional, save mode): "cursor", "vscode", or "generic" (auto-detected)

**Modes:**
- **Share:** Returns Casper workflow content for immediate use by the LLM.
- **Save:** Writes Casper workflow to the appropriate directory for your AI tool (e.g., `.cursor/rules/`, `.github/instructions/`, or project root).

**Example (Share):**
```json
{
  "tool": "get_casper_workflow",
  "mode": "share",
  "section": "explore",
  "content": "# 🔍 Casper's Collaborative Exploration Phase...",
  "sections_available": ["explore", "craft", "polish", "full"]
}
```

**Example (Save):**
```json
{
  "tool": "get_casper_workflow",
  "mode": "save",
  "section": "explore",
  "tool_context": "cursor",
  "file_path": "/path/to/project/.cursor/rules/casper-explore.mdc",
  "status": "success"
}
```

**Integration:**
Casper workflow files are auto-saved in the correct format and location for Cursor, VS Code, or generic tools. Tool context is detected automatically.

**Phases:**
- Explore: Analysis & planning
- Craft: TDD implementation
- Polish: Quality refinement

### For IT Teams

This MCP server:
- Uses standard MCP protocol (JSON-RPC 2.0 over stdin/stdout)
- Supports API key authentication
- No data stored locally - all queries go to your Haiven server
- Works with **any MCP-compatible AI tool**
- **Multi-architecture Docker support** (AMD64 and ARM64)

#### Deployment Options
- **Docker**: Container available for enterprise deployment (recommended)
- **Individual install**: Users run Docker commands on their machines
- **Centralized**: Deploy via software distribution systems

### Setup Resources

- **[VS Code MCP Servers](https://code.visualstudio.com/docs/copilot/chat/mcp-servers)** - Comprehensive VS Code guide
- **[Claude Code MCP](https://docs.anthropic.com/en/docs/claude-code/mcp)** - Official Claude documentation
- **[Cursor MCP Setup](https://docs.cursor.com/en/context/mcp#using-mcp-json)** - Cursor-specific instructions
- **[MCP Protocol Overview](https://modelcontextprotocol.io/quickstart/user#understanding-mcp-servers)** - General MCP concepts

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

**Pre-commit hooks**: Install with `pip install pre-commit && pre-commit install`

**Testing**: Run tests with `poetry run pytest tests/ -v`

## Privacy

The MCP server implementation does not collect, process, or transmit any client-specific data, user inputs, conversation history, or session information. It operates purely as a content delivery mechanism for accessing the Haiven prompt library. Unlike the Haiven web interface, **prompts execute through your AI tool's configured LLM** (not your enterprise's controlled deployment). Ensure your AI tool usage complies with organizational policies.

## License

Licensed under the same terms as the main Haiven project.
