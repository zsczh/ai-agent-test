import shlex
import subprocess
from typing import Annotated

from mcp.server import FastMCP
from pydantic import Field

mcp = FastMCP()

@mcp.tool(name="run_shell", description="Run a shell command")
def run_shell_command(command:
    Annotated[str, Field(description="shell command will be executed", examples="ls -al")]) -> str:
    print(command)
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
    print(run_shell_command("mkdir -p 'd:/study/ai/ai-agent-test/.temp/Test'"))
    #mcp.run(transport="stdio")