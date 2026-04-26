from langchain_openai import ChatOpenAI
from pydantic import SecretStr
import os
from langchain_core.prompts import ChatPromptTemplate,ChatMessagePromptTemplate

llm = ChatOpenAI(
    model="qwen-max-latest",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=SecretStr(os.getenv("DASHSCOPE_API_KEY")),
    streaming= True
)

system_message_template = ChatMessagePromptTemplate.from_template(
    template="你是一位{role}专家，擅长回答{domain}领域的问题",
    role = "system"
)

human_message_template = ChatMessagePromptTemplate.from_template(
    template="用户问题：{question}",
    role = "user"
)

chat_prompt_template = ChatPromptTemplate.from_messages([
    system_message_template,
    human_message_template
])
prompt = chat_prompt_template.format(
    role="编程",
    domain="web专家",
    question="你擅长什么？"
)

print(prompt)

response = llm.stream(prompt)

for chunk in response:
    print(chunk.content,end="")