# Haiven MCP Setup Guide for End Users

**For Business Analysts, Product Managers, and other non-technical users**

This guide shows you how to connect **any MCP-compatible AI tool** to your organization's **Haiven AI** system.

## **What You'll Need**

- **An MCP-compatible AI tool** installed on your computer
- **Access to your organization's Haiven system** (the web version)
- **15-20 minutes** for setup

## **What This Gives You**

After setup, you can:
- Use Haiven prompts directly from your AI tool
- Execute prompts with your own input
- Get all Haiven's AI capabilities without switching apps
- Keep your conversation context while using Haiven tools

---

## **Quick Start (Recommended)**

> **Want the easiest setup?** Copy the configuration from the [README.md](../README.md) and add it to your AI tool's MCP settings.

**For automated setup:**
```bash
# Clone and setup
git clone https://github.com/tw-haiven/haiven-mcp-server
cd haiven-mcp-server
sh ./scripts/install.sh
```

---

## **Manual Setup**

## **Step 1: Get Your API Key**

1. **Open Haiven in your browser** (the web version your organization uses)
2. **Login** with your work credentials (OKTA/SSO)
3. **Click "API Keys"** in the top navigation menu
4. **Click "Generate New API Key"**
5. **Fill out the form:**
   - Name: "AI Tool Integration"
   - Expiration: 30 days (or your preference)
6. **Copy the generated key** - **Save it immediately!** You won't see it again
7. **Store it safely** (password manager recommended)

---

## **Step 2: Choose Your Setup Method**

### **Option A: Docker (Recommended)**

**Prerequisites:**
- Docker installed on your computer

**Why Docker is recommended:**
- No Python installation required
- No dependency management needed
- Works consistently across all platforms
- Easy to update and maintain
- Isolated environment (more secure)

### **Option B: Python Local Setup**

**Prerequisites:**
- Python 3.11+ installed

**Use this option if:**
- Your organization doesn't allow Docker
- You prefer to run the server locally
- You need to customize the setup

---

## **Docker Setup (Recommended)**

### **Install Docker**
1. **Download Docker Desktop** from [docker.com](https://docker.com)
2. **Install and start Docker Desktop**
3. **Verify installation:** Open terminal and run `docker --version`

**Alternative for Mac users: Colima**
```bash
brew install colima
brew install docker
colima start
```

### **Configure Your AI Tool**
Add the MCP server configuration from the [README.md](../README.md) to your AI tool's MCP settings.

### **Test Docker Setup**
```bash
docker run -i --rm \
  -e HAIVEN_API_KEY="your-api-key" \
  -e HAIVEN_API_URL="https://your-haiven-server.com" \
  ghcr.io/tw-haiven/haiven-mcp-server:latest
```

---

## **Python Local Setup**

### **Install Python**
- **Windows:** Download from [python.org](https://python.org)
- **Mac:** `brew install python@3.11`
- **Linux:** `sudo apt update && sudo apt install python3.11`

### **Setup MCP Server**
```bash
# Clone and setup
git clone https://github.com/tw-haiven/haiven-mcp-server
cd haiven-mcp-server
sh ./scripts/install.sh
```

### **Configure Your AI Tool**
The installer will generate configuration files. Add the generated configuration to your AI tool's MCP settings.

---

## **Test Your Setup**

1. **Restart your AI tool**
2. **Ask:** "What Haiven prompts are available?"
3. **You should see prompts from your Haiven system**

---

## **Need Help?**

- **Troubleshooting**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **IT Support**: Ask your IT team for help with technical setup
- **Haiven Admin**: Contact your Haiven administrator for API key issues

**MCP Setup Resources:**
- **[VS Code MCP Servers](https://code.visualstudio.com/docs/copilot/chat/mcp-servers)** - Comprehensive guide for VS Code
- **[Claude Code MCP](https://docs.anthropic.com/en/docs/claude-code/mcp)** - Official Claude documentation
- **[Cursor MCP Setup](https://docs.cursor.com/en/context/mcp#using-mcp-json)** - Cursor-specific instructions
- **[MCP Protocol Overview](https://modelcontextprotocol.io/quickstart/user#understanding-mcp-servers)** - General MCP concepts
