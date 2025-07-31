# 🔧 MCP Server Troubleshooting Guide

> **💡 Before troubleshooting**: Try our automated setup first:
> ```bash
> ./scripts/install.sh
> ```
> This often resolves common issues automatically!

## 🚨 Common Issues & Solutions

### **🐳 Docker Issues**

#### **"Docker not found"**
**Problem**: AI tool shows "docker: command not found" or similar errors

**Solutions**:
- ✅ Install Docker Desktop from [docker.com](https://docker.com)
- ✅ Make sure Docker Desktop is running
- ✅ Restart your computer after Docker installation
- ✅ On Linux: `sudo apt install docker.io` or equivalent
- ✅ **Mac alternative**: Install Colima for a lighter Docker runtime:
  ```bash
  brew install colima
  colima start
  docker --version
  ```

#### **"Permission denied" (Linux)**
**Problem**: Docker commands fail with permission errors

**Solutions**:
- ✅ Add your user to the docker group: `sudo usermod -aG docker $USER`
- ✅ Log out and log back in
- ✅ Or run with sudo (not recommended for production)

#### **"Connection refused" (Docker)**
**Problem**: Docker container can't connect to your Haiven server

**Solutions**:
- ✅ Make sure Docker Desktop is running
- ✅ Check that your API key and URL are correct
- ✅ Test the Docker command manually:
  ```bash
  docker run -i --rm \
    -e HAIVEN_API_KEY="your-api-key" \
    -e HAIVEN_API_URL="https://your-haiven-server.com" \
    --add-host=host.docker.internal:host-gateway \
    ghcr.io/tw-haiven/haiven-mcp-server:latest
  ```

#### **"host.docker.internal not found" (Linux)**
**Problem**: Docker container can't resolve host.docker.internal

**Solutions**:
- ✅ Use `--add-host=host.docker.internal:host-gateway` (already in config)
- ✅ Or replace `host.docker.internal` with your actual IP address
- ✅ For local development: use `172.17.0.1` instead of `host.docker.internal`

### **🐍 Python Issues**

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

##### **4. Alternative: Use Poetry with Absolute Path**
```json
{
  "mcpServers": {
    "haiven": {
      "command": "poetry",
      "args": ["run", "python", "/full/path/to/your/haiven-mcp-server/mcp_server.py"],
      "cwd": "/full/path/to/your/haiven-mcp-server",
      "env": {
        "HAIVEN_API_URL": "http://localhost:8080",
        "HAIVEN_DISABLE_AUTH": "true"
      }
    }
  }
}
```

##### **5. Module Import Version (Most Reliable)**
```json
{
  "mcpServers": {
    "haiven": {
      "command": "/full/path/to/your/haiven-mcp-server/.venv/bin/python",
      "args": ["-m", "src.mcp_server"],
      "cwd": "/full/path/to/your/haiven-mcp-server",
      "env": {
        "HAIVEN_API_URL": "http://localhost:8080",
        "HAIVEN_DISABLE_AUTH": "true"
      }
    }
  }
}
```

#### **"Error: HTTP error from Haiven API: 307"**

**Problem**: MCP server connects but fails with HTTP 307 error when trying to access Haiven prompts

**Cause**: This typically indicates an authentication issue with your API key

**Solutions**:

##### **1. Check API Key Validity**
- ✅ **Generate a new API key** from the Haiven web interface
- ✅ **Check API key expiration** - keys expire based on the duration you set (up to 365 days)
- ✅ **Verify API key format** - should start with `haiven_sk_` followed by a long string
- ✅ **Test API key manually**:
  ```bash
  curl -H "Authorization: Bearer <YOUR_API_KEY>" \
       https://your-haiven-server.com/api/prompts
  ```

##### **2. Check Haiven Server URL**
- ✅ **Verify the URL is correct** and accessible from your machine
- ✅ **Test server connectivity**:
  ```bash
  curl https://your-haiven-server.com/health
  ```

##### **3. Check User Permissions**
- ✅ **Ensure your user account** has access to the Haiven API
- ✅ **Contact your Haiven administrator** if you don't have the right permissions
- ✅ **Try logging into Haiven web interface** to verify your account works

##### **4. Development Mode Test**
If you're testing locally, try development mode:
```bash
# On your Haiven server
export AUTH_SWITCHED_OFF=true

# Test without authentication
curl http://localhost:8080/api/prompts
```

##### **5. Update MCP Configuration**
After generating a new API key, update your AI tool's configuration:
```json
{
  "mcpServers": {
    "haiven-prompts": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "HAIVEN_API_KEY=your-new-api-key-here",
        "-e", "HAIVEN_API_URL=https://your-haiven-server.com",
        "ghcr.io/tw-haiven/haiven-mcp-server:latest"
      ]
    }
  }
}
```

**Most Common Fix**: Generate a new API key from the Haiven web interface and update your configuration!

---

## 🧪 **Testing Your Configuration**

### **🐳 Docker Testing**

#### **1. Test Docker Installation**
```bash
# Check if Docker is installed and running
docker --version
docker ps

# If using Colima on Mac, also check:
colima status
```

#### **2. Test Docker Image**
```bash
# Test the Docker image directly
docker run -i --rm \
  -e HAIVEN_API_KEY="your-api-key" \
  -e HAIVEN_API_URL="https://your-haiven-server.com" \
  --add-host=host.docker.internal:host-gateway \
  ghcr.io/tw-haiven/haiven-mcp-server:latest
```

#### **3. Test Local Development with Docker**
```bash
# Test against local Haiven instance
docker run -i --rm \
  -e HAIVEN_API_URL="http://host.docker.internal:8080" \
  -e HAIVEN_DISABLE_AUTH="true" \
  --add-host=host.docker.internal:host-gateway \
  ghcr.io/tw-haiven/haiven-mcp-server:latest
```

### **🐍 Python Testing**

#### **1. Verify Your Path**
```bash
# Check if the path exists
ls -la /path/to/your/haiven-mcp-server/
# Should show mcp_server.py file
```

#### **2. Test Python Import**
```bash
# From your haiven-mcp-server directory
python -c "from mcp_server import HaivenMCPServer; print('✅ Import works')"
```

#### **3. Test with Poetry**
```bash
# From your haiven-mcp-server directory
poetry run python -c "from mcp_server import HaivenMCPServer; print('✅ Poetry works')"
```

---

## 📱 **AI Tool Specific Issues**

### **Claude Desktop**
- **Config location**: `~/.config/claude/config.json` (Linux/Mac) or `%APPDATA%\Claude\config.json` (Windows)
- **Common issue**: Must restart Claude completely after config changes
- **Debug**: Check Claude's logs for specific error messages

### **VS Code**
- **Config location**: Settings → search for "mcp"
- **Common issue**: Extension-specific MCP configuration varies
- **Debug**: Check VS Code's developer console (Help → Toggle Developer Tools)

### **Cursor**
- **Config location**: `~/.cursor/config.json`
- **Common issue**: Similar to Claude Desktop
- **Debug**: Check Cursor's logs

---

## 🛠️ **Quick Fix Generator**

Run this script to generate a working config for your system:

```bash
# In your haiven-mcp-server directory
cat > generate_config.py << 'EOF'
import json
import os
import shutil
from pathlib import Path

# Get current directory
current_dir = Path.cwd().absolute()
script_path = current_dir / "mcp_server.py"
venv_python = current_dir / ".venv" / "bin" / "python"
venv_python_windows = current_dir / ".venv" / "Scripts" / "python.exe"

# Check if files exist
if not script_path.exists():
    print("❌ mcp_server.py not found in current directory")
    exit(1)

# Check if Docker is available
docker_available = shutil.which("docker") is not None

# Generate Docker config (if available)
if docker_available:
    config_docker = {
        "mcpServers": {
            "haiven-prompts": {
                "command": "docker",
                "args": [
                    "run", "-i", "--rm",
                    "-e", "HAIVEN_API_KEY=your-api-key-here",
                    "-e", "HAIVEN_API_URL=https://your-haiven-server.com",
                    "--add-host=host.docker.internal:host-gateway",
                    "ghcr.io/tw-haiven/haiven-mcp-server:latest"
                ]
            }
        }
    }
    print("🎯 Docker Configuration (RECOMMENDED):")
    print(json.dumps(config_docker, indent=2))
    print()

# Determine best Python path
if venv_python.exists():
    python_path = str(venv_python)
elif venv_python_windows.exists():
    python_path = str(venv_python_windows)
else:
    python_path = "python"

# Generate Python config with absolute paths
config = {
    "mcpServers": {
        "haiven": {
            "command": python_path,
            "args": [str(script_path)],  # Full path to script
            "env": {
                "HAIVEN_API_URL": "http://localhost:8080",
                "HAIVEN_DISABLE_AUTH": "true"
            }
        }
    }
}

# Alternative with module import
config_module = {
    "mcpServers": {
        "haiven": {
            "command": python_path,
            "args": ["-m", "src.mcp_server"],
            "cwd": str(current_dir),
            "env": {
                "HAIVEN_API_URL": "http://localhost:8080",
                "HAIVEN_DISABLE_AUTH": "true"
            }
        }
    }
}

print("✅ Python Configuration with absolute path (RECOMMENDED):")
print(json.dumps(config, indent=2))

print("\n✅ Python Configuration with module import:")
print(json.dumps(config_module, indent=2))

print(f"\n📁 Current directory: {current_dir}")
print(f"📄 Script path: {script_path}")
print(f"🐍 Python path: {python_path}")
if docker_available:
    print("🐳 Docker is available - use Docker config for easiest setup!")
else:
    print("🐳 Docker not found - using Python setup")
EOF

python generate_config.py
```

---

## 🔍 **Debugging Steps**

### **1. Check AI Tool Logs**
- **Claude Desktop**: Check application logs/console
- **VS Code**: Help → Toggle Developer Tools → Console
- **Cursor**: Similar to VS Code

### **2. Test MCP Server Directly**

#### **Docker Testing**
```bash
# Test Docker server starts up
docker run -i --rm \
  -e HAIVEN_API_KEY="your-api-key" \
  -e HAIVEN_API_URL="https://your-haiven-server.com" \
  --add-host=host.docker.internal:host-gateway \
  ghcr.io/tw-haiven/haiven-mcp-server:latest
```

#### **Python Testing**
```bash
# Test server starts up
python mcp_server.py --help

# Test with environment
export HAIVEN_API_URL=http://localhost:8080
export HAIVEN_DISABLE_AUTH=true
python mcp_server.py
```

### **3. Verify Dependencies**

#### **Docker Dependencies**
```bash
# Check Docker installation
docker --version
docker ps

# Check Docker image
docker pull ghcr.io/tw-haiven/haiven-mcp-server:latest
```

#### **Python Dependencies**
```bash
# Check Python version
python --version

# Check Poetry installation
poetry --version

# Check dependencies
poetry show
```

---

## 💡 **Quick Solutions by Error Message**

| Error Message | Solution |
|---------------|----------|
| "docker: command not found" | Install Docker Desktop |
| "Permission denied" (Docker) | Add user to docker group |
| "Connection refused" (Docker) | Check Docker Desktop is running |
| "host.docker.internal not found" | Use `--add-host=host.docker.internal:host-gateway` |
| "path not found" | Use absolute path |
| "No such file or directory" | Check path exists with `ls` |
| "Permission denied" | Check file permissions |
| "Command not found" | Use full path to Python |
| "Module not found" | Run `poetry install` |
| "Connection refused" | Start Haiven backend first |
| "Invalid JSON" | Validate JSON syntax |
| "HTTP error from Haiven API: 307" | Generate new API key from Haiven web interface |

---

## 🆘 **Still Having Issues?**

1. **Try Docker setup first** - it's the most reliable option
2. **Run the config generator** above to get a working config
3. **Check the specific error message** in your AI tool's logs
4. **Use absolute paths** instead of relative paths
5. **Verify Haiven backend is running** (`curl http://localhost:8080/health`)
6. **Share the exact error message** for more specific help

**Most common fix**: Use Docker setup or absolute paths to avoid path-related issues!
