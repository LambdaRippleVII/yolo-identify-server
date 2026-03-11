import logging
import sys

from loguru import logger

# 日志过滤列表
FILTER_MODULES = {
    "websockets.legacy.server": logging.DEBUG,
    "websockets.legacy.protocol": logging.DEBUG
}

class LoggingInterceptor(logging.Handler):
    """
    日志拦截器类
    继承自logging.Handler，用于拦截日志并执行自定义操作
    """

    def __init__(self, level=logging.NOTSET):
        super().__init__(level)

    def emit(self, record):
        # 获取 loguru 对应的日志等级
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        # 找到原始调用位置（跳过 logging 内部帧）
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def logger_level_filter(record):
    """
    自定义过滤器
    """
    logger_name = record["name"]
    level_no = record["level"].no

    if logger_name in FILTER_MODULES.keys() and level_no <= FILTER_MODULES[logger_name]:
        return False
    return True


def setup_logger():
    # 移除默认的 handler（避免重复输出）
    logger.remove()

    # 控制台输出（带颜色）
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        level="DEBUG",
        colorize=True,
        filter=logger_level_filter
    )

    # 拦截 Uvicorn 和 Gunicorn 的日志
    interceptor = LoggingInterceptor()
    interceptor.setLevel(logging.DEBUG)

    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.handlers = [interceptor]
    uvicorn_logger.setLevel(logging.DEBUG)
    uvicorn_logger.propagate = False

    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_access_logger.handlers = [interceptor]
    uvicorn_access_logger.setLevel(logging.DEBUG)
    uvicorn_access_logger.propagate = False

    uvicorn_error_logger = logging.getLogger("uvicorn.error")
    uvicorn_error_logger.handlers = [interceptor]
    uvicorn_error_logger.setLevel(logging.DEBUG)
    uvicorn_error_logger.propagate = False
