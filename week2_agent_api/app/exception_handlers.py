from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions import AppError
from app.utils.response import make_error_response


async def app_error_handler(request: Request, error: AppError) -> JSONResponse:
    """
    统一处理应用内可预期异常。

    只要业务代码中 raise AppError 或它的子类，
    FastAPI 就会自动调用这个函数构造错误响应。
    """

    response = make_error_response(
        code=error.__class__.__name__,
        message=str(error),
    )

    return JSONResponse(
        status_code=400,
        content=response.model_dump(),
    )
