from rich.console import Console
from rich.panel import Panel

from app.config import load_settings
from app.history import append_message, load_history, save_history
from app.llm_client import call_llm


console = Console()

def main() -> None:
    try:
        settings = load_settings()

        console.print(
            Panel.fit(
                f"模型配置读取成功\n模型: {settings.model}\n地址: {settings.base_url}",
                title="配置检查"
            )
        )

        user_input = input("请输入您的问题：").strip()
        if not user_input:
            raise ValueError("输入不能为空")
        
        # 第一步：先保存用户消息，确保用户输入不会丢
        append_message(
            {
                "role":"user",
                "content": user_input,
            }
        )

        # 第二步：调用大模型，把用户输入变成模型回答
        assistant_reply = call_llm(
            settings=settings, 
            user_text=user_input,
            temperature=2.1
        )
        
        # 第三步：保存模型回答，形成一轮完整对话
        append_message(
            {
                "role":"assistant",
                "content": assistant_reply,
            }
        )

        history = load_history()
        console.print(
            Panel.fit(
                assistant_reply,
                title=f"模型回答|当前历史消息数: {len(history)}",
            )
        )
    except (ValueError, Exception, FileNotFoundError) as exc:
        console.print(f"[red]运行失败: {exc}[/red]")
        raise SystemExit(1) from exc

if __name__ == "__main__":
    main()