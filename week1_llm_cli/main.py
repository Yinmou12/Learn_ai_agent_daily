from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from app.config import load_settings
from app.history import append_message, load_history, save_history
from app.llm_client import call_llm

Message = dict[str, str]

console = Console()

def build_parser() -> argparse.ArgumentParser:
    """
        创建命令行参数解析器
        main.py 是项目入口，所以这里负责定义"用户可以怎么使用这个工具"
    """

    parser = argparse.ArgumentParser(
        prog="llm-cli",
        description="一个最小可用的 LLM 命令行调用工具",
    )

    parser.add_argument(
        "-m",
        "--message",
        type=str,
        required=False,
        help="要发送给大模型的问题，例如：--message '解释 async def'",
    )

    parser.add_argument(
        "--no-save",
        action="store_true",
        help="只调用大模型，不把本轮对话保存到历史文件",
    )

    parser.add_argument(
        "--history-limit",
        type=int,
        default=0,
        help="调用前显示最近 N 条历史消息；默认 0 表示不显示",
    )

    parser.add_argument(
        "--history-path",
        type=Path,
        default=Path("data") / "history.json",
        help="历史记录文件路径，默认 data/history.json",
    )

    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="控制大模型回答稳定性参数，默认 0.7",
    )

    parser.add_argument(
        "--clean-history",
        action="store_true",
        help="清空历史记录文件",
    )

    parser.add_argument(
        "--show-history-only",
        action="store_true",
        help="只显示历史记录，不调用大模型",
    )

    return parser

def normalize_message(raw_message: str | None) -> str:
    """
    清洗并校验用户输入。

    注意：空字符串不能发送给大模型。
    如果这里不提前拦截，后面会浪费一次 API 请求，还会让报错更难定位。
    """
    if raw_message is None:
        raise ValueError("请使用 --message 传入问题，例如：python main.py --message \"你好\"")

    message = raw_message.strip()
    if not message:
        raise ValueError("问题不能为空")
    
    return message

def show_recent_historty(hisory_path: Path, limit: int) -> None:
    """
        展示最近 N 条历史消息。
    """
    console.print(Panel.fit(f"历史记录文件路径：{hisory_path}", title="History Path"))
    if limit <= 0:
        return
    
    messages = load_history(hisory_path)

    if not messages:
        console.print("[yellow]当前还没有历史记录。[/yellow]")
        return

    console.print(Panel.fit(f"最近 {limit} 条历史消息", title="History"))

    for message in messages[-limit:]:
        role = message.get("role", "unknown")
        content = message.get("content","")
        console.print(f"[bold]{role}[/bold]: {content}")

def save_dialogue(hisory_path: Path, user_message: str, assistant_message: str) -> None:
    """保存一轮 user -> assistant 对话。"""
    user_record: Message = {
        "role": "user",
        "content": user_message,
    }

    assistant_record: Message = {
        "role": "assistant",
        "content": assistant_message,
    }

    append_message(user_record, hisory_path)
    append_message(assistant_record, hisory_path)


def run_cli() -> None:
    """
    CLI 主流程。

    这里是“编排层”：
    - 不直接写 HTTP 请求
    - 不直接解析大模型响应
    - 不直接处理配置文件细节

    这些能力都交给 app/ 下面的模块。
    """
    parser = build_parser()
    args = parser.parse_args()

    if args.clean_history:
        save_history([], path=args.history_path)
        console.print("[green]历史记录已清空。[/green]")
        return
    
    if args.show_history_only:
        show_recent_historty(
            hisory_path=args.history_path,
            limit=args.history_limit,
        )
        return

    user_message = normalize_message(args.message)

    show_recent_historty(
        hisory_path=args.history_path,
        limit=args.history_limit,
    )

    settings = load_settings()

    console.print(Panel.fit(user_message, title="User"))

    assistant_message = call_llm(
        settings=settings,
        user_text=user_message,
        temperature=args.temperature,
    )

    console.print(Panel.fit(assistant_message, title="Assistant"))
    if args.no_save:
        console.print("[yellow]本轮对话未保存，因为启用了 --no-save。[/yellow]")
        return
    
    save_dialogue(
        hisory_path=args.history_path,
        user_message=user_message,
        assistant_message=assistant_message,
    )

    console.print("[green]本轮对话已保存到历史记录。[/green]")

if __name__ == "__main__":
    try:
        run_cli()
    except ValueError as error:
        console.print(f"[red]参数错误：{error}[/red]")
    except KeyboardInterrupt:
        console.print("[yellow]用户中断了程序。[/yellow]")
    except Exception as error:
        console.print(f"[red]程序运行失败：{error}[/red]")
        raise