from langchain_community.agent_toolkits import FileManagementToolkit

file_toolkit = FileManagementToolkit(root_dir="D:/study/ai/ai-agent-test/.temp")

file_tools = file_toolkit.get_tools()