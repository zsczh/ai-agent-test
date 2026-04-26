import asyncio
import os
os.environ["PLAYWRIGHT_CONNECT"] = "false"
os.environ["PLAYWRIGHT_HEADLESS"] = "true"  # 不显示窗口（可选）
os.environ["PLAYWRIGHT_ONE_BROWSER"] = "true"
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp_demo import StdioServerParameters, stdio_client, ClientSession

from app.common import llm


async def mcp_playwright_client():

    server_params = StdioServerParameters(
        command="node",
        args=["D:/nvm4w/nodejs/node_modules/@executeautomation/playwright-mcp-server/dist/index.js"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)

            agent = create_react_agent(model=llm,tools=tools,debug=True)

            response = await agent.ainvoke(input={"messages": [("user", "在百度中查询北京今天的天气，读取页面信息并告诉我北京今天的问题、湿度、出行建议")]})
            print(response)

            messages = response["messages"]
            for message in messages:
                if isinstance(message,HumanMessage):
                    print("用户",message.content)
                elif isinstance(message,AIMessage):
                    if message.content:
                        print("助理：",message.content)
                    else:
                        for tool_call in message.tool_calls:
                            print("助理[调用工具]：",tool_call["name"],tool_call["args"])
                elif isinstance(message,ToolMessage):
                    print("调用工具：",message.name)
                    
asyncio.run(mcp_playwright_client())