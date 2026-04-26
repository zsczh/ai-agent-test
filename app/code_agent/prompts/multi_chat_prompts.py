from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

multi_chat_prompts = ChatPromptTemplate.from_messages([
    ("system","你是一位有些的技术专家啊，擅长解决各种开发中的技术问题"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human","{question}")
])