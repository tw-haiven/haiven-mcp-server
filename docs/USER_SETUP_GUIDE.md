# 🚀 Haiven MCP Setup Guide for End Users

**For Business Analysts, Product Managers, and other non-technical users**

This guide shows you how to connect **any MCP-compatible AI tool** to your organization's **Haiven AI** system, so you can use Haiven's prompts directly from your favorite AI tools.

## 📋 **What You'll Need**

- **An MCP-compatible AI tool** installed on your computer:
  - Claude Desktop, VS Code (with AI extensions), Cursor, Zed, etc.
- **Access to your organization's Haiven system** (the web version)
- **15-20 minutes** for setup

## 🎯 **What This Gives You**

After setup, you can:
- ✅ Use Haiven prompts directly from your AI tool
- ✅ Execute prompts with your own input
- ✅ Get all Haiven's AI capabilities without switching apps
- ✅ Keep your conversation context while using Haiven tools

---

## 🚀 **Quick Start (Recommended)**

> **💡 Want the easiest setup?** Run our automated installer:
> ```bash
> ./scripts/install.sh
> ```
> This will detect your system, install dependencies, and generate the perfect configuration for your AI tool!

**Or use our configuration generator:**
```bash
python scripts/generate_config.py
```

---

## 📦 **Manual Setup (Alternative)**

## 🔑 **Step 1: Get Your API Key**

1. **Open Haiven in your browser** (the web version your organization uses)
2. **Login** with your work credentials (OKTA/SSO)
3. **Click "API Keys"** in the top navigation menu
4. **Click "Generate New API Key"**
5. **Fill out the form:**
   - Name: "AI Tool Integration"
   - Expiration: 365 days (or your preference)
6. **Copy the generated key** - ⚠️ **Save it immediately!** You won't see it again
7. **Store it safely** (password manager recommended)

---

## 🐳 **Step 2: Choose Your Setup Method**

### **Option A: Docker (Recommended) 🎯**

**Prerequisites:**
- Docker installed on your computer

**Why Docker is recommended:**
- ✅ No Python installation required
- ✅ No dependency management needed
- ✅ Works consistently across all platforms
- ✅ Easy to update and maintain
- ✅ Isolated environment (more secure)

### **Option B: Python Local Setup**

**Prerequisites:**
- Python 3.11+ installed
- Poetry package manager installed

**Use this option if:**
- Your organization doesn't allow Docker
- You prefer to run the server locally
- You need to customize the setup

---

## 🐳 **Option A: Docker Setup (Recommended)**

> **💡 Quick Start**: Run `./scripts/install.sh` for automated setup, then follow the manual steps below if needed.

### **Step A1: Install Docker**

1. **Download Docker Desktop** from [docker.com](https://docker.com)
2. **Install and start Docker Desktop**
3. **Verify installation:** Open terminal and run `docker --version`

**Alternative for Mac users: Colima**
If you prefer a lighter alternative to Docker Desktop, you can use [Colima](https://github.com/abiosoft/colima/blob/main/README.md):

```bash
# Install Colima using Homebrew
brew install colima

# Start Colima
colima start

# Verify installation
docker --version
```

> **Note:** Colima provides a lightweight Docker runtime for macOS. See the [Colima GitHub repository](https://github.com/abiosoft/colima/blob/main/README.md) for detailed installation and usage instructions.

### **Step A2: Configure Your AI Tool**

Choose your AI tool and add the Docker configuration:

#### **Claude Desktop**
1. **Find Claude Desktop's config file:**
   - **Windows:** `%APPDATA%\Claude\config.json`
   - **Mac:** `~/Library/Application Support/Claude/config.json`
   - **Linux:** `~/.config/claude/config.json`

2. **Create the config file if it doesn't exist** (just an empty file named `config.json`)

3. **Edit the config file** and add:

```json
{
  "mcpServers": {
    "haiven-prompts": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "HAIVEN_API_KEY=<VALUE_MENTIONED_BY_YOU>",
        "-e", "HAIVEN_API_URL=https://your-haiven-server.com",
        "ghcr.io/tw-haiven/haiven-mcp-server:latest"
      ]
    }
  }
}
```

#### **VS Code with AI Extensions**
1. **Open VS Code Settings** (Ctrl+, or Cmd+,)
2. **Search for "mcp"** or check your AI extension's configuration
3. **Add MCP server configuration:**

```json
{
  "mcp.servers": {
    "haiven-prompts": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "HAIVEN_API_KEY=<VALUE_MENTIONED_BY_YOU>",
        "-e", "HAIVEN_API_URL=https://your-haiven-server.com",
        "ghcr.io/tw-haiven/haiven-mcp-server:latest"
      ]
    }
  }
}
```

#### **Cursor**
1. **Find Cursor's config file:**
   - **Windows:** `%APPDATA%\Cursor\config.json`
   - **Mac:** `~/Library/Application Support/Cursor/config.json`
   - **Linux:** `~/.config/cursor/config.json`

2. **Add the same Docker configuration as Claude Desktop**

#### **Other AI Tools**
Check your tool's documentation for MCP server configuration. Look for:
- "MCP servers" or "Model Context Protocol"
- "External tools" or "Integrations"
- Settings for adding custom servers

### **Step A3: Customize the Configuration**

**Replace these values in your configuration:**

- `your-api-key-here` → Your actual API key from Step 1
- `https://your-haiven-server.com` → Your organization's Haiven server URL

**Example with real values:**
```json
{
  "mcpServers": {
    "haiven-prompts": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "HAIVEN_API_KEY=<VALUE_MENTIONED_BY_YOU>",
        "-e", "HAIVEN_API_URL=https://haiven.your-company.com",
        "ghcr.io/tw-haiven/haiven-mcp-server:latest"
      ]
    }
  }
}
```

### **Step A4: Test Docker Setup**

1. **Open terminal/command prompt**
2. **Test the Docker command:**
   ```bash
   docker run -i --rm \
     -e HAIVEN_API_KEY="your-api-key" \
     -e HAIVEN_API_URL="https://your-haiven-server.com" \
     ghcr.io/tw-haiven/haiven-mcp-server:latest
   ```
3. **You should see output indicating the server is running**
4. **Press Ctrl+C to stop the test**

---

## 🐍 **Option B: Python Local Setup**

> **💡 Quick Start**: Run `./scripts/install.sh` for automated setup, then follow the manual steps below if needed.

### **Step B1: Install Prerequisites**

#### **Check if Python is installed:**
1. **Press Windows Key + R** (Windows) or **Cmd + Space** (Mac)
2. **Type:** `cmd` (Windows) or `Terminal` (Mac)
3. **Type:** `python3 --version`
4. If you see a version number like `Python 3.11.x`, you're good!

#### **If Python is not installed:**
- **Windows:** Download from [python.org](https://python.org) - choose "Add to PATH" during installation
- **Mac:** Use Homebrew: `brew install python@3.11` or download from [python.org](https://python.org)
- **Linux:** `sudo apt update && sudo apt install python3.11`

#### **Install Poetry:**
```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -
# Or on macOS with Homebrew
brew install poetry
```

### **Step B2: Download and Setup the MCP Server**

1. **Download from Your IT Team (Recommended)**
   Ask your IT team for the "Haiven MCP Server" - they should provide you with a folder containing the setup files.

2. **Or Download from GitHub (If IT allows)**
   - Go to your organization's Haiven repository
   - Download the `haiven-mcp-server` folder
   - Save it somewhere easy to find (like `Downloads/haiven-mcp-server`)

3. **Open Terminal/Command Prompt**

4. **Navigate to your MCP server folder:**
   ```bash
   cd Downloads/haiven-mcp-server  # Adjust path as needed
   ```

5. **Run the installer script:**
   ```bash
   # Mac/Linux
   ./scripts/install.sh

   # Windows
   python scripts/generate_config.py
   ```

6. **Follow the prompts** - the installer will:
   - Configure Poetry for in-project virtual environments
   - Install all dependencies
   - Generate configuration files for your AI tool
   - Ask for your Haiven server URL and API key

### **Step B3: Configure Your AI Tool**

The installer will generate configuration files for you. Use the **Option 1 (Full path)** configuration as it's the most reliable.

#### **Claude Desktop**
1. **Find Claude Desktop's config file:**
   - **Windows:** `%APPDATA%\Claude\config.json`
   - **Mac:** `~/Library/Application Support/Claude/config.json`
   - **Linux:** `~/.config/claude/config.json`

2. **Create the config file if it doesn't exist** (just an empty file named `config.json`)

3. **Edit the config file** and add the configuration from the installer output:

```json
{
  "mcpServers": {
    "haiven": {
      "command": "/full/path/to/your/haiven-mcp-server/.venv/bin/python",
      "args": ["/full/path/to/your/haiven-mcp-server/mcp_server.py"],
      "env": {
        "HAIVEN_API_URL": "https://your-haiven-server.com",
        "HAIVEN_API_KEY": <VALUE_MENTIONED_BY_YOU>
      }
    }
  }
}
```

#### **VS Code with AI Extensions**
1. **Open VS Code Settings** (Ctrl+, or Cmd+,)
2. **Search for "mcp"** or check your AI extension's configuration
3. **Add MCP server configuration:**

```json
{
  "mcp.servers": {
    "haiven": {
      "command": "/full/path/to/your/haiven-mcp-server/.venv/bin/python",
      "args": ["/full/path/to/your/haiven-mcp-server/mcp_server.py"],
      "env": {
        "HAIVEN_API_URL": "https://your-haiven-server.com",
        "HAIVEN_API_KEY": <VALUE_MENTIONED_BY_YOU>
      }
    }
  }
}
```

#### **Cursor**
1. **Find Cursor's config file:**
   - **Windows:** `%APPDATA%\Cursor\config.json`
   - **Mac:** `~/Library/Application Support/Cursor/config.json`
   - **Linux:** `~/.config/cursor/config.json`

2. **Add the same MCP server configuration as Claude Desktop**

#### **Other AI Tools**
Check your tool's documentation for MCP server configuration. Look for:
- "MCP servers" or "Model Context Protocol"
- "External tools" or "Integrations"
- Settings for adding custom servers

### 💡 **Example Configuration:**
```json
{
  "mcpServers": {
    "haiven": {
      "command": "/Users/YourName/Downloads/haiven-mcp-server/.venv/bin/python",
      "args": ["/Users/YourName/Downloads/haiven-mcp-server/mcp_server.py"],
      "env": {
        "HAIVEN_API_URL": "https://haiven.your-company.com",
        "HAIVEN_API_KEY": <VALUE_MENTIONED_BY_YOU>
      }
    }
  }
}
```

> **Note:** The installer generates the correct paths automatically. Use the **Option 1 (Full path)** configuration from the installer output for the most reliable setup.

---

## 🚀 **Step 3: Start Your AI Tool**

1. **Close your AI tool** completely (if it was open)
2. **Restart your AI tool**
3. **Look for the MCP connection indicator** - you should see "haiven" or "haiven-prompts" connected

---

## ✅ **Step 4: Test It Out**

In your AI tool, try asking:

> "What Haiven prompts are available?"

or

> "Execute a Haiven prompt to help me analyze user feedback"

You should see your AI tool accessing your Haiven system and showing available prompts!

---

## 🆘 **Troubleshooting**

### **Docker Issues**

#### "Docker not found"
- ✅ Install Docker Desktop from [docker.com](https://docker.com)
- ✅ Make sure Docker Desktop is running
- ✅ Restart your computer after Docker installation

#### "Permission denied" (Linux)
- ✅ Add your user to the docker group: `sudo usermod -aG docker $USER`
- ✅ Log out and log back in
- ✅ Or run with sudo (not recommended for production)

#### "Connection refused"
- ✅ Make sure Docker Desktop is running
- ✅ Check that your API key and URL are correct
- ✅ Try the test command in Step A4

### **Python Issues**

#### "MCP server not connecting"
- ✅ Check that Python 3.11+ is installed: `python3 --version`
- ✅ Check that Poetry is installed: `poetry --version`
- ✅ Check that the file path in config.json is correct
- ✅ Check that your API key is valid (test in Haiven web interface)

#### "Authentication failed"
- ✅ Generate a new API key from Haiven web interface
- ✅ Make sure the API key is correctly copied (no extra spaces)
- ✅ Confirm your Haiven URL is correct

#### "Command not found"
- ✅ Make sure you installed Poetry: `curl -sSL https://install.python-poetry.org | python3 -`
- ✅ Try using full path to Python in the config
- ✅ Check that you ran the installer script in the correct folder

#### "Python not found"
- ✅ Install Python 3.11+ from [python.org](https://python.org)
- ✅ On macOS, try: `brew install python@3.11`
- ✅ Make sure "Add to PATH" was checked during installation
- ✅ Restart your computer after Python installation

---

## 📞 **Getting Help**

If you're stuck:

1. **Ask your IT team** - they can help with the technical setup
2. **Check with your Haiven administrator** - they can verify your API key
3. **Check your AI tool's documentation** - for MCP server setup specifics
4. **Share this guide** with your IT team - they'll know what to do

---

## 🔄 **Maintenance**

### **Docker Setup**
- **Updates:** Docker will automatically pull the latest image when you restart your AI tool
- **API Key Renewal:** Generate a new key and update your AI tool's config

### **Python Setup**
- **API Key Renewal:** Generate a new key and update your AI tool's config
- **Updates:** Your IT team will let you know when there are updates

---

## 🎉 **You're All Set!**

Now you can use Haiven's powerful AI prompts directly from your favorite AI tool!

**Pro Tips:**
- Start with asking "What prompts are available?" to explore
- Use specific prompts for your domain (product analysis, user research, etc.)
- The integration remembers your conversation context
- You can still use your AI tool's regular features alongside Haiven

**Happy AI-powered work! 🚀**
