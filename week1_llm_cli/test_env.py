import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

# 初始化 rich 终端控制台
console = Console()

# 加载 .env 文件
# load_dotenv() 会自动寻找当前目录下的 .env 文件并将其载入到os.environ中
load_dotenv()

def verify_env():
    # 读取环境变量
    api_key = os.getenv("API_KEY")
    base_url = os.getenv("BASE_URL")

    # 验证逻辑
    if api_key and base_url:
        success_msg = (
            f"[bold green] .env配置文件读取成功 [/bold green]\n\n"
            f"[bold]BASE_URL: [/bold] {base_url}\n"
            f"[bold]API_KEY: [/bold] {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else ''}"
        )
        console.print(Panel(success_msg, title="检查结果"),style="green")
    else:
        error_msg = "[bold red] 未能成功读取环境变量！ [/bold red]\n请检查当前目录下是否存在.env文件"
        console.print(Panel(error_msg, title="检查结果"),style="red")

if __name__ == "__main__":
    verify_env()