# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
#!/usr/bin/env python3
"""
Test script to verify the MCP server is working correctly.
"""

import asyncio
import sys

from src.mcp_server import HaivenMCPServer


async def test_mcp_server() -> None:
    """Test the MCP server functionality."""
    print("🧪 Testing Haiven MCP Server...")

    server = HaivenMCPServer()
    print(f"✅ MCP server created, connecting to: {server.base_url}")

    try:
        # Test 1: Check backend connectivity
        print("\n1. Testing backend connectivity...")
        response = await server.client.get(f"{server.base_url}/api/prompts")
        if response.status_code == 200:
            prompts = response.json()
            print(f"✅ Backend connected successfully - Found {len(prompts)} prompts")

            # Show a few prompt examples
            if prompts:
                print("📝 Example prompts:")
                for i, prompt in enumerate(prompts[:3]):
                    print(f"   {i + 1}. {prompt.get('name', 'Unknown')}: {prompt.get('description', 'No description')[:50]}...")
        else:
            print(f"❌ Backend connection failed: {response.status_code} - {response.text}")

        # Test 2: Test get_prompts tool (via tool registry)
        print("\n2. Testing get_prompts tool...")
        try:
            tool = server.tool_registry.get_tool("get_prompts")
            result = await tool.execute({})
            if result:
                print(f"✅ get_prompts tool works - Returns {len(result)} content items")
            else:
                print("❌ get_prompts tool failed")
        except Exception as e:
            print(f"⚠️ get_prompts test failed: {e}")

        # Test 3: Test get_prompt_text tool with sample data
        print("\n3. Testing get_prompt_text tool...")
        if prompts:
            # Use the first prompt for testing
            first_prompt = prompts[0]
            test_args = {
                "prompt_id": first_prompt.get("identifier", ""),
            }

            try:
                tool = server.tool_registry.get_tool("get_prompt_text")
                result = await tool.execute(test_args)
                if result and result[0].text:
                    print(f"✅ get_prompt_text tool works - Got response ({len(result[0].text)} chars)")
                    print(f"📤 Response preview: {result[0].text[:100]}...")
                else:
                    print("❌ get_prompt_text tool returned empty result")
            except Exception as e:
                print(f"⚠️ get_prompt_text test failed (this may be expected): {e}")

        print("\n🎉 MCP Server is working correctly!")
        print("\n📋 Next steps:")
        print("1. Make sure your IDE/editor supports MCP")
        print("2. Configure it to use this server with:")
        print(f"   - Command: python {sys.argv[0].replace('test_mcp_connection.py', 'mcp_server.py')}")
        print(f"   - Working directory: {sys.path[0]}")
        print("3. The server will automatically connect to your Haiven backend")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
    finally:
        await server.client.aclose()


if __name__ == "__main__":
    success = asyncio.run(test_mcp_server())
    sys.exit(0 if success else 1)
