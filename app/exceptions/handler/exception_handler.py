import logging

from fastapi import Request
from starlette.responses import JSONResponse

from app.exceptions.errors import BusinessFailException, BusinessErrorException
from app.models.result_model import Result


def _error_msg(exc: Exception) -> dict[str, str]:
    """
    生成错误信息

    Args:
        exc: 错误对象
    Return:
        str: 错误信息
    """
    message_key = "error_msg"
    return {message_key: str(exc)}


def _error_log(msg: str, error_url: str) -> str:
    """
    生成错误日志

    Args:
        msg: 错误信息
        error_url: 错误发生的url
    Return:
        str: 错误日志信息
    """
    return f"{msg}|URL--{error_url}|"


async def business_fail_handler(request: Request, exc: BusinessFailException) -> JSONResponse:
    """
    自定义异常处理
    业务失败处理

    Args:
        request: 请求对象
        exc: 错误对象
    Return:
        JSONResponse: 响应对象
    """
    logging.error(f"{_error_log(exc.message, request.url.path)}", exc)

    return JSONResponse(
        status_code=200,
        content=Result.fail(message=exc.message).model_dump()
    )


async def business_error_handler(request: Request, exc: BusinessErrorException) -> JSONResponse:
    """
    自定义异常处理
    业务错误处理

    Args:
        request: 请求对象
        exc: 错误对象
    Return:
        JSONResponse: 响应对象
    """
    logging.error(f"{_error_log(exc.message, request.url.path)}", exc)

    return JSONResponse(
        status_code=exc.code,
        content=Result.error(message=exc.message, data=_error_msg(exc)).model_dump()
    )


async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    全局异常处理，参数校验错误

    Args:
        request: 请求对象
        exc: 错误对象
    Return:
        JSONResponse: 响应对象
    """
    error_msg = "参数错误"
    logging.error(f"{_error_log(error_msg, request.url.path)}", exc)

    return JSONResponse(
        status_code=400,
        content=Result.error(message=error_msg, data=_error_msg(exc)).model_dump()
    )


async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    全局异常处理，未被捕获的全部报错

    Args:
        request: 请求对象
        exc: 异常对象
    Return:
        JSONResponse: 响应对象
    """
    error_msg = "系统异常"
    logging.error(f"{_error_log(error_msg, request.url.path)}", exc)

    return JSONResponse(
        status_code=500,
        content=Result.error(message=error_msg, data=_error_msg(exc)).model_dump()
    )
