from typing import Any

import httpx

from app.config import Settings
from app.exceptions import LLMRequestError

Message = dict[str, str]


def build_messages(user_text: str) -> list[Message]:
    """
    构造大模型 messages。

    system 用来约束模型行为。
    user 放真实用户问题。
    """

    return [
        {"role": "system", "content": "你是一个回答清晰、严谨的 AI Agent 学习助手。"},
        {"role": "user", "content": user_text},
    ]


def parse_assistant_message(response_json: dict[str, Any]) -> str:
    """从 OpenAI-compatible 响应中提取 assistant 回复。"""

    try:
        content = response_json["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as error:
        raise LLMRequestError(f"大模型响应结构异常: {error}") from error

    if not isinstance(content, str):
        raise LLMRequestError(f"大模型返回的 content 不是字符串")

    content = content.strip()
    if not content:
        raise LLMRequestError("大模型返回了空内容")

    return content


def call_llm(settings: Settings, user_text: str) -> str:
    """调用大模型并返回文本回答。"""

    url = f"{settings.llm_base_url.rstrip('/')}/chat/completions"

    headers = {
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": settings.llm_model,
        "messages": build_messages(user_text),
    }

    print("LLM url", url)
    print("LLM model:", settings.llm_model)
    print("message length:", len(user_text))

    try:
        response = httpx.post(url, headers=headers, json=payload, timeout=60.0)
        response.raise_for_status()
    except httpx.HTTPStatusError as error:
        status_code = error.response.status_code
        # response_text = error.response.text

        if status_code == 401:
            message = "大模型 API 鉴权失败，请检查 API Key。"
        elif status_code == 429:
            message = "大模型请求过于频繁或额度不足，请稍后重试。"
        elif status_code >= 500:
            message = "大模型服务暂时不可用，请稍后重试。"
        else:
            message = f"大模型请求失败，HTTP 状态码: {status_code}"

        raise LLMRequestError(
            f"大模型 API 返回错误状态码 {status_code}: {message}"
        ) from error
    except httpx.TimeoutException as error:
        raise LLMRequestError("大模型 API 请求超时，请稍后重试") from error
    except httpx.RequestError as error:
        raise LLMRequestError(f"大模型 API 请求失败: {error}") from error

    try:
        response_data = response.json()
    except ValueError as error:
        raise LLMRequestError("大模型 API 返回的不是合法 JSON") from error

    return parse_assistant_message(response_data)
