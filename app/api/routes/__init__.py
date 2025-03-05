# 路由包初始化文件
from app.api.routes.auth import router as auth_router
from app.api.routes.openai import router as openai_router

__all__ = ["auth", "openai"]