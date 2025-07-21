# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
#!/usr/bin/env python3
"""
Simple MCP client test for Haiven MCP Server
Tests basic MCP protocol communication
"""

import json
import subprocess
import sys
import time
from typing import Any


class SimpleMCPClient:
    """Simple MCP client for testing."""

    def __init__(self, server_command: list):
        self.server_command = server_command
        self.process = None

    def start_server(self):
        """Start the MCP server process."""
        try:
            self.process = subprocess.Popen(
                self.server_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1
            )
            print(f"✅ Started MCP server with command: {' '.join(self.server_command)}")
            return True
        except Exception as e:
            print(f"❌ Failed to start MCP server: {e}")
            return False

    def send_message(self, message: dict[str, Any]) -> dict[str, Any]:
        """Send a message to the MCP server and get response."""
        if not self.process:
            raise RuntimeError("Server not started")

        # Send message
        message_str = json.dumps(message) + "\n"
        self.process.stdin.write(message_str)
        self.process.stdin.flush()

        # Read response
        response_line = self.process.stdout.readline()
        if not response_line:
            raise RuntimeError("No response from server")

        try:
            return json.loads(response_line.strip())
        except json.JSONDecodeError:
            print(f"❌ Failed to parse response: {response_line.strip()}")
            raise

    def test_initialization(self) -> bool:
        """Test MCP server initialization."""
        print("\n🧪 Testing MCP server initialization...")

        # Send initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            },
        }

        try:
            response = self.send_message(init_request)
            print(f"✅ Initialization response: {response}")
            return True
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            return False

    def test_list_tools(self) -> bool:
        """Test listing available tools."""
        print("\n🧪 Testing tool listing...")

        list_tools_request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}

        try:
            response = self.send_message(list_tools_request)
            print(f"✅ Tools response: {response}")

            # Check if we got the expected tools
            if "result" in response and "tools" in response["result"]:
                tools = response["result"]["tools"]
                tool_names = [tool.get("name", "") for tool in tools]
                print(f"📋 Available tools: {tool_names}")

                expected_tools = ["get_prompts", "get_prompt_text"]
                for expected in expected_tools:
                    if expected in tool_names:
                        print(f"✅ Found expected tool: {expected}")
                    else:
                        print(f"❌ Missing expected tool: {expected}")
                        return False

                return True
            else:
                print(f"❌ Unexpected response format: {response}")
                return False

        except Exception as e:
            print(f"❌ Tool listing failed: {e}")
            return False

    def test_call_tool(self) -> bool:
        """Test calling a tool."""
        print("\n🧪 Testing tool call...")

        call_tool_request = {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "get_prompts", "arguments": {}}}

        try:
            response = self.send_message(call_tool_request)
            print(f"✅ Tool call response: {response}")
            return True
        except Exception as e:
            print(f"❌ Tool call failed: {e}")
            return False

    def stop_server(self):
        """Stop the MCP server process."""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
                print("✅ Server stopped gracefully")
            except subprocess.TimeoutExpired:
                self.process.kill()
                print("⚠️  Server killed forcefully")

    def run_tests(self) -> bool:
        """Run all MCP tests."""
        print("🧪 Running MCP Protocol Tests")
        print("=" * 40)

        if not self.start_server():
            return False

        try:
            # Give server time to start
            time.sleep(1)

            # Run tests
            tests = [self.test_initialization, self.test_list_tools, self.test_call_tool]

            passed = 0
            for test in tests:
                if test():
                    passed += 1
                else:
                    break

            print(f"\n📊 Test Results: {passed}/{len(tests)} tests passed")
            return passed == len(tests)

        finally:
            self.stop_server()


def main():
    """Main test function."""
    # Test with Docker container
    docker_command = [
        "docker",
        "run",
        "--rm",
        "-i",
        "-e",
        "HAIVEN_API_URL=http://host.docker.internal:8080",
        "-e",
        "HAIVEN_DISABLE_AUTH=true",
        "thoughtworks/haiven-mcp-server:test",
    ]

    print("Testing Docker container MCP server...")
    client = SimpleMCPClient(docker_command)

    if client.run_tests():
        print("\n🎉 All MCP tests passed!")
        return 0
    else:
        print("\n❌ Some MCP tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
