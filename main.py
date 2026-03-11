# 初始化日志配置
from app.config import setup_logger
setup_logger()

# 创建FastApi应用实例
from app.core import lifespan
from app.core import settings
from fastapi import FastAPI

app = FastAPI(
    title=settings.SERVER_TITLE,
    version=settings.SERVER_VERSION,
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL,
    openapi_url=settings.OPENAPI_URL,
    lifespan=lifespan,
)

# == 添加路由 ==
from app.api.api_main import api_router
app.include_router(api_router)

# == 设置配置项 ==
from app.config import setup_exception_handler
# 异常处理
setup_exception_handler(app)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host=settings.SERVER_HOST, port=settings.SERVER_PORT, log_config=None)