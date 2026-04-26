from langchain_core.output_parsers import  JsonOutputParser
from langchain.agents import initialize_agent,AgentType
from pydantic import BaseModel, Field

from app.common import create_calc_tools, llm, chat_prompt_template


class Output(BaseModel):
    args:  str = Field("工具的参数")
    result: str = Field("计算的结果")
    think: str = Field("思考过程")

parser = JsonOutputParser(pydantic_object=Output)
format_instructions = parser.get_format_instructions()
# print(format_instructions)

agent = initialize_agent(
    tools=create_calc_tools(),
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

prompt = chat_prompt_template.format_messages(
    role= "计算",
    domain = "使用自定义工具进行数字计算",
    question = f"""
请阅读下面的问题，并返回一个严格的JSON对象，不要使用Markdown代码块包裹！
格式要求：
{format_instructions}

问题：
使用工具计算：100+100=？
"""
)

resp = agent.invoke(prompt)

#print(resp)
print(resp["output"])