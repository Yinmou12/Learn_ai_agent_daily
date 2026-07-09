from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions import (
    AppError,
    AuthError,
    NotFoundError,
    ParameterError,
)
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


async def auth_error_handler(request: Request, error: AuthError) -> JSONResponse:
    """
    统一处理认证异常
    """
    response = make_error_response(
        code=error.__class__.__name__,
        message=str(error),
    )

    return JSONResponse(
        status_code=401,
        content=response.model_dump(),
    )


async def not_found_error_handler(
    request: Request, error: NotFoundError
) -> JSONResponse:
    """
    统一处理资源不存在异常
    """
    response = make_error_response(
        code=error.__class__.__name__,
        message=str(error),
    )

    return JSONResponse(status_code=404, content=response.model_dump())


async def parameter_error_handler(
    request: Request, error: ParameterError
) -> JSONResponse:
    """
    统一处理用户传参错误异常
    """

    response = make_error_response(
        code=error.__class__.__name__,
        message=str(error),
    )

    return JSONResponse(
        status_code=422,
        content=response.model_dump(),
    )
