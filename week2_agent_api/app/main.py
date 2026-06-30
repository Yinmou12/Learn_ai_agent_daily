from fastapi import FastAPI

from app.api.routes.chat import router as chat_router
from app.api.routes.debug import router as debug_router
from app.api.routes.health import router as health_router
from app.api.routes.version import router as version_router
from app.exception_handlers import app_error_handler
from app.exceptions import AppError


def create_app() -> FastAPI:
    """创建 FastAPI 应用。

    把创建应用、注册异常处理器、注册路由集中在这里。
    这样 main.py 会更像真实项目的启动入口。
    """

    app = FastAPI(
        title="Agent Backend API",
        description="Week2 Agent 后端服务骨架",
        version="0.3.0",
    )

    app.add_exception_handler(AppError, app_error_handler)

    app.include_router(health_router)
    app.include_router(version_router)
    app.include_router(chat_router)
    app.include_router(debug_router)

    return app


app = create_app()
