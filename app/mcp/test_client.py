import asyncio
import sys

from mcp import Client, StdioServerParameters


async def main():

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "app.mcp.server"])

    async with Client(server_params) as client:

        result = await client.call_tool(
            "get_incident_information",
            {
                "incident_id": "INC-1002"
            }
        )

        print(result)


if __name__ == "__main__":
    asyncio.run(main())