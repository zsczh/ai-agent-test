import asyncio

from langchain.agents import initialize_agent, AgentType
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent

from app.common import llm

# 使用stdio模式

async def create_mcp_stdio_client():
    server_params = StdioServerParameters(
        command="python",
        args=["D:/study/ai/ai-agent-test/app/mcp_demo/stdio/mcp_stdio_server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            print(tools)

            agent = initialize_agent(llm =llm,
                                     tools = tools,
                                     agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
                                     verbose=True)

            resp = await agent.ainvoke("1 + 2 * 5 = ?")
            print(resp)

asyncio.run(create_mcp_stdio_client())
