import asyncio
from fastmcp import Client

async def main():
    async with Client("http://localhost:8000/mcp") as client:   # does the handshake for you
        print([t.name for t in await client.list_tools()])
        result = await client.call_tool("doc_search", {"query": "cache key expiration"})
        print(result.data)

asyncio.run(main())