from app.http_client import request_get_json

if __name__ == "__main__":
    data = request_get_json(
        "https://httpbin.org/get",
        params={
            "keyword": "ai_agent",
            "page": 1,
        },
        timeout_seconds=20.0,
    )

    print("实际请求 URL:", data["url"])
    print("服务端收到的查询参数:", data["args"])