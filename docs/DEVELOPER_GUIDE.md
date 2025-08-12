# Developer Guide: Local Haiven MCP Setup

**For developers testing against local Haiven instances**

This guide shows how to quickly set up the MCP server for local development with authentication disabled.

## **Quick Start (5 minutes)**

### **1. Start Local Haiven Backend**
Start your local Haiven backend. It should be running at `http://localhost:8080`

### **2. Setup MCP Server**
```bash
# Clone and setup
git clone https://github.com/tw-haiven/haiven-mcp-server
cd haiven-mcp-server
sh ./scripts/install.sh
```

### **3. Configure for Local Development**
Create a `.env` file:
```bash
HAIVEN_API_URL=http://localhost:8080
HAIVEN_DISABLE_AUTH=true
```

### **4. Test the MCP Server**
```bash
python -m src.mcp_server --help
```

### **5. Configure Your AI Tool**
Add this MCP server to your AI tool's configuration:
```json
"haiven-dev": {
  "command": "/full/path/to/your/haiven-mcp-server/.venv/bin/python",
  "args": ["/full/path/to/your/haiven-mcp-server/mcp_server.py"],
  "env": {
    "HAIVEN_API_URL": "http://localhost:8080",
    "HAIVEN_DISABLE_AUTH": "true"
  }
}
```

### **6. Test in Your AI Tool**
Restart your AI tool and ask: "What Haiven prompts are available?"

---

## **Development Workflow**

### **Starting Development Session**
```bash
# Terminal 1: Start Haiven backend
cd haiven && poetry run app

# Terminal 2: Test MCP server
cd haiven-mcp-server && python mcp_server.py --help
```

### **Quick Testing**
```bash
# Direct test of MCP server
cd haiven-mcp-server
export HAIVEN_API_URL="http://localhost:8080"
export HAIVEN_DISABLE_AUTH="true"
python -m src.mcp_server
```

### **Testing Different Scenarios**
```bash
# Test with authentication enabled
export HAIVEN_API_URL="http://localhost:8080"
export HAIVEN_API_KEY="your-dev-api-key"
unset HAIVEN_DISABLE_AUTH

# Test against remote instance
export HAIVEN_API_URL="https://your-remote-haiven.com"
export HAIVEN_API_KEY="your-remote-api-key"
```

---

## **Testing & Debugging**

### **Enable Debug Logging**
```bash
export PYTHONPATH=.
export HAIVEN_API_URL="http://localhost:8080"
export HAIVEN_DISABLE_AUTH="true"
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from mcp_server import HaivenMCPServer
print('Debug logging enabled')
"
```

### **Test API Connectivity**
```bash
curl http://localhost:8080/api/prompts
```

---

## **Common Issues & Solutions**

### **"Connection refused" errors**
```bash
# Check if Haiven backend is running
curl http://localhost:8080/health
```

### **"No prompts found"**
```bash
# Check if prompts are loaded
curl http://localhost:8080/api/prompts | jq '.[0].id'
```

### **MCP server not connecting**
```bash
# Test basic import
python -c "from mcp_server import HaivenMCPServer; print('OK')"
```

---

## **Development Tips**

### **Multiple Environment Setup**
Create different config files:
```bash
# dev.env
HAIVEN_API_URL=http://localhost:8080
HAIVEN_DISABLE_AUTH=true

# staging.env
HAIVEN_API_URL=https://staging.haiven.com
HAIVEN_API_KEY=staging-api-key
```

Load with:
```bash
source dev.env && python mcp_server.py
```

### **Alternative Entry Point**
You can also run from the project root:
```bash
python mcp_server.py
```

---

## **Development Checklist**

- Local Haiven backend running
- MCP server dependencies installed (`sh ./scripts/install.sh`)
- Environment variables set
- AI tool configured with local MCP server
- Basic connectivity tested
- MCP server responds to prompts query

**Happy local development!**

**MCP Setup Resources:**
- **[VS Code MCP Servers](https://code.visualstudio.com/docs/copilot/chat/mcp-servers)** - Comprehensive guide for VS Code
- **[Claude Code MCP](https://docs.anthropic.com/en/docs/claude-code/mcp)** - Official Claude documentation
- **[Cursor MCP Setup](https://docs.cursor.com/en/context/mcp#using-mcp-json)** - Cursor-specific instructions
- **[MCP Protocol Overview](https://modelcontextprotocol.io/quickstart/user#understanding-mcp-servers)** - General MCP concepts
