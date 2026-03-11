from fastapi import FastAPI

from app.exceptions.errors import BusinessFailException, BusinessErrorException
from app.exceptions.handler import exception_handler, validation_exception_handler, business_error_handler, business_fail_handler


def setup_exception_handler(app: FastAPI):
    """
    配置应用程序的异常处理器

    Args:
        app (FastAPI): FastAPI应用实例
    """

    # 全局异常处理
    app.add_exception_handler(Exception, exception_handler)
    # 参数校验异常处理
    app.add_exception_handler(ValueError, validation_exception_handler)

    # == 自定义异常处理 ==
    # 业务处理失败处理
    app.add_exception_handler(BusinessFailException, business_fail_handler)
    # 业务处理错误处理
    app.add_exception_handler(BusinessErrorException, business_error_handler)
