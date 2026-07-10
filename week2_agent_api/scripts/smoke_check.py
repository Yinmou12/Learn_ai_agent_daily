from __future__ import annotations

from typing import Any

import httpx

BASE_URL = "http://127.0.0.1:8000"


def request_json(method: str, path: str) -> dict[str, Any]:
    """请求本地接口并返回 JSON。

    这个脚本用于快速确认服务是否正常运行。
    它不是单元测试，而是本地冒烟检查。
    """

    url = f"{BASE_URL}{path}"

    try:
        response = httpx.request(
            method=method,
            url=url,
            timeout=5.0,
        )
    except httpx.RequestError as error:
        raise RuntimeError("请求本地服务失败，请先确认 uvicorn 是否已经启动") from error

    if response.status_code != 200:
        raise RuntimeError(
            f"接口返回异常状态码：{response.status_code}，响应内容：{response.text}"
        )

    try:
        data = response.json()
    except ValueError as error:
        raise RuntimeError("接口返回内容不是合法 JSON") from error

    return data


def check_health() -> None:
    """检查健康接口。"""

    data = request_json("GET", "/health")

    if data.get("success") is not True:
        raise RuntimeError("/health 返回 success 不是 true")

    print("[OK] /health")


def check_version() -> None:
    """检查版本接口。"""

    data = request_json("GET", "/api/v1/version")

    if data.get("success") is not True:
        raise RuntimeError("/api/v1/version 返回 success 不是 true")

    print("[OK] /api/v1/version")


def main() -> None:
    """执行本地服务冒烟检查。"""

    check_health()
    check_version()
    print("[OK] 本地服务基础接口检查通过")


if __name__ == "__main__":
    main()
