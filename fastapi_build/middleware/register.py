# -- coding: utf-8 --
# @Time : 2024/5/16 11:13
# @Author : PinBar
# @File : register.py
import time

from fastapi import Request, FastAPI
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.context import g
from common.log import logger
from exceptions.base import ApiError
from exceptions.http_status import HTTP_400_BAD_REQUEST
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

    @app.exception_handler(ApiError)
    async def custom_exception_handler(request: Request, exc: ApiError):
        return JSONResponse(
            status_code=exc.http_code,
            content={"message": f"{exc.message}", "code": exc.code},
        )

    @app.exception_handler(Exception)
    async def exception_handler(request: Request, exc):
        return JSONResponse(
            status_code=500,
            content={"message": f"{exc}", "code": 500},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        errors = exc.errors()
        model_exc = errors.pop()
        model: BaseModel = model_exc.get('model')
        if not model:
            errors.append(model_exc)
            return JSONResponse(
                status_code=500,
                content={"message": f"{exc}", "code": 500},
            )
        display_error = ""
        for error in errors:
            for name in error['loc']:
                field = model.model_fields.get(name)
                if field is not None:
                    display_field_name = name  # if not field.description else field.description
                    display_error += f"{display_field_name} {error['msg']}"
                    break
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={"message": f"{display_error}", "code": HTTP_400_BAD_REQUEST},
        )

    @app.exception_handler(ResponseValidationError)
    async def response_exception_handler(request, exc):
        errors = exc.errors()
        model_exc = errors.pop()
        model: BaseModel = model_exc.get('model')
        if not model:
            errors.append(model_exc)
            return JSONResponse(
                status_code=500,
                content={"message": f"{exc}", "code": 500},
            )
        display_error = ""
        for error in errors:
            for name in error['loc']:
                field = model.model_fields.get(name)
                if field is not None:
                    display_field_name = name  # if not field.description else field.description
                    display_error += f"{display_field_name} {error['msg']}"
                    break
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={"message": f"{display_error}", "code": HTTP_400_BAD_REQUEST},
        )

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
            # from db.backends.mysql import session
            # session.remove()
        except Exception:
            logger.exception("日志记录异常")
        return response

    app.on_event("startup")(startup)
