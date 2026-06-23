import asyncio
from time import perf_counter
from typing import Any

import httpx

from app.config import Settings

Message = dict[str, Any]

def build_messages(user_text: str) -> list[Message]:
    clean_text = user_text.strip()

    if not clean_text:
        raise ValueError("User text cannot be empty")
    
    return[
        {
            "role":"system",
            "content": "你是一个严谨的 AI Agent 学习助手，请用中文简洁回答。"
        },
        {
            "role":"user",
            "content": clean_text
        },
    ]

def parse_assistant_message(response_data: dict) -> str:
    choices = response_data.get("choices")
    if not isinstance(choices, list) or not choices:
        raise RuntimeError("No choices found in response")
    
    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        raise RuntimeError("Choices[0] is not a dictionary")
    
    message = first_choice.get("message")
    if not isinstance(message, dict):
        raise RuntimeError("Message is not a dictionary")
    
    content = message.get("content")
    if not isinstance(content, str) or not content:
        raise RuntimeError("Content is not a string")

    return content


async def request_json_async(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    headers: dict[str, str] | None = None,
    json_body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    clean_url = url.strip()
    if not clean_url.startswith(("http://", "https://")):
        raise ValueError("Invalid URL: must start with 'http://' or 'https://'")
    
    try:
        response = await client.request(
            method=method,
            url=clean_url,
            headers=headers,
            json=json_body,
        )

        response.raise_for_status()

        data = response.json()
    except httpx.TimeoutException as exc:
        raise RuntimeError(f"Request timed out: {clean_url}") from exc
    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code
        raise RuntimeError(f"Request failed with status code {status_code}, {clean_url}") from exc
    except httpx.RequestError as exc:
        raise RuntimeError(f"Request error: {clean_url},because {exc}") from exc
    except ValueError as exc:
        raise RuntimeError(f"Value error: {clean_url}") from exc
    
    if not isinstance(data, dict):
        raise RuntimeError(f"Expected dict, got {type(data)}")

    return data


async def call_llm_async(
        client: httpx.AsyncClient,
        settings: Settings,
        user_text: str,
        temperature: float = 0.3,
) -> str:
    url = f"{settings.base_url.rstrip('/')}/chat/completions"

    headers = {
        "Authorization": f"Bearer {settings.api_key}",
        "Content-Type": "application/json",
    }

    if temperature < 0 or temperature > 2:
        raise ValueError("Temperature must be between 0 and 2")
    request_body = {
        "model": settings.model,
        "messages": build_messages(user_text),
        "temperature": temperature,
    }

    # 关键点：这里必须 await，否则请求不会真正被异步等待
    response_data = await request_json_async(
        client=client,
        method="POST",
        url=url,
        headers=headers,
        json_body=request_body,
    )
    return parse_assistant_message(response_data)

async def call_many_questions(
    settings: Settings,
    questions: list[str],
    max_questions: int = 5,
    timeout_seconds: float = 60.0,
) -> list[dict[str, str]]:
    if not questions:
        raise ValueError("Questions list cannot be empty")
    
    if len(questions) > max_questions:
        raise ValueError(f"Questions list cannot exceed {max_questions} items")

    timeout = httpx.Timeout(timeout_seconds)

    async with httpx.AsyncClient(timeout=timeout) as client:
        start_time = perf_counter()

        # 关键点：创建多个协程对象。此时还没有真正等待结果。
        tasks = [
            call_llm_async(
                client=client,
                settings=settings,
                user_text=question,
            ) for question in questions
        ]

        # 关键点：gather 会并发等待这些任务完成。
        # return_exceptions=True 的作用是：某个请求失败时，不让整个程序直接崩掉。
        raw_results = await asyncio.gather(*tasks, return_exceptions=True)

        elapsed_seconds = perf_counter() - start_time

    results: list[dict[str, str]] = []
    for question, raw_result in zip(questions, raw_results):
        if isinstance(raw_result, Exception):
            results.append(
                {
                    "question": question,
                    "answer": "",
                    "error": str(raw_result),
                }
            )
        else:
            results.append(
                {
                    "question": question,
                    "answer": raw_result,
                    "error": "",
                }
            )
    
    results.append(
        {
            "question": "__elapsed_seconds__",
            "answer": f"{elapsed_seconds:.2f}",
            "error": "",
        }
    )

    return results