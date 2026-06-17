from rich.console import Console
from rich.panel import Panel

from app.config import load_settings
from app.history import append_message, load_history, save_history
from app.http_client import call_echo_api


console = Console()

def main() -> None:
    """Day 1 最小验证：读取配置，并把用户输入保存到 JSON 历史"""
    try:
        settings = load_settings()
        console.print(Panel.fit("配置读取成功",title="Week 1 Day 1"))

        console.print(f"模型：{settings.model}")
        console.print(f"Base URL：{settings.base_url}")
        console.print("API Key：已读取，但不会打印明文")

        user_text=input("请输入一条测试消息：").strip()
        if not user_text:
            raise ValueError("测试消息不能为空")
        
        append_message({"role": "user", "content": user_text})
        api_result = call_echo_api(user_text)
        history = load_history()

        echoed_json = api_result.get("json", {})
        echoed_message = echoed_json.get("message","")

        console.print(Panel.fit(f"测试 API 返回消息：{echoed_message}\n当前历史记录数：{len(history)}条",title="Week 1 Day 1"))

    except Exception as exc:
        console.print(Panel.fit(str(exc), title="运行失败", style="red"))
        raise SystemExit(1) from exc

if __name__ == "__main__":
    main()