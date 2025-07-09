# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
# Thin launcher for Haiven MCP Server
from src.mcp_server import main

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
