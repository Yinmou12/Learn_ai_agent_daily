from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel

from app.config import load_settings
from app.exceptions import HistoryArgumentError, InputValidationError, ConfigError
from app.history import append_message, load_history, save_history
from app.llm_client import call_llm

Message = dict [str, str]

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

    parser.add_argument(
        "--debug",
        action="store_true",
        help="开启调试模式，显示完整错误堆栈",
    )

    return parser


def validate_history_limit(limit: int) -> None:
    """校验历史记录显示数量。"""
    if limit < 0:
        raise HistoryArgumentError("history-limit 不能小于 0")


def normalize_message(raw_message: str | None) -> str:
    """
    清洗并校验用户输入。

    注意：空字符串不能发送给大模型。
    如果这里不提前拦截，后面会浪费一次 API 请求，还会让报错更难定位。
    """
    if raw_message is None:
        raise InputValidationError("请使用 --message 传入问题，例如：python main.py --message \"你好\"")

    message = raw_message.strip()
    if not message:
        raise InputValidationError("问题不能为空")
    
    return message


def show_recent_history(history_path: Path, limit: int) -> None:
    """
        展示最近 N 条历史消息。
    """
    validate_history_limit(limit)

    if limit == 0:
        console.print("[yellow]未指定 --history-limit，默认显示最近 10 条。[/yellow]")
        limit = 10
    
    messages = load_history(history_path)

    if not messages:
        console.print("[yellow]当前还没有历史记录。[/yellow]")
        return

    console.print(Panel.fit(f"最近 {limit} 条历史消息", title="History"))

    for message in messages[-limit:]:
        role = message.get("role", "unknown")
        content = message.get("content","")
        console.print(f"[bold]{role}[/bold]: {content}")

def save_dialogue(history_path: Path, user_message: str, assistant_message: str) -> None:
    """保存一轮 user -> assistant 对话。"""
    user_record: Message = {
        "role": "user",
        "content": user_message,
    }

    assistant_record: Message = {
        "role": "assistant",
        "content": assistant_message,
    }

    append_message(user_record, history_path)
    append_message(assistant_record, history_path)


def run_cli() -> None:
    """运行 CLI 主流程。"""
    parser = build_parser()
    args = parser.parse_args()

    if args.clean_history:
        save_history([], args.history_path)
        console.print("[yellow]历史记录已清空。[/yellow]")
        return

    validate_history_limit(args.history_limit)

    if args.show_history_only:
        show_recent_history(args.history_path, args.history_limit)
        return
    
    user_message = normalize_message(args.message)

    if args.history_limit > 0:
        show_recent_history(history_path=args.history_path, limit=args.history_limit)

    settings = load_settings()


    console.print(Panel.fit(user_message, title="User"))

    assistant_message = call_llm(
        settings=settings,
        user_text=user_message,
    )
    console.print(Panel.fit(assistant_message, title="Assistant"))

    if args.no_save:
        console.print("[yellow]本轮对话未保存，因为启用了 --no-save。[/yellow]")
        return
    
    save_dialogue(
        history_path=args.history_path, 
        user_message=user_message, 
        assistant_message=assistant_message
    )

    console.print("[green]本轮对话已保存到历史记录。[/green]")

def handle_cli_error(error: Exception, debug: bool = False) -> None:
    """统一处理 CLI 错误输出。
    
    普通模式：显示用户能看懂的错误。
    debug 模式：把原始异常继续抛出，显示完整 traceback。
    """
    from app.exceptions import LLMCLIError

    if debug:
        raise error

    if isinstance(error, LLMCLIError):
        console.print(f"[red]输入错误：{error}[/red]")
        return

    if isinstance(error, KeyboardInterrupt):
        console.print("\n[yellow]用户中断了程序。[/yellow]")
        return
    
    if isinstance(error, ConfigError):
        console.print(f"[red]配置错误：{error}[/red]")
        return

    # 未知错误继续抛出，保留 traceback，方便 Debug。
    raise error