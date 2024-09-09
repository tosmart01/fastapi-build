# -- coding: utf-8 --
# @Time : 2024/5/16 11:13
# @Author : PinBar
# @File : middle.py
import time

from fastapi import Request, FastAPI
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
from starlette.middleware.base import BaseHTTPMiddleware

from core.context import g
from common.log import logger
from exceptions.base import ApiError
from exceptions.error_code import ParamCheckError
from exceptions.http_status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from middleware.startup import startup


def register_middleware(app: FastAPI):
    origins = [
        "*"
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    def human_errors(exc: ValidationError) -> str:
        errors = exc.errors()
        for error in errors:
            loc = list(error.get('loc', []))
            loc_len = len(loc)
            msg = error.get('msg')
            error_type = error.get('type')
            if error_type == 'json_invalid':
                return msg
            if loc_len == 1:
                text = f"Field {loc[0]} error: {msg}"
                return text
            if loc_len == 2:
                text = "Field "
                if isinstance(loc[1], int):
                    text += f"{loc[0]}[{loc[1]}]"
                if isinstance(loc[1], str):
                    text += f"`{loc[1]}`"
                text += ' error: ' + msg
                return text
            if loc_len > 2:
                key_field = None
                if loc[-1] == "[key]":
                    key_field = loc.pop()
                text = "Field "
                for ix, field in enumerate(loc[1:]):
                    if isinstance(field, str):
                        if ix == 0:
                            text += field
                        else:
                            text += f"['{field}']"
                    if isinstance(field, int):
                        text += f"[{field}]"
                if key_field:
                    text += f" the value '{loc[-1]}'"
                    text += ' ' + msg
                else:
                    text += ' error: ' + msg
                return text
        return str(errors)

    @app.exception_handler(ApiError)
    async def custom_exception_handler(request: Request, exc: ApiError):
        return JSONResponse(
            status_code=exc.http_code,
            content={"message": f"{exc.message}", "code": exc.code},
        )

    @app.exception_handler(Exception)
    async def exception_handler(request: Request, exc):
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": f"{exc}", "code": HTTP_500_INTERNAL_SERVER_ERROR},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        try:
            human_err = human_errors(exc)
        except Exception:
            logger.warning(f"format error fail:")
            return JSONResponse(status_code=HTTP_400_BAD_REQUEST,
                                content={"message": str(exc), "code": ParamCheckError})
        return JSONResponse(status_code=HTTP_400_BAD_REQUEST, content={"message": human_err, "code": ParamCheckError})

    @app.exception_handler(ResponseValidationError)
    async def response_exception_handler(request, exc):
        try:
            human_err = human_errors(exc)
        except Exception:
            logger.warning(f"format error fail:")
            return JSONResponse(status_code=HTTP_400_BAD_REQUEST,
                                content={"message": str(exc), "code": ParamCheckError})
        return JSONResponse(status_code=HTTP_400_BAD_REQUEST, content={"message": human_err, "code": ParamCheckError})

    @app.middleware("http")
    async def common_requests(request: Request, call_next):
        # 记录请求开始时间
        start_time = time.time()

        # 获取请求信息
        method = request.method
        url = str(request.url.path)
        client_ip = request.client.host
        client_agent = request.headers.get("user-agent")
        query_params = dict(request.query_params)
        request_body = await request.body()
        g.request = request
        g.extra_data = {}
        # 处理请求
        try:
            response = await call_next(request)
        except Exception:
            logger.exception(f"接口异常{url=}")
            raise

        # 计算请求处理时间
        duration = time.time() - start_time

        # 记录日志
        try:
            logger.info(
                f"{method}: {url}, 用时: {duration:.4f}s, Query Params: {query_params},"
                f" Body: {request_body.decode()} IP: {client_ip}, Agent: {client_agent}. ")
        except Exception:
            logger.exception("日志记录异常")
        return response

    app.on_event("startup")(startup)
