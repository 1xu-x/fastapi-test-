"""
为全局异常处理器:将所有未捕获异常转为500 JSON响应
"""
from fastapi import Request
from fastapi.responses import JSONResponse
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message":"服务器内部错误","detail":str(exc)},
    )