## 目录

1. [简介](#简介)
2. [安装](#安装)
3. [快速开始](#快速开始)
   - [创建新项目](#创建新项目)
   - [创建新应用](#创建新应用)
   - [添加插件](#添加插件)
     - [可用插件](#可用插件)
   - [其他命令行](#其他命令行)
4. [运行项目](#运行项目)
5. [基于类的视图](#基于类的视图)
5. [同步异步session](#同步异步session)
7. [全局g变量](#全局g变量)
8. [仿Django ORM 操作](#仿django-orm-操作)
9. [声明式身份验证](#声明式身份验证)
10. [中间件](#中间件)
11. [配置文件](#配置文件)
12. [日志配置](#日志配置)
13. [错误处理](#错误处理)
14. [启动项目](#启动项目)
15. [访问接口文档](#访问接口文档)
16. [项目结构](#项目结构)

## 简介

`fastapi-build` 是一个强大的 CLI 工具，用于搭建 FastAPI 项目脚手架。受 Django 管理功能的启发，它允许开发者：

- 命令行快速设置 FastAPI 应用程序的基本结构和依赖项。
- 提供视图类支持
- 全局的异步sqlalchemy session 对象，await g.session.get(Model, id)
- 不依赖注入的身份验证，类似djangorestframework 声明式, authentication_classes = []
- 仿flask的g变量，g.request, g.user
- 仿Django ORM风格操作
- 自定义错误处理等集成

## 安装

必要条件： python >=3.9

```shell
$ pip install fastapi-build --index-url=https://pypi.org/sample
```

## 快速开始

### 创建新项目

`fbuild startproject`

```shell
$ fbuild startproject myproject

# 也可以使用 --example-api 添加demo接口示例
$ fbuild startproject --example-api myproject
```

### 创建新应用

`fbuild startapp`

```shell
$ cd myproject/src
$ fbuild startapp myapp
```

### 添加插件

`fbuild add_plugin `

```shell
$ cd myproject/src
# 当前支持 插件列表 db, db[mysql], db[redis], db[es], migrate, all
$ fbuild add_plugin plugin_name
```

#### 可用插件

- **db**: 提供所有数据库支持
- **db[mysql]**: 提供 MySQL 数据库支持
- **db[redis]**: 提供 Redis 数据库支持
- **db[es]**: 提供 Elasticsearch 支持
- **celery**: 提供 Celery 任务队列支持
- **migrate**: 提供alembic 迁移支持，命令仿照Django makemigrations migrate
- **all**: 安装所有插件

#### 其他命令行

```shell
$ fbuild --help
Usage: fbuild [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  startproject    Create project folder
  startapp        To create the app, you need to navigate to the...
  add_plugin      Register a plugin for the application.
  makemigrations  Run the alembic revision, like Django python manage.py makemigrations
  showmigrations  Run the alembic history, like Django python manage.py showmigrations
  migrate         Run the alembic upgrade head, like Django python migrate


```

## 运行项目

```
$ cd src
$ python server.py
INFO:     Started server process [70055]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:6100 (Press CTRL+C to quit)


```

访问 http://127.0.0.1:6100/docs 查看文档

## 基于类的视图

1. 创建app: fbuild startapp example_api
2. 编辑 api/example_api/urls.py

```python
from . import APP_NAME
from core.base_view import path
from .example_view import ExampleView

urlpatterns = [
    path('/test', ExampleView, tags=[APP_NAME])
]
```

3. 编写视图类
   api/example_api/view.py
   目前支持在 视图类中复写以下函数

- get, get请求，get查询,不带路径id
- detail, get请求,根据路径id查询
- post, post请求，表单提交
- query_post, post请求，用于复杂参数的post方式查询
- put, put请求，根据路径id的表单更新
- multi_put, put请求，带请求体批量更新
- delete, delete请求, 根据路径id的删除请求
- multi_delete, delete请求，带请求体的批量删除

```python
from fastapi import Depends

from .request_schema import UserQueryParams, UserCreateModel, UserLoginModel, UserLoginResponseModel
from .response_schema import UserListResponse, UserItemResponse
from core.decorator import api_description
from core.base_view import BaseView
from db.models.user import User
from core.response import Res
from core.context import g
from auth.authentication import TokenAuthentication


class DemoView(BaseView):
    authentication_classes = [TokenAuthentication, ]

    @api_description(summary="用户详情", response_model=Res(UserItemResponse), depend_async_session=True)
    def detail(self, _id: int):
        user = User.objects.get(User.id == _id, raise_not_found=True)
        return self.message(data=user)

    @api_description(summary="用户查询", response_model=Res(UserListResponse), depend_async_session=True)
    async def get(self, query: UserQueryParams = Depends(UserQueryParams)):
        self.request  # request对象直接通过self获取
        self.user  # 直接获取user对象
        g.session # 获取async session对象
        total, users = await User.objects.search(query)
        return self.message(data={'total': total, 'results': users}
```
## 同步异步session
- 同步 session
```python
from db.backends.mysql import session
session.query()
session.add()
```
- 异步session
1. 非注入方式
```python
from core.context import g
async def create_user():
    g.session.add()

@api_description(summary="用户查询",  depend_async_session=True)
async def get(self, _id):
    await g.session.add()
    await create_user()
```
2. 注入方式
 ```python
from db.backends.mysql import async_session
@api_description(summary="用户查询")
async def get(self, _id, session: async_session):
    await session.add()
```
3. 手动创建方式
```python
from db.backends.mysql import sessionmanager
@api_description(summary="用户查询")
async def get(self, _id):
    async with sessionmanager.session() as session:
        await session.add

```
## 全局g变量
- 内置 
1. g.request,
2. g.user, g.user_id, 
3. g.session(异步session), 
4. g.extra_data(字典)

```python
from core.context import g
from db.models.user import User
from core.decorator import api_description

@api_description(summary="用户查询",  depend_async_session=True)
async def get(self, _id):
    # 获取request对象，不依赖手动注入
    g.request
    # 获取user，需要在视图类中声明 authentication_classes = [TokenAuthentication, ]
    g.user, g.user_id
    # 获取 异步session, 需要在视图函数中声明 depend_async_session = True
    await g.session.get(User, _id)
    # 其他参数
    g.extra_data['name'] = 1
    g.extra_data['name']
```

## 仿Django ORM 操作

### 类似 Django 的 ORM

提供的类似 Django 的 ORM 操作的有限集成，例如:

```python
from db.models.base import BaseModel


class User(BaseModel):
    __tablename__ = 'user'
    username = Column(String(32))
    # you column ...


User.objects.get()
await User.objects.aget()

User.objects.get_by_ids(to_dict=True)
await User.objects.aget_by_ids(to_dict=True)

User.objects.create()
await User.objects.a_create()

User.objects.update_by_id()
await User.objects.a_update_by_id()
# ...等其他操作
```
## 声明式身份验证
1. 定义身份验证类
 - **需要实现同步异步两个方法**
```python
from fastapi import Request

from auth.base_authentication import BaseTokenAuthentication
from db.models.user import User


class TokenAuthentication(BaseTokenAuthentication):

    async def authenticate(self, request: Request):
        user_info = self.validate_token(request)
        user = await User.objects.aget_by_id(user_info['user_id'])
        # 需要返回 user，可以是 pydantic 对象，可以是 sqlalchemy对象
        return user

    def authenticate_sync(self, request: Request):
        user_info = self.validate_token(request)
        user = User.objects.get_by_id(user_info['user_id'])
        # 需要返回 user，可以是 pydantic 对象，可以是 sqlalchemy对象
        return user
```
2. 视图类中声明
- 如果需要全局设置，可以修改BaseView  authentication_classes
- 可以为每个视图函数单独指定验证类, @api_description(authentication_classes=[])
- 通过验证后可以在 视图函数或者g变量中访问 user
```python
from core.context import g
class DemoView(BaseView):
    authentication_classes = [TokenAuthentication, ]

    @api_description(summary="用户详情", response_model=Res(UserItemResponse))
    async def detail(self, _id: int):
        user = User.objects.aget(User.id == _id, raise_not_found=True)
        return self.message(data=user)

    @api_description(summary="用户查询", response_model=Res(UserListResponse), authentication_classes=[])
    def get(self, query: UserQueryParams = Depends(UserQueryParams)):
        self.request  # request对象直接通过self获取
        self.user  # 直接获取user对象
        g.user 
        total, users = User.objects.search(query)
        return self.message(data={'total': total, 'results': users}
```

## 中间件

内置了接口信息打印，访问时长记录，跨域CORS，自定义错误返回结构等。

- src/middleware/middle.py

## 配置文件

提供了基础的数据库，时区，日志路径等配置,本地开发可以使用 dev.py 覆盖配置

- src/config/settings.py

## 日志配置

**使用loguru管理日志**

- src/common.log.py

## 错误处理

```python
from exceptions.custom_exception import ParamsError
from exceptions.http_status import HTTP_500_INTERNAL_SERVER_ERROR


# 接口中直接使用
async def post(request: Request):
    raise ParamsError(message="username must be string")


# 将返回：
# http_code: 400
res: {"code": 400, "message": "username must be string"}

# 可指定 http_code
ParamsError(message="username must be string", http_code=HTTP_500_INTERNAL_SERVER_ERROR)

# 可自定义错误类
from exceptions.base import ApiError


class ValidatePhoneError(ApiError):
    default_code = ParamCheckError
    default_message = "请输出正确的手机号"
    default_http_code = HTTP_400_BAD_REQUEST

```

## 启动项目

```shell
cd src
python server.py
```

## 访问接口文档

- 根据app名称分组，接口名称及参数可添加注释，
- 返回结构为 {"code": 0, "data": [], "message": ""} 制作完成
  ![apidocs2](./docs/asset/img/api_docs2.png)
  ![apidocs](./docs/asset/img/apidocs.png)

## 项目结构

由 `fastapi-build` 生成的项目结构概览。

```
├── README.md
├── build
│   ├── Dockerfile
│   └── docker_build.sh
├── requirements.txt
└── src
    ├── api
    │   ├── __init__.py
    │   └── demo
    │       ├── __init__.py
    │       ├── request_schema.py
    │       ├── response_schema.py
    │       ├── urls.py
    │       └── view.py
    ├── auth
    │   ├── __init__.py
    │   ├── authentication.py
    │   ├── base_authentication.py
    │   ├── base_permission.py
    │   └── hashers.py
    ├── common
    │   ├── __init__.py
    │   ├── load_model.py
    │   ├── log.py
    │   └── patch
    │       ├── __init__.py
    │       └── fastapi_patch.py
    ├── config
    │   ├── __init__.py
    │   ├── dev.py
    │   └── settings.py
    ├── core
    │   ├── __init__.py
    │   ├── base_params.py
    │   ├── base_view.py
    │   ├── context.py
    │   ├── decorator.py
    │   └── response.py
    ├── dao
    │   ├── __init__.py
    │   ├── base.py
    │   └── sql_tools.py
    ├── db
    │   ├── backends
    │   │   ├── __init__.py
    │   │   ├── es.py
    │   │   ├── mysql.py
    │   │   └── redis_client.py
    │   └── models
    │       ├── __init__.py
    │       └── base.py
    ├── exceptions
    │   ├── __init__.py
    │   ├── base.py
    │   ├── custom_exception.py
    │   ├── error_code.py
    │   └── http_status.py
    ├── gunicorn_conf.py
    ├── middleware
    │   ├── __init__.py
    │   └── register.py
    └── server.py
```

## 贡献指南

感谢你对 `fastapi-build` 的贡献！请遵循以下步骤提交你的代码：

1. Fork 此仓库
2. 创建你的特性分支 (`git checkout -b feature/fooBar`)
3. 提交你的更改 (`git commit -am 'Add some fooBar'`)
4. 推送到分支 (`git push origin feature/fooBar`)
5. 创建一个新的 Pull Request

## 许可证

此项目使用 MIT 许可证，详情请参阅 LICENSE 文件。
