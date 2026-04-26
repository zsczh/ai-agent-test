from pydantic import BaseModel, Field

from app.common import chat_prompt_template,llm
from langchain_core.tools import tool

class AddInputArgs(BaseModel):
    a: int = Field(description="first number")
    b: int = Field(description="second number")

@tool(
    description="add two numbers",
    args_schema= AddInputArgs,
    return_direct= True
)
def add (a,b):
    """add two numbers"""
    return a+b

tool_dict = {
    "add" : add
}

llm_with_tools = llm.bind_tools([add])
chain = chat_prompt_template | llm_with_tools

response = chain.invoke(input={"role": "计算","domain":"数学计算","question":"使用工具计算100+100=?"})

print(response)

for tool_call in response.tool_calls:
    print(tool_call)

    args = tool_call["args"]
    print(args)

    function_name = tool_call["name"]
    print(function_name)

    tool_function = tool_dict.get(function_name)
    result = tool_function.invoke(args)
    print(result)





