import os

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.checkpoint.redis import RedisSaver
from langgraph.prebuilt import create_react_agent

from app.code_agent.model.qwen import llm_qwen
from app.code_agent.tools.file_tools import file_tools


def create_agent():
    # with RedisSaver.from_conn_string("redis://172.20.14.66:6379") as memory:
    MONGODB_URI = "mongodb://172.20.14.66:27017"
    MONGODB_DB = "chat"
    with MongoDBSaver.from_conn_string(MONGODB_URI,MONGODB_DB) as memory:
        agent = create_react_agent(
            model=llm_qwen,
            tools= file_tools,
            checkpointer=memory,
            debug=True
        )

        config = RunnableConfig(configurable={"thread_id": 1})

        # res = agent.invoke(input={"messages": [("user", "你好，我是Ethan")]}, config=config)
        # print("=" * 60)
        # print(res)
        # print("=" * 60)

        res = agent.invoke(input={"messages": [("user", "我叫什么？")]}, config=config)
        print("=" * 60)
        print(res)
        print("=" * 60)

        return agent


if __name__ == '__main__':
    create_agent()