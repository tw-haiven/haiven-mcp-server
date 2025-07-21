# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
#!/usr/bin/env python3
"""
Simple MCP test for Haiven MCP Server
Tests basic connectivity and initialization
"""

import json
import subprocess
import sys
import time


def test_mcp_server_basic() -> bool:
    """Test basic MCP server functionality."""
    print("🧪 Testing Haiven MCP Server Basic Functionality")
    print("=" * 50)

    # Start the server
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

    print(f"Starting server with: {' '.join(docker_command)}")

    try:
        process = subprocess.Popen(
            docker_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1
        )

        # Give server time to start
        time.sleep(2)

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

        print("Sending initialization request...")
        message = json.dumps(init_request) + "\n"
        if process.stdin is not None:
            process.stdin.write(message)
            process.stdin.flush()

        # Read response
        if process.stdout is not None:
            response_line = process.stdout.readline()
        else:
            print("❌ No stdout available")
            return False
        if response_line:
            try:
                response = json.loads(response_line.strip())
                print(f"✅ Received response: {response}")

                # Check if it's a successful initialization
                if "result" in response and "serverInfo" in response["result"]:
                    server_info = response["result"]["serverInfo"]
                    print(f"✅ Server initialized successfully: {server_info}")
                    return True
                else:
                    print(f"❌ Unexpected response format: {response}")
                    return False

            except json.JSONDecodeError:
                print(f"❌ Failed to parse response: {response_line.strip()}")
                return False
        else:
            print("❌ No response received")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        if "process" in locals():
            process.terminate()
            try:
                process.wait(timeout=5)
                print("✅ Server stopped gracefully")
            except subprocess.TimeoutExpired:
                process.kill()
                print("⚠️  Server killed forcefully")


def test_container_health() -> bool:
    """Test container health and basic functionality."""
    print("\n🧪 Testing Container Health")
    print("=" * 30)

    # Test basic container startup
    try:
        result = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "--entrypoint",
                "python",
                "thoughtworks/haiven-mcp-server:test",
                "-c",
                "import sys; print('Container Python working')",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0 and "Container Python working" in result.stdout:
            print("✅ Container Python environment working")
            return True
        else:
            print(f"❌ Container test failed: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Container test timed out")
        return False
    except Exception as e:
        print(f"❌ Container test failed: {e}")
        return False


def main() -> int:
    """Main test function."""
    tests = [test_container_health, test_mcp_server_basic]

    passed = 0
    for test in tests:
        if test():
            passed += 1
        else:
            break

    print(f"\n📊 Test Results: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("\n🎉 All tests passed! Container is working correctly.")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
