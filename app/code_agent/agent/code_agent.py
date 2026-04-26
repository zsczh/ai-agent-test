import asyncio


from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import create_react_agent
from app.code_agent.model.qwen import llm_qwen
from app.code_agent.tools.file_tools import file_tools
from app.code_agent.tools.file_saver import FileSaver
from app.code_agent.tools.shell_tools import get_stdio_shell_tools


async def run_agent():
    memory = FileSaver()

    shell_tools = await get_stdio_shell_tools()

    tools = file_tools + shell_tools

    agent = create_react_agent(
        model=llm_qwen,
        tools=tools,
        checkpointer=memory,
        debug=True
    )

    config = RunnableConfig(configurable={"thread_id": 9})

    while True:
        user_input = input("用户： ")

        if user_input.lower() == "exit":
            break
        res = await agent.ainvoke(input={"messages": user_input}, config=config)
        print("助理: ", res["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(run_agent())