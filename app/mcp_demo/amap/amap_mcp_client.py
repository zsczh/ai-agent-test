import asyncio
import os

from langchain.agents import initialize_agent, AgentType
from langchain_core.prompts import PromptTemplate

from common import llm, file_tools
from langchain_mcp_adapters.client import MultiServerMCPClient


async def create_amap_mcp_client():
    amap_key = os.environ.get("AMAP_KEY")
    mcp_config = {
        "amap": {
            "url": f"https://mcp.amap.com/sse?key={amap_key}",
            "transport": "sse",
        }
    }

    client = MultiServerMCPClient(mcp_config)
    tools = await client.get_tools()
    print(tools)

    return client,tools

async def create_and_run_agent():
    client, tools = await create_amap_mcp_client()
    print(file_tools)
    agent = initialize_agent(
        llm=llm,
        tools=tools + file_tools,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )

    prompt_template = PromptTemplate.from_template("你是一个智能助手，可以调用高德MCP 工具。\n\n {input}")
    prompt = prompt_template.format(input="""
    目标：
    - 明天上午10点我要从北京南站到北京望京SOHO
    - 线路选择：公交地铁或打车
    - 考虑出行时间和路线，以及天气状况
    
    要求：
    - 制作一个网页来展示出行线路和位置，输出一个 HTML 页面到：D:/study/ai/ai-code_agent-test/.temp 目录下
    - 网页使用简约美观的页面风格，以及卡片展示
    - 行程规划的结果要能够在高德APP中展示，并集成到H5页面中
    """)
    print(prompt)

    resp = await agent.ainvoke(prompt)
    print(resp)

    return resp

asyncio.run(create_and_run_agent())