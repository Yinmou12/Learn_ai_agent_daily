import asyncio

from rich.console import Console
from rich.panel import Panel

from app.async_llm_client import call_many_questions
from app.config import load_settings

console = Console()

async def main_async() -> None:
    settings = load_settings()

    questions = [
        "用一句话解释 Python 异步编程解决什么问题。",
        "用一句话解释 HTTP 429 状态码通常代表什么。",
        "用一句话解释为什么 Agent 项目需要超时处理。",
    ]

    results = await call_many_questions(settings=settings, questions=questions)

    elapsed_seconds = "unknown"

    for result in results:
        if result["question"] == "__elapsed_seconds__":
            elapsed_seconds = result["answer"]
            continue

        if result["error"]:
            console.print(
                Panel.fit(
                    f"问题：{result['question']}\n错误：{result['error']}",
                    title="请求失败",
                )
            )
        else:
            console.print(
                Panel.fit(
                    f"问题：{result['question']}\n回答：{result['answer']}",
                    title="模型回答",
                )
            )
    
    console.print(f"[green]并发调用总耗时：{elapsed_seconds} 秒[/green]")

if __name__ == "__main__":
    asyncio.run(main_async())
            