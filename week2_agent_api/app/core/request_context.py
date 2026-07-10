from contextvars import ContextVar

request_id_var: ContextVar[str | None] = ContextVar(
    "request_id",
    default=None,
)


def get_request_id() -> str | None:
    """
    获取当前请求的 request_id
    """

    return request_id_var.get()
