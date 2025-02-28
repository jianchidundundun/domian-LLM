import typer
from rich import print
from ..core.llm_manager import LLMManager
from ..adapter.adapter_manager import AdapterManager

app = typer.Typer()
llm_manager = LLMManager()
adapter_manager = AdapterManager()

@app.command()
def query(text: str):
    """向LLM发送查询"""
    try:
        response = llm_manager.process_query(text)
        print(f"[green]AI响应:[/green] {response}")
    except Exception as e:
        print(f"[red]错误:[/red] {str(e)}")

@app.command()
def analyze(domain: str, task: str):
    """执行特定领域的任务"""
    try:
        result = adapter_manager.execute_task(domain, {"task": task})
        print(f"[blue]任务结果:[/blue] {result}")
    except Exception as e:
        print(f"[red]错误:[/red] {str(e)}") 