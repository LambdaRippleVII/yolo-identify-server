from typing import Optional, Any, TypeVar, Generic

from pydantic import BaseModel, Field

T = TypeVar('T')

class Result(BaseModel, Generic[T]):
    """
    响应结果模型

    Args:
        code: 响应码，成功返回:0;失败返回:1;错误返回对应http响应码
        message: 响应信息
        data: 响应数据
    """
    code: int = Field(default=0, description="响应码，成功返回:0;失败返回:1;错误返回对应http响应码")
    message: str = Field(default="success", description="响应信息")
    data: Optional[T] = Field(default=None, description="响应数据")

    @classmethod
    def success(cls, message: str="成功", data: Optional[T]=None) -> "Result":
        """ 返回成功响应 """
        return cls(code=0, message=message, data=data)

    @classmethod
    def fail(cls, message: str="失败", data: Optional[T]=None) -> "Result":
        """ 返回正常处理失败响应 """
        return cls(code=1, message=message, data=data)

    @classmethod
    def error(cls, code: int=500, message: str="错误", data: Optional[T]=None) -> "Result":
        """ 返回错误响应 """
        return cls(code=code, message=message, data=data)