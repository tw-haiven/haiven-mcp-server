# Haiven MCP Server

Connect your AI tools directly to your organization's Haiven prompts. Use expertly crafted prompts from Claude Desktop, VS Code, Cursor, and other AI tools without switching apps.

## What You Get

✅ **Access your organization's expert prompts** directly in your AI tools  
✅ **Ready-to-use prompts** for user stories, code reviews, architecture decisions, PRDs, and more  
✅ **No app switching** - stay in your current workflow  
✅ **Works with any MCP-compatible tool** - Claude Desktop, VS Code, Cursor, and more  
✅ **Seamless integration** - prompts appear as if they're built into your AI tool  
✅ **Context preservation** - your conversations continue uninterrupted  

## Quick Start

**Prerequisites**: Docker installed on your machine

1. **Get your API key** from your Haiven web interface (API Keys → Generate New API Key)
   
   **🔒 Security note**: Store your API key securely and never commit it to version control

2. **Add this configuration to your AI tool's MCP settings**:
   ```json
   "haiven-prompts": {
     "command": "docker",
     "args": [
       "run", "-i", "--rm",
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

After setup, try these commands in your AI tool:

**See available prompts:**
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
- **API Key Authentication**: Secure connection to your Haiven server
- **No Local Storage**: All queries proxy directly to your Haiven server
- **Multi-Architecture Docker**: Supports AMD64 and ARM64
- **Security Hardened**: Comprehensive security scanning and validation

### Available Tools

`get_prompts`
Retrieves all available prompts with their metadata and follow-ups.

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

`get_prompt_tex`t
Fetches the content of a specific prompt by ID.

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

## License

Licensed under the same terms as the main Haiven project.