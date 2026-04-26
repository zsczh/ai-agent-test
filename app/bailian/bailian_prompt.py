from app.common import chat_prompt_template,llm
from langchain_core.tools import Tool

def add (a,b):
    return a+b

add_tools = Tool.from_function(
    func=add,
    name="add",
    description="add two numbers",
)

tool_dict = {
    "add" : add
}

llm_with_tools = llm.bind_tools([add_tools])
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
    result = tool_function(int(args["__arg1"]),int(args["__arg2"]))
    print(result)





