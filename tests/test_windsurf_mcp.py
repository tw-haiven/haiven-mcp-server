# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
#!/usr/bin/env python3
"""
Test script to verify MCP server works from Windsurf's perspective.
This simulates how Windsurf would interact with our MCP server.
"""

import asyncio
import json
import os
import subprocess
import sys


async def test_mcp_server_stdio() -> None:
    """Test the MCP server using stdio (how Windsurf communicates with it)."""
    print("🧪 Testing Haiven MCP Server for Windsurf...")

    # Set environment variables
    env = os.environ.copy()
    env["HAIVEN_API_URL"] = "http://localhost:8080"
    env["HAIVEN_DISABLE_AUTH"] = "true"

    # Start the MCP server as subprocess
    server_path = os.path.join(os.path.dirname(__file__), "mcp_server.py")
    process = subprocess.Popen(
        [sys.executable, server_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )

    try:
        # Send initialization request (what Windsurf sends first)
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"roots": {"listChanged": True}},
                "clientInfo": {"name": "windsurf-test", "version": "1.0.0"},
            },
        }

        print("📤 Sending initialization request...")
        if process.stdin is not None:
            process.stdin.write(json.dumps(init_request) + "\n")
            process.stdin.flush()

        # Read response
        if process.stdout is not None:
            response_line = process.stdout.readline()
        else:
            print("❌ No stdout available")
            return
        print(f"📥 Received: {response_line.strip()}")

        if response_line.strip():
            try:
                response = json.loads(response_line.strip())
                if response.get("id") == 1:
                    print("✅ Initialization successful!")

                    # Test tools list request
                    tools_request = {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "list_tools",
                        "params": {},
                    }

                    print("📤 Requesting tools list...")
                    if process.stdin is not None:
                        process.stdin.write(json.dumps(tools_request) + "\n")
                        process.stdin.flush()

                    if process.stdout is not None:
                        tools_response = process.stdout.readline()
                    else:
                        print("❌ No stdout available")
                        return
                    print(f"📥 Tools response: {tools_response.strip()}")

                    if tools_response.strip():
                        tools_data = json.loads(tools_response.strip())
                        if "result" in tools_data and "tools" in tools_data["result"]:
                            tools = tools_data["result"]["tools"]
                            print(f"✅ Found {len(tools)} tools:")
                            for tool in tools:
                                print(f"   - {tool['name']}: {tool['description']}")
                        else:
                            print("❌ No tools found in response")

                else:
                    print("❌ Initialization failed")

            except json.JSONDecodeError:
                print("❌ Invalid JSON response")
        else:
            print("❌ No response received")

        # Check for any errors
        if process.stderr is not None:
            stderr_output = process.stderr.read()
            if stderr_output:
                print(f"⚠️ Server stderr: {stderr_output}")

    except Exception as e:
        print(f"❌ Error during test: {e}")

    finally:
        # Clean up
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


if __name__ == "__main__":
    asyncio.run(test_mcp_server_stdio())
