from langchain.output_parsers import  DatetimeOutputParser
from langchain_core.prompts import ChatPromptTemplate
from app.common import llm

parser = DatetimeOutputParser()
instructions =  parser.get_format_instructions()
#chain = chat_prompt_template | llm | parser

prompt = ChatPromptTemplate.from_messages([
    ("system",f"必须按照以下格式返回日志时间：{instructions}"),
    ("human","请将以下自然语言转换为标准日期时间格式：{text}")
])
print(prompt)
chain = prompt | llm | parser

resp = chain.invoke({
    "text":"二零二六年四月十九日二十三点零七分"
})

print(resp)