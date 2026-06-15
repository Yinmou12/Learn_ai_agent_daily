from rich.console import Console
from rich.panel import Panel

from app.config import load_settings
from app.history import append_message, load_history, save_history


console = Console()

def main() -> None:
    """Day 1 最小验证：读取配置，并把用户输入保存到 JSON 历史"""
    try:
        settings = load_settings()
        console.print(Panel("配置读取成功",title="Week 1 Day 1"))

        console.print(f"模型：{settings.model}")
        console.print(f"Base URL：{settings.base_url}")
        console.print("API Key：已读取，但不会打印明文")

        user_text=input("请输入一条测试消息：").strip()
        if not user_text:
            raise ValueError("测试消息不能为空")
        
        append_message({"role": "user", "content": user_text})
        history = load_history()

        console.print(Panel(f"历史消息数量:{len(history)}", title="保存成功"))
        console.print(Panel(f"最后一条消息: {history[-1]['content']}", title="最新消息"))

    except Exception as exc:
        console.print(Panel.fit(str(exc), title="运行失败", style="red"))
        raise

if __name__ == "__main__":
    main()