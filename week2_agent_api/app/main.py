from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.chat import router as chat_router
from app.api.routes.debug import router as debug_router
from app.api.routes.health import router as health_router
from app.api.routes.questions import router as questios_router
from app.api.routes.resumes import router as resumes_router
from app.api.routes.users import router as users_router
from app.api.routes.version import router as version_router
from app.core.logging_config import setup_logging
from app.db.session import init_db
from app.exception_handlers import (
    app_error_handler,
    auth_error_handler,
    not_found_error_handler,
    parameter_error_handler,
    resume_error_handler,
)
from app.exceptions import (
    AppError,
    AuthError,
    NotFoundError,
    ParameterError,
    ResumeParseError,
)
from app.middlewares.request_log import RequestLogMiddleware


def create_app() -> FastAPI:
    """创建 FastAPI 应用。

    把创建应用、注册异常处理器、注册路由集中在这里。
    这样 main.py 会更像真实项目的启动入口。
    """

    setup_logging()

    app = FastAPI(
        title="Agent Backend API",
        description="Week2 Agent 后端服务骨架",
        version="0.5.0",
    )

    app.add_middleware(RequestLogMiddleware)

    init_db()

    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(AuthError, auth_error_handler)
    app.add_exception_handler(NotFoundError, not_found_error_handler)
    app.add_exception_handler(ParameterError, parameter_error_handler)
    app.add_exception_handler(ResumeParseError, resume_error_handler)

    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(chat_router)
    app.include_router(resumes_router)
    app.include_router(questios_router)
    app.include_router(health_router)
    app.include_router(version_router)
    app.include_router(debug_router)

    return app


app = create_app()
