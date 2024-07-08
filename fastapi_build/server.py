# -- coding: utf-8 --
# @Time : 2024/5/15 16:56
# @Author : PinBar
# @File : server.py
from fastapi import FastAPI

from core.base_view import base_router
from common.load_model import import_api_module
from middleware.register import register_middleware


def create_app() -> FastAPI:
    app = FastAPI()
    import_api_module('api')
    import_api_module('db.models')
    from db.models.base import create_tables
    create_tables()
    app.include_router(base_router, prefix='/api', )
    register_middleware(app)
    from common import patch

    return app


app = create_app()

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='127.0.0.1', port=6100)
