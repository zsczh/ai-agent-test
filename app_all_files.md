# app 文件夹所有文件内容汇总

> 生成日期：2026-05-09

---

## 目录结构

```
app/
├── __init__.py
├── common.py
├── bailian/
│   ├── __init__.py
│   ├── bailian.py
│   ├── bailian_agent.py
│   ├── bailian_annotation_prompt.py
│   ├── bailian_output_parser.py
│   ├── bailian_prompt.py
│   ├── bailian_python_perl.py
│   ├── bailian_qwq.py
│   ├── bailian_tools.py
│   └── bailian_tools2.py
├── code_agent/
│   ├── __init__.py
│   ├── 3afbed54-5bfb-42fd-91c5-994ba940111e.json
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── agent_chat.py
│   │   ├── code_agent.py
│   │   └── model_chat.py
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── powershell_tools.py
│   │   ├── shell_tools.py
│   │   └── terminal_tools.py
│   ├── model/
│   │   ├── __init__.py
│   │   └── qwen.py
│   ├── prompts/
│   │   ├── __init__.py
│   │   └── multi_chat_prompts.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── file_saver.py
│   │   ├── file_tools.py
│   │   └── shell_tools.py
│   └── utils/
│       ├── __init__.py
│       └── mcp.py
├── mcp_demo/
│   ├── __init__.py
│   ├── amap/
│   │   ├── __init__.py
│   │   └── amap_mcp_client.py
│   └── stdio/
│       ├── __init__.py
│       ├── mcp_playwright_client.py
│       ├── mcp_stdio_client.py
│       └── mcp_stdio_server.py
└── ollama/
    ├── __init__.py
    └── allama.py
```

---

## 文件内容

---

### 1. app/__init__.py

**路径：** `app/__init__.py`

文件为空内容。

---

### 2. app/common.py

**路径：** `app/common.py`

```python
import os

from langchain_community.agent_toolkits import FileManagementToolkit
from langchain_core.prompts import ChatMessagePromptTemplate, ChatPromptTemplate
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from pydantic import SecretStr, BaseModel, Field

llm = ChatOpenAI(
    model="qwen-max",
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


class AddInputArgs(BaseModel):
    a: int = Field(description="first number")
    b: int = Field(description="second number")

@tool(
    description="add two numbers",
    args_schema= AddInputArgs,
    return_direct= False
)
def add (a,b):
    """add two numbers"""
    return a+b

def create_calc_tools():
    return [add]

calc_tools = create_calc_tools()

file_toolkit = FileManagementToolkit(root_dir="/.temp")
file_tools = file_toolkit.get_tools()
```

---

### 3. app/bailian/__init__.py

**路径：** `app/bailian/__init__.py`

文件为空内容。

---

### 4. app/bailian/bailian.py

**路径：** `app/bailian/bailian.py`

```python
import os
from openai import OpenAI

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

completion = client.chat.completions.create(
    # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    model="qwen-plus",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "你是谁？"},
    ]
)
print(completion.model_dump_json())
```

---

### 5. app/bailian/bailian_agent.py

**路径：** `app/bailian/bailian_agent.py`

```python
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
```

---

### 6. app/bailian/bailian_annotation_prompt.py

**路径：** `app/bailian/bailian_annotation_prompt.py`

```python
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
```

---

### 7. app/bailian/bailian_output_parser.py

**路径：** `app/bailian/bailian_output_parser.py`

```python
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
```

---

### 8. app/bailian/bailian_prompt.py

**路径：** `app/bailian/bailian_prompt.py`

```python
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
```

---

### 9. app/bailian/bailian_python_perl.py

**路径：** `app/bailian/bailian_python_perl.py`

```python

from langchain.agents import initialize_agent,AgentType
from langchain_experimental.tools.python.tool import PythonAstREPLTool

from app.common import llm
from langchain_core.prompts import PromptTemplate

tools = [PythonAstREPLTool()]
tool_name = ["PythonAstREPLTool"]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)

prompt_template = PromptTemplate.from_template("""
尽你所能回答以下问题，你可以使用以下工具：{tool_name}
--
请按照以下格式进行思考：
```
# 思考的过程
- 问题：你必须回答的问题
- 思考：你考虑应该怎么做
- 行动：要采取的行动，应该是[{tool_name}]中的一个
- 行动输入：行动的输入
- 观察：行动的结果
```（这个思考/行动/行动输入/观察可以重复N次）
# 最终结果
对原始输入问题的最终答案
```
--
注意：
- PythonAstREPTool工具的入参是python代码，不允许添加 ```python 或者 ```py 等标记
--
问题：{input}
""")

prompt = prompt_template.format(
    tool_name=", ".join(tool_name),
    input="""
要求：
1. 向 D:/study/ai/ai-code_agent-test/.temp 目录下写入一个新文件，名称为：index.html
2. 写一个在线教育产品的官网，包含3个tab，分别是：首页、实战课、体系课和关于我们
3. 首页展示3个模块，分别是：热门课程、上新课程、爆款课程
4. 关于我们展示平台的联系方式等基本信息
"""
)

agent.invoke(prompt)
```

---

### 10. app/bailian/bailian_qwq.py

**路径：** `app/bailian/bailian_qwq.py`

```python
from openai import OpenAI
import os

# 初始化OpenAI客户端
client = OpenAI(
    # 如果没有配置环境变量，请用阿里云百炼API Key替换：api_key="sk-xxx"
    # 各地域的API Key不同。获取API Key：https://help.aliyun.com/zh/model-studio/get-api-key
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    # 各地域配置不同，请根据实际地域修改
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

messages = [{"role": "user", "content": "你是谁"}]

completion = client.chat.completions.create(
    model="qwq-plus",  # 您可以按需更换为其它深度思考模型
    messages=messages,
    extra_body={"enable_thinking": True},
    stream=True,
    stream_options={
        "include_usage": True
    },
)

reasoning_content = ""  # 完整思考过程
answer_content = ""  # 完整回复
is_answering = False  # 是否进入回复阶段
print("\n" + "=" * 20 + "思考过程" + "=" * 20 + "\n")

for chunk in completion:
    if not chunk.choices:
        print("\nUsage:")
        print(chunk.usage)
        continue

    delta = chunk.choices[0].delta

    # 只收集思考内容
    if hasattr(delta, "reasoning_content") and delta.reasoning_content is not None:
        if not is_answering:
            print(delta.reasoning_content, end="", flush=True)
        reasoning_content += delta.reasoning_content

    # 收到content，开始进行回复
    if hasattr(delta, "content") and delta.content:
        if not is_answering:
            print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
            is_answering = True
        print(delta.content, end="", flush=True)
        answer_content += delta.content

print("\n\n\n")
print("思考的内容")
print(reasoning_content)
print("\n\n\n")
print("回答的内容")
print(answer_content)
```

---

### 11. app/bailian/bailian_tools.py

**路径：** `app/bailian/bailian_tools.py`

```python
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
```

---

### 12. app/bailian/bailian_tools2.py

**路径：** `app/bailian/bailian_tools2.py`

```python
from random import shuffle
from sys import prefix

from langchain_openai import ChatOpenAI
from pydantic import SecretStr
import os
from langchain_core.prompts import ChatPromptTemplate, ChatMessagePromptTemplate, FewShotPromptTemplate, PromptTemplate

llm = ChatOpenAI(
    model="qwen-max-latest",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=SecretStr(os.getenv("DASHSCOPE_API_KEY")),
    streaming= True
)

examples = [
    {"input":"将'Hello'翻译成中文","output":"你好"},
    {"input":"将'Goodbye'翻译成中文","output":"再见"},
    {"input":"将'Pen'翻译成中文","output":"钢笔"}
]
examples_prompt = "输入：{input}\n输出:{output}"

few_shot_with_templates = FewShotPromptTemplate(
    examples=examples,
    example_prompt=PromptTemplate.from_template(examples_prompt),
    prefix="请将一下英文翻译成中文",
    suffix="输入：{text}\n输出：",
    input_variables=["text"],
)

#print(few_shot_with_templates)

#prompt = few_shot_with_templates.format(text = "Thank you!")

#print(prompt)

#response = llm.stream(prompt)

chain = few_shot_with_templates | llm
print(chain)
# response = chain.stream(input ={"text":"Thank you!"})
#
# for chunk in response:
#     print(chunk.content,end="")
```

---

### 13. app/code_agent/__init__.py

**路径：** `app/code_agent/__init__.py`

文件为空内容。

---

### 14. app/code_agent/3afbed54-5bfb-42fd-91c5-994ba940111e.json

**路径：** `app/code_agent/3afbed54-5bfb-42fd-91c5-994ba940111e.json`

```json
[{"type": "human", "data": {"content": "你有那些工具", "additional_kwargs": {}, "response_metadata": {}, "type": "human", "name": null, "id": null, "example": false}}, {"type": "ai", "data": {"content": "我有以下这些工具可以使用：\n\n1. `copy_file` - 用于在指定位置创建文件的副本。\n2. `file_delete` - 用于删除一个文件。\n3. `file_search` - 用于在一个子目录中递归地搜索匹配正则表达式的文件。\n4. `move_file` - 用于将文件从一个位置移动或重命名到另一个位置。\n5. `read_file` - 用于从磁盘读取文件。\n6. `write_file` - 用于将文件写入磁盘，可以选择是否追加到现有文件。\n7. `list_directory` - 用于列出指定文件夹中的文件和目录。\n\n如果你需要使用其中一个工具，请告诉我你需要执行的具体任务。", "additional_kwargs": {}, "response_metadata": {}, "type": "ai", "name": null, "id": null, "example": false, "tool_calls": [], "invalid_tool_calls": [], "usage_metadata": null}}, {"type": "human", "data": {"content": "查询一下 D:/study/ai/ai-agent-test/.temp 的文件列表", "additional_kwargs": {}, "response_metadata": {}, "type": "human", "name": null, "id": null, "example": false}}, {"type": "ai", "data": {"content": "", "additional_kwargs": {}, "response_metadata": {}, "type": "ai", "name": null, "id": null, "example": false, "tool_calls": [], "invalid_tool_calls": [], "usage_metadata": null}}, {"type": "human", "data": {"content": "D:/study/ai/ai-agent-test/.temp 有哪些文件", "additional_kwargs": {}, "response_metadata": {}, "type": "human", "name": null, "id": null, "example": false}}, {"type": "ai", "data": {"content": "", "additional_kwargs": {}, "response_metadata": {}, "type": "ai", "name": null, "id": null, "example": false, "tool_calls": [], "invalid_tool_calls": [], "usage_metadata": null}}, {"type": "human", "data": {"content": "D:/study/ai/ai-agent-test/.temp 目录下有哪些文件", "additional_kwargs": {}, "response_metadata": {}, "type": "human", "name": null, "id": null, "example": false}}, {"type": "ai", "data": {"content": "", "additional_kwargs": {}, "response_metadata": {}, "type": "ai", "name": null, "id": null, "example": false, "tool_calls": [], "invalid_tool_calls": [], "usage_metadata": null}}, {"type": "human", "data": {"content": "你有哪些工具？", "additional_kwargs": {}, "response_metadata": {}, "type": "human", "name": null, "id": null, "example": false}}, {"type": "ai", "data": {"content": "我可以使用以下工具来帮助解决技术问题：\n\n1. `copy_file` - 用于在指定位置创建文件的副本。\n2. `file_delete` - 用于删除一个文件。\n3. `file_search` - 用于在一个子目录中递归地搜索匹配正则表达式的文件。\n4. `move_file` - 用于将文件从一个位置移动或重命名到另一个位置。\n5. `read_file` - 用于从磁盘读取文件的内容。\n6. `write_file` - 用于将文本写入磁盘上的文件，可以选择是否追加到现有文件。\n7. `list_directory` - 用于列出指定文件夹中的所有文件和目录。\n\n如果你需要我使用其中任何一个工具，请告诉我具体的任务详情。比如，如果你想要查看某个目录下的文件列表，可以使用 `list_directory` 工具并提供相应的目录路径。", "additional_kwargs": {}, "response_metadata": {}, "type": "ai", "name": null, "id": null, "example": false, "tool_calls": [], "invalid_tool_calls": [], "usage_metadata": null}}, {"type": "human", "data": {"content": "你有哪些工具", "additional_kwargs": {}, "response_metadata": {}, "type": "human", "name": null, "id": null, "example": false}}, {"type": "ai", "data": {"content": "我有以下工具可以用来帮助处理文件和目录相关的任务：\n\n1. **`copy_file`** - 创建一个文件的副本到指定的位置。\n2. **`file_delete`** - 删除一个文件。\n3. **`file_search`** - 在子目录中递归搜索与正则表达式模式匹配的文件。\n4. **`move_file`** - 将文件从一个位置移动或重命名到另一个位置。\n5. **`read_file`** - 从磁盘读取文件内容。\n6. **`write_file`** - 将文本写入磁盘上的文件，可以选择追加到现有文件。\n7. **`list_directory`** - 列出指定文件夹中的文件和目录。\n\n如果你需要使用这些工具中的任何一个，请告诉我具体的任务细节。例如，要查看某个目录下的所有文件，你可以使用 `list_directory` 并提供相应的目录路径。如果现在需要查询 `D:/study/ai/ai-agent-test/.temp` 目录下的文件列表，我可以使用 `list_directory` 来完成这个操作。是否需要我执行这个操作？", "additional_kwargs": {}, "response_metadata": {}, "type": "ai", "name": null, "id": null, "example": false, "tool_calls": [], "invalid_tool_calls": [], "usage_metadata": null}}, {"type": "human", "data": {"content": "查看D:/study/ai/ai-agent-test/.temp 文件列表", "additional_kwargs": {}, "response_metadata": {}, "type": "human", "name": null, "id": null, "example": false}}, {"type": "ai", "data": {"content": "", "additional_kwargs": {}, "response_metadata": {}, "type": "ai", "name": null, "id": null, "example": false, "tool_calls": [], "invalid_tool_calls": [], "usage_metadata": null}}]
```

---

### 15. app/code_agent/agent/__init__.py

**路径：** `app/code_agent/agent/__init__.py`

文件为空内容。

---

### 16. app/code_agent/agent/agent_chat.py

**路径：** `app/code_agent/agent/agent_chat.py`

```python
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
```

---

### 17. app/code_agent/agent/code_agent.py

**路径：** `app/code_agent/agent/code_agent.py`

```python
import asyncio
import time

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import create_react_agent
from trio import current_time

from app.code_agent.model.qwen import llm_qwen
from app.code_agent.tools.file_tools import file_tools
from app.code_agent.tools.file_saver import FileSaver
from app.code_agent.tools.shell_tools import get_stdio_shell_tools

def format_debug_output(step_name:str ,content:str,is_tool_call=False):
    if is_tool_call:
        print(f"""🔎 【工具调用】 {step_name}""")
    else:
        print(f"""📇 【{step_name}】""")
    print("-"*40)
    print(content.strip())
    print("-"*40)

async def run_agent():
    memory = FileSaver()

    shell_tools = await get_stdio_shell_tools()

    tools = file_tools + shell_tools

    agent = create_react_agent(
        model=llm_qwen,
        tools=tools,
        checkpointer=memory,
        debug=False
    )

    config = RunnableConfig(configurable={"thread_id": 9})

    while True:
        user_input = input("用户： ")

        if user_input.lower() == "exit":
            break

        print("\n🚓 助手正在思考...")
        print("=" * 60)

        iteration_count = 0
        start_time = time.time()
        last_tool_time = start_time
        async for chunk in agent.astream(input={"messages": user_input}, config=config):
            iteration_count += 1
            print(f"\n🛫 第{iteration_count} 步执行：")
            print("-" * 30)

            items = chunk.items()
            for node_name,node_output in items:
                if "messages" in node_output:
                    for msg in node_output["messages"]:
                        if isinstance(msg,AIMessage):
                            if msg.content:
                                format_debug_output("AI思考",msg.content)
                            else:
                                for tool in msg.tool_calls:
                                    format_debug_output("工具调用",f"{tool['name']}:{tool["args"]}")

                        elif isinstance(msg,ToolMessage):
                            tool_name = getattr(msg,"name","unknown")
                            tool_content = msg.content

                            current_time = time.time()
                            tool_duration = current_time - last_tool_time
                            last_tool_time = current_time

                            tool_result = f"""🛸 工具：{tool_name}
🚂 结果：
{tool_content}
✔️ 状态：执行完成，可以开始下一个任务
🌖 执行时间：{tool_duration:.2f}秒"""
                            format_debug_output("工具执行结果",tool_result,is_tool_call=True)
                        else:
                            format_debug_output("未实现",f"暂未实现的打印内容：{chunk}")



if __name__ == "__main__":
    asyncio.run(run_agent())
```

---

### 18. app/code_agent/agent/model_chat.py

**路径：** `app/code_agent/agent/model_chat.py`

```python
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
```

---

### 19. app/code_agent/mcp/__init__.py

**路径：** `app/code_agent/mcp/__init__.py`

文件为空内容。

---

### 20. app/code_agent/mcp/powershell_tools.py

**路径：** `app/code_agent/mcp/powershell_tools.py`

文件为空内容。

---

### 21. app/code_agent/mcp/shell_tools.py

**路径：** `app/code_agent/mcp/shell_tools.py`

```python
import shlex
import subprocess
from typing import Annotated

from mcp.server import FastMCP
from pydantic import Field

mcp = FastMCP()

@mcp.tool(name="run_shell", description="Run a shell command")
def run_shell_command(command:
    Annotated[str, Field(description="shell command will be executed", examples="ls -al")]) -> str:
    try:
        shell_command = shlex.split(command)
        if "rm" in shell_command:
            raise Exception("不允许使用del")

        bash_path = "C:\\Program Files\\Git\\bin\\bash.exe"
        res = subprocess.run([bash_path, "-c", command],shell=True,capture_output=True,text=True)

        if res.returncode != 0:
            return res.stderr
        return res.stdout
    except Exception as e:
        return str(e)

def run_shell_command_popen(command):
    p = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True)
    stdout, stderr = p.communicate()
    if stdout:
        return stdout
    return stderr


if __name__ == '__main__':
    #print(run_shell_command("mkdir -p 'd:/study/ai/ai-agent-test/.temp/Test'"))
    mcp.run(transport="stdio")
```

---

### 22. app/code_agent/mcp/terminal_tools.py

**路径：** `app/code_agent/mcp/terminal_tools.py`

文件为空内容。

---

### 23. app/code_agent/model/__init__.py

**路径：** `app/code_agent/model/__init__.py`

文件为空内容。

---

### 24. app/code_agent/model/qwen.py

**路径：** `app/code_agent/model/qwen.py`

```python
import os

from langchain_openai import ChatOpenAI

llm_qwen = ChatOpenAI(
    model="qwen-max",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    streaming= True
)
```

---

### 25. app/code_agent/prompts/__init__.py

**路径：** `app/code_agent/prompts/__init__.py`

文件为空内容。

---

### 26. app/code_agent/prompts/multi_chat_prompts.py

**路径：** `app/code_agent/prompts/multi_chat_prompts.py`

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

multi_chat_prompts = ChatPromptTemplate.from_messages([
    ("system","你是一位有些的技术专家啊，擅长解决各种开发中的技术问题"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human","{question}")
])
```

---

### 27. app/code_agent/tools/__init__.py

**路径：** `app/code_agent/tools/__init__.py`

文件为空内容。

---

### 28. app/code_agent/tools/file_saver.py

**路径：** `app/code_agent/tools/file_saver.py`

```python
import base64
import json
import os
import pickle
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Tuple, Optional

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import BaseCheckpointSaver, CheckpointTuple, Checkpoint, CheckpointMetadata, \
    ChannelVersions
from langgraph.prebuilt import create_react_agent

from app.code_agent.model.qwen import llm_qwen
from app.code_agent.tools.file_tools import file_tools


class FileSaver(BaseCheckpointSaver[str]):

    def _get_checkpoint_path(self, thread_id,checkpoint_id):
        dir_path = os.path.join(self.base_path, thread_id)
        os.makedirs(dir_path, exist_ok=True)
        return  os.path.join(dir_path, checkpoint_id + ".json")

    def _serialize_data(self, data) -> str:
        pickled = pickle.dumps(data)
        return base64.b64encode(pickled).decode()

    def _deserialize_data (self, data) -> str:
        decoded = base64.b64decode(data)
        return pickle.loads(decoded)

    def __init__(self, base_path: str = "D:/study/ai/ai-agent-test/.temp/checkpoint") -> None:
        super().__init__()
        self.base_path = base_path
        os.makedirs(self.base_path,exist_ok=True)

    def get_tuple(self, config: RunnableConfig) -> CheckpointTuple | None:
        """Fetch a checkpoint tuple using the given configuration.

        Args:
            config: Configuration specifying which checkpoint to retrieve.

        Returns:
            Optional[CheckpointTuple]: The requested checkpoint tuple, or None if not found.

        Raises:
            NotImplementedError: Implement this method in your custom checkpoint saver.
        """
        #1. 找到正确的checkpoint文件路径
        thread_id = config["configurable"]["thread_id"]

        #2. 读取checkpoint文件内容
        dir_path = os.path.join(self.base_path, thread_id)
        checkpoint_files = list(Path(dir_path).glob("*.json"))
        checkpoint_files.sort(key=lambda x: x.stem,reverse=True)

        if len(checkpoint_files) <= 0:
            return None
        latest_checkpoint = checkpoint_files[0]
        checkpoint_id = latest_checkpoint.stem
        checkpoint_file_path = self._get_checkpoint_path(thread_id,checkpoint_id)

        #3. 对文件内容进行反序列化
        with open(checkpoint_file_path,"r",encoding="utf-8") as fp:
            data = json.load(fp)

        checkpoint = self._deserialize_data(data["checkpoint"])
        metadata = self._deserialize_data(data["metadata"])

        #4. 返回checkpoint对象
        return CheckpointTuple(
            config={
                "configurable":{
                    "thread_id":thread_id,
                    "checkpoint_id":checkpoint_id
                }
            },
            checkpoint=checkpoint,
            metadata=metadata
        )

    def put(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        """Store a checkpoint with its configuration and metadata.

        Args:
            config: Configuration for the checkpoint.
            checkpoint: The checkpoint to store.
            metadata: Additional metadata for the checkpoint.
            new_versions: New channel versions as of this write.

        Returns:
            RunnableConfig: Updated configuration after storing the checkpoint.

        Raises:
            NotImplementedError: Implement this method in your custom checkpoint saver.
        """
        #1. 生成存储的JSON 文件的路径
        thread_id = config["configurable"]["thread_id"]
        checkpoint_id = checkpoint["id"]
        checkpoint_path = self._get_checkpoint_path(thread_id,checkpoint_id)

        #2. 将Checkpoint 进行序列化
        checkpoint_data = {
            "checkpoint": self._serialize_data(checkpoint),
            "metadata":  self._serialize_data(metadata)
        }

        #3. 将Checkpoint 存储到文件系统
        with open(checkpoint_path,"w",encoding="utf-8") as fp:
            json.dump(checkpoint_data,fp,ensure_ascii=False,indent=2)
        #4. 生成返回值
        return {
            "configurable":{
                "thread_id":thread_id,
                "checkpoint_id":checkpoint_id
            }
        }

    def put_writes(
        self,
        config: RunnableConfig,
        writes: Sequence[tuple[str, Any]],
        task_id: str,
        task_path: str = "",
    ) -> None:
        """Store intermediate writes linked to a checkpoint.

        Args:
            config: Configuration of the related checkpoint.
            writes: List of writes to store.
            task_id: Identifier for the task creating the writes.
            task_path: Path of the task creating the writes.

        Raises:
            NotImplementedError: Implement this method in your custom checkpoint saver.
        """
        #print("put_writes")

    async def aget_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        """Asynchronously fetch a checkpoint tuple using the given configuration.

        Args:
            config: Configuration specifying which checkpoint to retrieve.

        Returns:
            Optional[CheckpointTuple]: The requested checkpoint tuple, or None if not found.

        Raises:
            NotImplementedError: Implement this method in your custom checkpoint saver.
        """
        return self.get_tuple(config)

    async def aput(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        """Asynchronously store a checkpoint with its configuration and metadata.

        Args:
            config: Configuration for the checkpoint.
            checkpoint: The checkpoint to store.
            metadata: Additional metadata for the checkpoint.
            new_versions: New channel versions as of this write.

        Returns:
            RunnableConfig: Updated configuration after storing the checkpoint.

        Raises:
            NotImplementedError: Implement this method in your custom checkpoint saver.
        """
        return self.put(config, checkpoint, metadata, new_versions)

    async def aput_writes(
        self,
        config: RunnableConfig,
        writes: Sequence[Tuple[str, Any]],
        task_id: str,
        task_path: str = "",
    ) -> None:
        """Asynchronously store intermediate writes linked to a checkpoint.

        Args:
            config: Configuration of the related checkpoint.
            writes: List of writes to store.
            task_id: Identifier for the task creating the writes.
            task_path: Path of the task creating the writes.

        Raises:
            NotImplementedError: Implement this method in your custom checkpoint saver.
        """
        return self.put_writes(config, writes, task_id, task_path)

if __name__ == '__main__':
    memory = FileSaver()

    agent = create_react_agent(
        model=llm_qwen,
        tools=file_tools,
        checkpointer=memory,
        debug=False
    )

    config = RunnableConfig(configurable={"thread_id":2})

    while True:
        user_input = input("用户： ")

        if user_input.lower() == "exit":
            break
        res = agent.invoke(input={"messages":user_input},config=config)
        print("助理: ",res["messages"][-1].content)
```

---

### 29. app/code_agent/tools/file_tools.py

**路径：** `app/code_agent/tools/file_tools.py`

```python
from langchain_community.agent_toolkits import FileManagementToolkit

file_toolkit = FileManagementToolkit(root_dir="D:/study/ai/ai-agent-test/.temp")

file_tools = file_toolkit.get_tools()
```

---

### 30. app/code_agent/tools/shell_tools.py

**路径：** `app/code_agent/tools/shell_tools.py`

```python
from app.code_agent.utils.mcp import create_mcp_stdio_client


async def get_stdio_shell_tools():
    params = {
        "command": "python",
        "args":[
            "D:/study/ai/ai-agent-test/app/code_agent/mcp/shell_tools.py"
        ],
    }

    client,tools = await create_mcp_stdio_client("shell_tools",params)

    return tools
```

---

### 31. app/code_agent/utils/__init__.py

**路径：** `app/code_agent/utils/__init__.py`

文件为空内容。

---

### 32. app/code_agent/utils/mcp.py

**路径：** `app/code_agent/utils/mcp.py`

```python
from langchain_mcp_adapters.client import MultiServerMCPClient 

async def create_mcp_stdio_client(name,params):
    config = {
        name : {
            "transport" : "stdio",
            **params
        }
    }

    client = MultiServerMCPClient(config)

    tools = await client.get_tools()

    return client,tools
```

---

### 33. app/mcp_demo/__init__.py

**路径：** `app/mcp_demo/__init__.py`

文件为空内容。

---

### 34. app/mcp_demo/amap/__init__.py

**路径：** `app/mcp_demo/amap/__init__.py`

文件为空内容。

---

### 35. app/mcp_demo/amap/amap_mcp_client.py

**路径：** `app/mcp_demo/amap/amap_mcp_client.py`

```python
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
```

---

### 36. app/mcp_demo/stdio/__init__.py

**路径：** `app/mcp_demo/stdio/__init__.py`

文件为空内容。

---

### 37. app/mcp_demo/stdio/mcp_playwright_client.py

**路径：** `app/mcp_demo/stdio/mcp_playwright_client.py`

```python
import asyncio
import os
os.environ["PLAYWRIGHT_CONNECT"] = "false"
os.environ["PLAYWRIGHT_HEADLESS"] = "true"  # 不显示窗口（可选）
os.environ["PLAYWRIGHT_ONE_BROWSER"] = "true"
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import StdioServerParameters, stdio_client, ClientSession

from app.common import llm


async def mcp_playwright_client():

    server_params = StdioServerParameters(
        command="node",
        args=["D:/nvm4w/nodejs/node_modules/@executeautomation/playwright-mcp-server/dist/index.js"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)

            agent = create_react_agent(model=llm,tools=tools,debug=True)

            response = await agent.ainvoke(input={"messages": [("user", "在百度中查询北京今天的天气，读取页面信息并告诉我北京今天的问题、湿度、出行建议")]})
            print(response)

            messages = response["messages"]
            for message in messages:
                if isinstance(message,HumanMessage):
                    print("用户",message.content)
                elif isinstance(message,AIMessage):
                    if message.content:
                        print("助理：",message.content)
                    else:
                        for tool_call in message.tool_calls:
                            print("助理[调用工具]：",tool_call["name"],tool_call["args"])
                elif isinstance(message,ToolMessage):
                    print("调用工具：",message.name)
                    
asyncio.run(mcp_playwright_client())
```

---

### 38. app/mcp_demo/stdio/mcp_stdio_client.py

**路径：** `app/mcp_demo/stdio/mcp_stdio_client.py`

```python
import asyncio

from langchain.agents import initialize_agent, AgentType
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent

from app.common import llm

# 使用stdio模式

async def create_mcp_stdio_client():
    server_params = StdioServerParameters(
        command="python",
        args=["D:/study/ai/ai-agent-test/app/mcp_demo/stdio/mcp_stdio_server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            print(tools)

            agent = initialize_agent(llm =llm,
                                     tools = tools,
                                     agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
                                     verbose=True)

            resp = await agent.ainvoke("1 + 2 * 5 = ?")
            print(resp)

asyncio.run(create_mcp_stdio_client())
```

---

### 39. app/mcp_demo/stdio/mcp_stdio_server.py

**路径：** `app/mcp_demo/stdio/mcp_stdio_server.py`

```python
from mcp.server import FastMCP

mcp = FastMCP("Math Tools")


@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    return a * b

if __name__ == '__main__':
    mcp.run(transport="stdio")
```

---

### 40. app/ollama/__init__.py

**路径：** `app/ollama/__init__.py`

文件为空内容。

---

### 41. app/ollama/allama.py

**路径：** `app/ollama/allama.py`

```python
from langchain_ollama.llms import OllamaLLM

if __name__ == "__main__":
    model = OllamaLLM(model="qwen2:1.5b")
    resp = model.invoke("你是谁?")
    print(resp)