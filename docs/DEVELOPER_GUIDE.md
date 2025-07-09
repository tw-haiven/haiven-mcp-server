# 🛠️ Developer Guide: Local Haiven MCP Setup

**For developers testing against local Haiven instances**

This guide shows how to quickly set up the MCP server for local development with authentication disabled.

💡 **Super Quick Setup**: Run `./dev_setup.sh` (Mac/Linux) or `python dev_setup.py` (All platforms) to automate most of this process!

## 🚀 **Quick Start (5 minutes)**

### **1. Start Local Haiven Backend**
Go to your local haiven directory start the haiven locally
Your local Haiven should be running at `http://localhost:8080`

### **2. Setup MCP Server for Local Development**
Go to haiven-mcp-server
```bash
# In the haiven-mcp-server directory
poetry config virtualenvs.in-project true
poetry install
```

### **3. Configure for Local Development**
Create a `.env` file in the `haiven-mcp-server` directory:
```bash
# .env file for local development
HAIVEN_API_URL=http://localhost:8080
HAIVEN_DISABLE_AUTH=true
```

### **4. Test the MCP Server**
```bash
# Test basic functionality
poetry run python -m src.mcp_server --help
```

### **5. Configure Your AI Tool**
**Claude Desktop example** (`~/.config/claude/config.json`):
```json
{
  "mcpServers": {
    "haiven-dev": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/haiven-mcp-server",
      "env": {
        "HAIVEN_API_URL": "http://localhost:8080",
        "HAIVEN_DISABLE_AUTH": "true"
      }
    }
  }
}
```

**VS Code example** (settings.json):
```json
{
  "mcp.servers": {
    "haiven-dev": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/haiven-mcp-server",
      "env": {
        "HAIVEN_API_URL": "http://localhost:8080",
        "HAIVEN_DISABLE_AUTH": "true"
      }
    }
  }
}
```

### **6. Test in Your AI Tool**
Restart your AI tool and ask:
> "What Haiven prompts are available?"

You should see prompts from your local Haiven instance!

---

## 🔧 **Development Workflow**

### **Starting Development Session**
```bash
# Terminal 1: Start Haiven backend
cd haiven && poetry run app
# Terminal 2: Test MCP server (optional)
cd haiven-mcp-server && poetry run python mcp_server.py --help
```

### **Quick Testing Without AI Tool**
```bash
# Direct test of MCP server
cd haiven-mcp-server
export HAIVEN_API_URL="http://localhost:8080"
export HAIVEN_DISABLE_AUTH="true"
poetry run python -m src.mcp_server
```

### **Testing Different Scenarios**
```bash
# Test with authentication enabled (requires API key)
export HAIVEN_API_URL="http://localhost:8080"
export HAIVEN_API_KEY="your-dev-api-key"
unset HAIVEN_DISABLE_AUTH

# Test against remote instance
export HAIVEN_API_URL="https://your-remote-haiven.com"
export HAIVEN_API_KEY="your-remote-api-key"
```

---

## 🧪 **Testing & Debugging**

### **Enable Debug Logging**
```bash
export PYTHONPATH=.
export HAIVEN_API_URL="http://localhost:8080"
export HAIVEN_DISABLE_AUTH="true"
poetry run python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from mcp_server import HaivenMCPServer
print('Debug logging enabled')
"
```

### **Test API Connectivity**
```bash
# Quick connectivity test
curl http://localhost:8080/api/prompts
```

### **Test Authentication (when enabled)**
```bash
# Test API key authentication
curl -H "Authorization: Bearer \$HAIVEN_API_KEY" http://localhost:8080/api/prompts
```

---

## 🚨 **Common Issues & Solutions**

### **"Connection refused" errors**
```bash
# Check if Haiven backend is running
curl http://localhost:8080/health

# Check logs
cd app && tail -f logs/haiven.log
```

### **"No prompts found"**
```bash
# Check if prompts are loaded in your local instance
curl http://localhost:8080/api/prompts | jq '.[0].id'
```

### **MCP server not connecting**
```bash
# Test basic import
poetry run python -c "from mcp_server import HaivenMCPServer; print('OK')"

# Test with environment variables
env HAIVEN_API_URL=http://localhost:8080 HAIVEN_DISABLE_AUTH=true poetry run python mcp_server.py
```

---

## 🎯 **Development Tips**

### **Multiple Environment Setup**
Create different config files for different environments:

```bash
# dev.env
HAIVEN_API_URL=http://localhost:8080
HAIVEN_DISABLE_AUTH=true

# staging.env  
HAIVEN_API_URL=https://staging.haiven.com
HAIVEN_API_KEY=staging-api-key

# prod.env
HAIVEN_API_URL=https://prod.haiven.com
HAIVEN_API_KEY=prod-api-key
```

Load with:
```bash
# Load environment
source dev.env && poetry run python mcp_server.py
```

### **Rapid Iteration**
```bash
# Watch for changes and restart (if using watchdog)
poetry run watchmedo auto-restart --pattern="*.py" poetry run python mcp_server.py
```

### **Integration Testing**
```bash
# Test against real deployment
export HAIVEN_API_URL="https://haiven.your-company.com"
export HAIVEN_API_KEY="your-real-api-key"
poetry run python test_integration.py
```

---

## 🔄 **Switching Between Configurations**

### **Quick Config Switch**
```bash
# Local development
export HAIVEN_API_URL="http://localhost:8080" && export HAIVEN_DISABLE_AUTH="true"

# Remote testing  
export HAIVEN_API_URL="https://your-remote.com" && export HAIVEN_API_KEY="your-key" && unset HAIVEN_DISABLE_AUTH
```

### **AI Tool Config for Development**
You can have multiple MCP servers configured:
```json
{
  "mcpServers": {
    "haiven-local": {
      "command": "python",
      "args": ["-m", "src.mcp_server"],
      "cwd": "/path/to/haiven-mcp-server",
      "env": {
        "HAIVEN_API_URL": "http://localhost:8080",
        "HAIVEN_DISABLE_AUTH": "true"
      }
    },
    "haiven-staging": {
      "command": "python", 
      "args": ["-m", "src.mcp_server"],
      "cwd": "/path/to/haiven-mcp-server",
      "env": {
        "HAIVEN_API_URL": "https://staging.haiven.com",
        "HAIVEN_API_KEY": "staging-key"
      }
    }
  }
}
```

---

## 🏁 Alternative Entry Point: Root-Level mcp_server.py

You can now also run the MCP server from the project root with:

```bash
python mcp_server.py
# or
poetry run python mcp_server.py
```

This is useful for AI tools or scripts that do not support the 'cwd' setting or the '-m' module syntax. The thin wrapper script at the root will launch the main server logic from 'src/mcp_server.py'.

> **Note:** Both 'python mcp_server.py' (root) and 'python -m src.mcp_server' (module) are supported and will work identically.

## 📋 **Development Checklist**

- [ ] ✅ Local Haiven backend running (`python dev.py`)
- [ ] ✅ MCP server dependencies installed (`poetry install`)
- [ ] ✅ Environment variables set (`HAIVEN_API_URL`, `HAIVEN_DISABLE_AUTH`)
- [ ] ✅ AI tool configured with local MCP server
- [ ] ✅ Basic connectivity tested (`curl http://localhost:8080/api/prompts`)
- [ ] ✅ MCP server responds to prompts query
- [ ] ✅ Can execute prompts through AI tool

**Happy local development! 🚀** 

> **Note:** The preferred way to run the MCP server is with `python -m src.mcp_server` (or `poetry run python -m src.mcp_server`). This ensures Python uses the correct module path and works reliably with the current project structure. 