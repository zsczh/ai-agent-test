import uuid

from langchain_community.agent_toolkits import FileManagementToolkit
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import ChatMessageHistory, FileChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory, RunnableSequence

from app.code_agent.model.qwen import llm_qwen
from app.code_agent.prompts.multi_chat_prompts import multi_chat_prompts
from app.code_agent.tools.file_tools import file_tools

llm_qwen_with_tools = llm_qwen.bind_tools(file_tools)
#chain = multi_chat_prompts | llm_qwen_with_tools | StrOutputParser()

#chain = multi_chat_prompts.pipe(llm_qwen_with_tools).pipe(StrOutputParser())

chain = RunnableSequence(
    first=multi_chat_prompts,
    middle=[llm_qwen_with_tools],
    last=StrOutputParser()
)

chat_history = ChatMessageHistory()

def get_session_history(session_id: str):
    return FileChatMessageHistory(f"""{session_id}.json""")

chain_with_history = RunnableWithMessageHistory(
     runnable=chain,
     get_session_history=get_session_history,
     input_messages_key="question",
     history_messages_key="chat_history"
     )

chat_session_id = "3afbed54-5bfb-42fd-91c5-994ba940111e"
while True:
    user_input = input("用户：")
    if user_input == "exit" or user_input == "quit":
        break

    response = chain_with_history.stream(
        input = {"question":user_input},
        config = {"configurable": {"session_id": chat_session_id}}
    )
    print("助理：",end="")
    for chunk in response:
        print(chunk,end="")

    print("\n")