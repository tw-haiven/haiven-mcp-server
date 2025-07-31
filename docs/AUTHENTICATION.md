# Haiven MCP Server Authentication Guide

This guide explains how to configure authentication for the Haiven MCP server when connecting to OKTA-protected Haiven instances.

## Overview

Haiven uses OKTA for authentication by default. The MCP server needs to authenticate when making API calls to Haiven. There are two authentication methods available:

## Method 1: Development Mode (Recommended for Testing)

**When to use**: Local development, testing, non-production environments

**Setup**:
1. Set `AUTH_SWITCHED_OFF=true` in your Haiven server environment
2. Restart your Haiven server
3. Configure MCP server without authentication:

```json
{
  "mcpServers": {
    "haiven-prompts": {
      "command": "/full/path/to/your/haiven-mcp-server/.venv/bin/python",
      "args": ["/full/path/to/your/haiven-mcp-server/mcp_server.py"],
      "env": {
        "HAIVEN_API_URL": "http://localhost:8080"
      }
    }
  }
}
```

**Pros**: Simple setup, no authentication hassles
**Cons**: Security risk, only suitable for development

## Method 2: API Key Authentication (Recommended for Production)

**When to use**: Production environments, shared Haiven instances

**Setup**:

### Step 1: Generate API Key

1. **Log in to Haiven**:
   - Open your browser
   - Navigate to your Haiven instance
   - Complete the OKTA authentication flow
   - Ensure you can access Haiven successfully

2. **Generate API Key**:
   - Click on "API Keys" in the navigation menu
   - Click "Generate New API Key"
   - Fill out the form:
     - Name: "AI Tool Integration"
     - Expiration: 3 days (or your preference)
   - Copy the generated key immediately (you won't see it again)

### Step 2: Configure MCP Server

**Environment Variable** (Recommended):
```bash
export HAIVEN_API_KEY="your_generated_api_key"
```

**Configuration File**:
```json
{
  "mcpServers": {
    "haiven-prompts": {
      "command": "/full/path/to/your/haiven-mcp-server/.venv/bin/python",
      "args": ["/full/path/to/your/haiven-mcp-server/mcp_server.py"],
      "env": {
        "HAIVEN_API_URL": "https://haiven.yourcompany.com",
        "HAIVEN_API_KEY": "your_generated_api_key"
      }
    }
  }
}
```

### Step 3: Test Authentication

```bash
# Test the connection
cd haiven-mcp-server
python tests/test_setup.py
```

**Important Notes**:
- API keys are valid for the duration you specified (up to 30 days)
- You'll need to generate a new key when the current one expires
- Keep your API key secure - treat it like a password

## Troubleshooting Authentication

### Common Issues

**401 Unauthorized**:
- **API keys**: Check if your API key is valid and not expired
- Generate a fresh API key from the Haiven web interface

**403 Forbidden**:
- Your user might not have access to the required APIs
- Contact your Haiven administrator

**Connection Refused**:
- Check if Haiven server is running
- Verify the API URL is correct
- Check network connectivity

**API Key Expired**:
- API keys expire based on the duration you set (up to 30 days)
- Generate a new API key from the Haiven web interface

### Testing Authentication

**Test without MCP server**:
```bash
# Test with API key
curl -H "Authorization: Bearer <YOUR_API_KEY>" \
     http://localhost:8080/api/prompts
```

**Test with development mode**:
```bash
# On Haiven server
export AUTH_SWITCHED_OFF=true

# Test without authentication
curl http://localhost:8080/api/prompts
```

### Security Best Practices

1. **Never commit API keys to version control**
2. Even if you accidentally did commit, considering revoking the key immediately from the haiven ui
3. **Use environment variables for sensitive data**
4. **Rotate API keys regularly**
5. **Use development mode only for local testing**
6. **Monitor for authentication failures in logs**

### Automation and CI/CD

For automated deployments, consider:

1. **Service accounts**: Request dedicated service accounts from your OKTA admin
2. **API key management**: Implement automated API key rotation
3. **Health checks**: Monitor authentication status
4. **Fallback**: Have a plan for authentication failures
