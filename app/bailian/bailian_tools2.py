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
