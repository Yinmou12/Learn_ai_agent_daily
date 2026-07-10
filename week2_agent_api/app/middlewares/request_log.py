import logging
from time import perf_counter
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.request_context import request_id_var

request_logger = logging.getLogger("app.request")
error_logger = logging.getLogger("app.error")


class RequestLogMiddleware(BaseHTTPMiddleware):
    """
    记录每个 HTTP 请求，并为其生成 request_id

    注意：
    不记录 Authorization 请求头。
    不记录用户密码。
    不记录 API Key。
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid4())
        token = request_id_var.set(request_id)

        request.state.request_id = request_id

        start_time = perf_counter()
        method = request.method
        path = request.url.path

        try:
            response = await call_next(request)
        except Exception:
            elapsed_ms = (perf_counter() - start_time) * 1000

            error_logger.exception(
                "request_failed request_id=%s method=%s path=%s elapsed_ms=%.2f",
                request_id,
                method,
                path,
                elapsed_ms,
            )

            # 继续抛出异常，让 FastAPI 的异常处理机制接管。
            raise
        finally:
            request_id_var.reset(token)

        elapsed_ms = (perf_counter() - start_time) * 1000

        request_logger.info(
            "request_finished request_id=%s method=%s path=%s status_code=%s elapsed_ms=%.2f",
            request_id,
            method,
            path,
            response.status_code,
            elapsed_ms,
        )

        response.headers["X-Request-ID"] = request_id

        return response
