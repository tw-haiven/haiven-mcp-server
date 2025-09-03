# MCP Server Troubleshooting Guide

> **Before troubleshooting**: Try our automated setup first:
> ```bash
> sh ./scripts/install.sh
> ```
> This often resolves common issues automatically!

## **Common Issues & Solutions**

### **Docker Issues**

#### **"Docker not found"**
**Problem**: AI tool shows "docker: command not found" or similar errors

**Solutions**:
- Install Docker Desktop from [docker.com](https://docker.com)
- Make sure Docker Desktop is running
- Restart your computer after Docker installation
- On Linux: `sudo apt install docker.io` or equivalent
- **Mac alternative**: Install Colima for a lighter Docker runtime:
  ```bash
  brew install colima
  colima start
  docker --version
  ```

#### **"Permission denied" (Linux)**
**Problem**: Docker commands fail with permission errors

**Solutions**:
- Add your user to the docker group: `sudo usermod -aG docker $USER`
- Log out and log back in
- Or run with sudo (not recommended for production)

#### **"Connection refused" (Docker)**
**Problem**: Docker container can't connect to your Haiven server

**Solutions**:
- Make sure Docker Desktop is running
- Check that your API key and URL are correct
- Test the Docker command manually:
  ```bash
  docker run -i --rm --pull=always \
    -e HAIVEN_API_KEY="your-api-key" \
    -e HAIVEN_API_URL="https://your-haiven-server.com" \
    --add-host=host.docker.internal:host-gateway \
    ghcr.io/tw-haiven/haiven-mcp-server:latest
  ```

#### **"host.docker.internal not found" (Linux)**
**Problem**: Docker container can't resolve host.docker.internal

**Solutions**:
- Use `--add-host=host.docker.internal:host-gateway` (already in config)
- Or replace `host.docker.internal` with your actual IP address
- For local development: use `172.17.0.1` instead of `host.docker.internal`

### **Python Issues**

#### **"Path not found" or "Command not found"**

**Problem**: AI tool shows errors like "path not found", "invalid directory", or "command not found"

**Solutions**:

##### **1. Use Absolute Path (RECOMMENDED - Most Reliable)**
```json
{
  "mcpServers": {
    "haiven": {
      "command": "/full/path/to/your/haiven-mcp-server/.venv/bin/python",
      "args": ["/full/path/to/your/haiven-mcp-server/mcp_server.py"],
      "env": {
        "HAIVEN_API_URL": "http://localhost:8080",
        "HAIVEN_DISABLE_AUTH": "true"
      }
    }
  }
}
```

##### **2. Get Your Current Directory**
```bash
# In the haiven-mcp-server directory, run:
pwd
# Copy the output and use it to build your absolute paths
```

##### **3. Windows Path Format**
```json
{
  "mcpServers": {
    "haiven": {
      "command": "C:\\Users\\YourName\\path\\to\\haiven-mcp-server\\.venv\\Scripts\\python.exe",
      "args": ["C:\\Users\\YourName\\path\\to\\haiven-mcp-server\\mcp_server.py"],
      "env": {
        "HAIVEN_API_URL": "http://localhost:8080",
        "HAIVEN_DISABLE_AUTH": "true"
      }
    }
  }
}
```

#### **"Authentication failed"**
**Problem**: MCP server connects but fails with authentication errors

**Solutions**:
- Generate a new API key from the Haiven web interface
- Check API key expiration (keys expire based on duration set)
- Verify API key format (should start with `haiven_sk_`)
- Test API key manually:
  ```bash
  curl -H "Authorization: Bearer <YOUR_API_KEY>" \
       https://your-haiven-server.com/api/prompts
  ```

#### **"Python not found"**
**Problem**: AI tool can't find Python executable

**Solutions**:
- Check if the command runs with `python3` instead of `python`
- Install Python 3.11+ from [python.org](https://python.org)
- On macOS, try: `brew install python@3.11`
- Make sure "Add to PATH" was checked during installation

---

## **Testing Your Configuration**

### **Docker Testing**
```bash
# Test Docker installation
docker --version
docker ps

# Test the Docker image
docker run -i --rm \
  -e HAIVEN_API_KEY="your-api-key" \
  -e HAIVEN_API_URL="https://your-haiven-server.com" \
  ghcr.io/tw-haiven/haiven-mcp-server:latest
```

### **Python Testing**
```bash
# Test Python import
python -c "from mcp_server import HaivenMCPServer; print('Import works')"

# Test server startup
python mcp_server.py --help
```

---

## **AI Tool Specific Issues**

### **Claude Desktop**
- **Common issue**: Must restart Claude completely after config changes
- **Debug**: Check Claude's logs for specific error messages

### **VS Code**
- **Common issue**: Extension-specific MCP configuration varies
- **Debug**: Check VS Code's developer console (Help → Toggle Developer Tools)

### **Cursor**
- **Common issue**: Similar to Claude Desktop
- **Debug**: Check Cursor's logs

---

## **Quick Solutions by Error Message**

| Error Message | Solution |
|---------------|----------|
| "docker: command not found" | Install Docker |
| "Permission denied" (Docker) | Add user to docker group |
| "Connection refused" (Docker) | Check Docker is running |
| "path not found" | Use absolute path |
| "Command not found" | Use full path to Python |
| "Module not found" | Run `sh ./scripts/install.sh` |
| "Connection refused" | Start Haiven backend first |
| "HTTP error from Haiven API: 307" | Recheck api-key configuration / create and use new API key |

---

## **Still Having Issues?**

1. **Try Docker setup first** - it's the most reliable option
2. **Run the automated setup**: `sh ./scripts/install.sh`
3. **Check the specific error message** in your AI tool's logs
4. **Use absolute paths** instead of relative paths
5. **Verify Haiven backend is running** (`curl http://localhost:8080`)

**Most common fix**: Use Docker setup or absolute paths to avoid path-related issues!

**MCP Setup Resources:**
- **[VS Code MCP Servers](https://code.visualstudio.com/docs/copilot/chat/mcp-servers)** - Comprehensive guide for VS Code
- **[Claude Code MCP](https://docs.anthropic.com/en/docs/claude-code/mcp)** - Official Claude documentation
- **[Cursor MCP Setup](https://docs.cursor.com/en/context/mcp#using-mcp-json)** - Cursor-specific instructions
- **[MCP Protocol Overview](https://modelcontextprotocol.io/quickstart/user#understanding-mcp-servers)** - General MCP concepts
