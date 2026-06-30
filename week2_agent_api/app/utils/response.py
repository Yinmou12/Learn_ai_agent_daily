from app.schemas import ApiResponse, ErrorDetail


def make_success_response(data: object) -> ApiResponse:
    """构造统一成功响应。"""

    return ApiResponse(
        success=True,
        data=data,
        error=None,
    )


def make_error_response(code: str, message: str) -> ApiResponse:
    """构造统一失败响应。"""

    return ApiResponse(
        success=False,
        data=None,
        error=ErrorDetail(
            code=code,
            message=message,
        ),
    )
