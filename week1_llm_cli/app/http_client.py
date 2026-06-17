from typing import Any,Literal
import httpx

HttpMethod=Literal["GET","POST"]

def request_json(
        method: HttpMethod,
        url:str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any]| None = None,
        timeout_seconds: float = 10.0,
) -> dict[str, Any]:
    """发送 HTTP 请求，并把 JSON 响应解析成字典。"""
    clean_url = url.strip()

    if not clean_url.startswith(("http://", "https://")):
        raise ValueError("url 必须以 http:// 或 https:// 开头")
    
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds 必须大于 0")
    
    try:
        with httpx.Client(timeout=timeout_seconds) as client:
            response = client.request(
                method=method,
                url=clean_url,
                headers=headers,
                params=params,
                json=json_body
            )

            # 如果是 4xx 或 5xx，这里会主动抛出异常，避免你误以为请求成功
            response.raise_for_status()

            data = response.json()
    except httpx.TimeoutException as exc:
        raise RuntimeError(f"请求超时：{clean_url}") from exc
    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code
        raise RuntimeError(f"HTTP 状态码错误：{status_code}，url={clean_url}") from exc
    except httpx.RequestError as exc:
        raise RuntimeError(f"请求发送失败：{clean_url}，原因：{exc}") from exc
    except ValueError as exc:
        raise RuntimeError("响应内容不是合法 JSON") from exc
    
    if not isinstance(data, dict):
        raise RuntimeError("响应 JSON 顶层不是字典，暂时不符合本项目处理规则")

    return data

def call_echo_api(message: str) -> dict[str, Any]:
    """调用测试接口，把用户输入原样发出去，验证 POST 请求流程。"""
    clean_message = message.strip()

    if not clean_message:
        raise ValueError("message 不能为空")

    return request_json(
        method="POST",
        url="https://httpbin.org/post",
        json_body={
            "message": clean_message,
            "source": "week1_llm_cli",
        },
        timeout_seconds=10.0,
    )

def request_get_json(
        url:str,
        params: dict[str, Any] | None = None,
        timeout_seconds: float = 10.0,
) -> dict[str, Any]:
    """发送 GET 请求，并把 JSON 响应解析成字典。"""
    return request_json(
        method="GET",
        url=url,
        params=params,
        timeout_seconds=timeout_seconds,
    )

