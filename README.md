## Fastapi-Build
Read this in [中文(Chinese)](README_CN.md)

## Introduction

`fastapi-build` is a powerful CLI tool designed for scaffolding FastAPI projects. Inspired by Django's administrative features, it allows developers to:

- Quickly set up the basic structure and dependencies of a FastAPI application via the command line.
- Provide support for view classes (Django-style).
- Imitate Django ORM style operations **(simplified version, limited functionality, based on SQLAlchemy)**
- Implement authentication without dependency injection, similar to Django REST framework, with declarative `authentication_classes = []`.
- Utilize a global asynchronous SQLAlchemy session object, e.g., `await g.session.get(Model, id)`.
- Access Flask-like `g` variables, such as `g.request` and `g.user`.
- Return human-readable Pydantic validation errors.

## Installation

Prerequisite： python >=3.9

```shell
$ pip install fastapi-build --index-url=https://pypi.org/sample
```

## Quick Start

### Create a Project with Example APIs
- Create a project via the command line:
```shell
fbuild startproject --all-plugin demo && cd demo/src
```

- Run the project
```shell
python server.py
```

- Example Route
```python
# api/urls.py
from .view import DemoView
from core.base_view import path

urlpatterns = [
    path('/user', DemoView, tags=["demo"]),
]

```
- Example API Interface
```python
from fastapi import Query, Body

from .request_schema import UserCreateModel
from .response_schema import UserItemResponse
from core.decorator import api_description
from core.base_view import BaseView
from models.user import User
from core.response import Res, ListRes
# from auth.authentication import TokenAuthentication

class DemoView(BaseView):
    # authentication_classes = [TokenAuthentication]
    authentication_classes = []

    @api_description(summary="user detail", response_model=Res(UserItemResponse))
    async def detail(self, _id: int):
        user = await User.objects.aget(User.id == _id, raise_not_found=True)
        # user = User.objects.get(User.id == _id, raise_not_found=True)
        return self.response(data=user)

    async def get(
        self,
        page: int = Query(default=1, ge=1),
        per_page: int = Query(default=10, ge=1),
        search: str = Query(default=""),
        sort: str = Query(default=""),
    ) -> ListRes(UserItemResponse):
        total, data = (
            await User.objects.filter(User.nickname == search)
            .order_by(sort)
            .a_pagination(page, per_page)
        )
        # total, data = User.objects.filter(User.nickname==search).order_by(sort).pagination(page, per_page)
        return self.response(data={"total": total, "items": data})

    @api_description(summary="create user", response_model=Res(UserItemResponse))
    async def post(self, body: UserCreateModel):
        user = await User.objects.a_create(**body.model_dump())
        # user = User.objects.create(**body.model_dump())
        return self.response(data=user)

    @api_description(summary="update user")
    async def put(
        self,
        _id: int,
        nickname: str = Body(..., embed=True),
        email: str = Body(..., embed=True),
    ):
        await User.objects.a_update_by_id(
            _id, properties={"nickname": nickname, "email": email}, raise_not_found=True
        )
        # User.objects.update_by_id(_id, properties={'nickname': nickname, 'email': email}, raise_not_found=True)
        return self.response()

    @api_description(summary="delete user")
    def delete(
        self,
    ): ...

    @api_description(summary="multi put")
    def multi_put(
        self,
    ): ...

    @api_description(summary="multi delete")
    def multi_delete(
        self,
    ): ...


```

## Core Features
### Global `g` Variable
- Built-in 
1. g.request,
2. g.user, g.user_id, 
3. g.session(async session), 
4. g.session_sync(sync session)
4. g.extra_data(dict)

```python
from core.context import g
from models import User
from core.decorator import api_description
from core.base_view import BaseView


class DemoView(BaseView):
    @api_description(summary="User query")
    async def get(self, _id):
        # # Get the request object without manual injection
        g.request
        # Get the user, requires declaring `authentication_classes = [TokenAuthentication]` in the view class
        g.user, g.user_id
        # Get the asynchronous session, requires modifying the configuration `config/settings CREATE_DEPENDS_SESSION=1` or declaring `depend_async_session = True` in the view function
        await g.session.get(User, _id)
        # Other parameters
        g.extra_data['name'] = 1
        g.extra_data['name']
```

### Django-like ORM Operations

**Note⚠️：**  This is a simplified version and does not support complex operations like joining tables, foreign key relationships, or querying with underscores (e.g., field__contains).

This project implements a simplified version of Django-like functionality using SQLAlchemy, providing both asynchronous and synchronous APIs for ease of use. It facilitates basic database operations like creating, querying, updating, and deleting records, along with more advanced features such as soft deletion, pagination, and aggregation.



**Core Features**

- Synchronous and Asynchronous Support: The API is compatible with both synchronous and asynchronous operations, making it suitable for various use cases.
- Rich Querying Capabilities: Supports conditional filtering, sorting, pagination, aggregation, and more.
- Create, Update, Delete Operations: Convenient interfaces for object creation, updates, and deletions.
- Soft Delete Support: Easily implement logical deletes using soft delete markers.
- Django-style API: The interface design is intended to closely follow Django's ORM usage patterns.

**Common API List**

- Create: `create()` / `a_create()`
- Query a single object: `get()` / `aget()` / `first()` / `afirst()`
- Query multiple records: `filter()` / `order_by()` / `values()` / `avalues()`
- Update: `update()` / `aupdate()`
- Delete: `delete()` / `adelete()` / `soft_delete()` / `asoft_delete()`
- Pagination: `pagination()` / `a_pagination()`
- Aggregation: `aggregate()`
- Check if record exists: `exists()` / `aexists()`
 
**Example**
```python
from models.base import BaseModel

class User(BaseModel):
    __tablename__ = "user"
    username = Column(String(32))
    # other columns ...

# Query a single object
User.objects.get(User.username == "")
await User.objects.aget(User.username == "")

# Create an object
User.objects.create()
await User.objects.a_create()

# Update an object by ID
User.objects.update_by_id()
await User.objects.a_update_by_id()

# Delete an object by ID
User.objects.delete_by_id()
await User.objects.a_delete_by_id()

# Query multiple records with filtering, ordering, and selecting specific values
User.objects.filter(User.id >= 10, username="test").order_by(User.id.desc()).values(
    User.username
)
await User.objects.filter(User.id >= 10, username="test").order_by(
    User.id.desc()
).avalues(User.username)

# Update multiple records
User.objects.filter(User.id > 10).update(username="test")
await User.objects.filter(User.id > 10).aupdate(username="test")

# Delete multiple records
User.objects.filter(User.id > 10).delete(username="test")
await User.objects.filter(User.id > 10).adelete(username="test")

# Fetch the first record
User.objects.filter(User.id >= 10).first()
await User.objects.filter(User.id >= 10).afirst()

# Fetch all records
User.objects.filter(User.id >= 10).all()
await User.objects.filter(User.id >= 10).a_all()

# Get the last record
User.objects.last()
await User.objects.alast()

# Select specific columns with a limit and filtering
User.objects.with_columns(User.id, User.username).filter(
    User.username.like(f"%test%")
).limit(10).values_list("username", flat=True)

await User.objects.with_columns(User.id, User.username).filter(
    User.username.like(f"%test%")
).limit(10).avalues_list("username", flat=True)

# ... other operations# ... other operations
```

**Native Query Approach in SQLAlchemy**
```python
from sqlalchemy import select

from core.context import g
from dao.base.database_fetch import database
from models.user import User

async def search():
    # Query a list
    query = (
        select(User.id, User.nickname)
        .where(User.nickname.like("%test%"))
        .order_by(User.created_time.desc())
    )
    data = await database.a_fetchall(query, to_dict=False)
    data = database.fetchall(query, to_dict=True)
    
    # Query a single record
    data_first = await database.a_fetchone(query)
    data_first = database.fetchone(query)
    
    # Query count
    await database.a_fetch_count(query)
    database.fetch_count(query)
    
    # Query scalar value
    await database.ascalar(query)
    database.scalar(query)
    
    # Alternatively, you can perform manual queries:
    # Asynchronous
    res = await g.session.execute(query)
    res.scalars().all()
    
    # Synchronous
    res = g.session_sync.execute(query).all()
    g.session_sync.query(User).all()
 
```

### Class-Based Views

- `get`: GET request, performs a query without an ID in the URL path.
- `detail`: GET request, queries based on the ID in the URL path.
- `post`: POST request, used for form submissions.
- `query_post`: POST request, used for complex parameter queries with a POST method.
- `put`: PUT request, updates a resource based on the ID in the URL path.
- `multi_put`: PUT request, performs a bulk update with a request body.
- `delete`: DELETE request, deletes a resource based on the ID in the URL path.
- `multi_delete`: DELETE request, performs a bulk delete with a request body.

```python
class DemoView():
    def get(self, *args, **kwargs):
        raise ImportError("Not implemented")

    def detail(self, *args, **kwargs):
        raise ImportError("Not implemented")

    def post(self, *args, **kwargs):
        raise ImportError("Not implemented")

    def query_post(self, *args, **kwargs):
        raise ImportError("Not implemented")

    def put(self, *args, **kwargs):
        raise ImportError("Not implemented")

    def multi_put(self, *args, **kwargs):
        raise ImportError("Not implemented")

    def delete(self, *args, **kwargs):
        raise ImportError("Not implemented")

    def multi_delete(self, *args, **kwargs):
        raise ImportError("Not implemented")
```

### Globally Accessible Synchronous and Asynchronous Sessions
- **Synchronous session**
```python
from core.context import g
g.session_sync.query()
g.session_sync.add()
...

```
- Asynchronous session
1. Non-injection method (Recommended)
```python
from core.context import g
from core.base_view import BaseView


class DemoView(BaseView):
    async def detail(self, _id: int):
        data = await g.session.query(...)
        return self.response(data=data)
```
2. Injection method

 ```python
from db.database import session_type
from core.base_view import BaseView


class DemoView(BaseView):
    async def detail(self, _id: int, session: session_type):
        data = await session.query(...)
        return self.response(data=data)
```
3. Manual creation method

```python
from db.database import sessionmanager

from core.base_view import BaseView


class DemoView(BaseView):
    async def detail(self, _id: int):
        async with sessionmanager.session() as session:
            await session.add


```

**Note⚠️：** 
- To use the global session variables (g.session, g.session_sync), you must configure CREATE_DEPENDS_SESSION=1, otherwise, each endpoint must declare depend_session=True in the view. The setting is located at: config/settings.py CREATE_DEPENDS_SESSION=1
- Alternatively, you can declare depend_session=True for each endpoint:
```python
@api_description(summary="User Query",  depend_session=True)
async def get(self, _id): 
   ...
```


### Declarative Authentication

1. **Define the Authentication Class**
   - **Both synchronous and asynchronous methods need to be implemented**

```python
from fastapi import Request

from auth.base_authentication import BaseTokenAuthentication
from models import User


class TokenAuthentication(BaseTokenAuthentication):

    async def authenticate(self, request: Request):
        user_info = self.validate_token(request)
        user = await User.objects.aget_by_id(user_info['user_id'])
        # Return the user, can be either a Pydantic or SQLAlchemy object
        return user

    def authenticate_sync(self, request: Request):
        user_info = self.validate_token(request)
        user = User.objects.get_by_id(user_info['user_id'])
        # Return the user, can be either a Pydantic or SQLAlchemy object
        return user
```
2. Declare in the View Class
- If you need to set it globally, modify the authentication_classes in BaseView.
- You can also specify the authentication class for each view function individually using @api_description(authentication_classes=[])
- After authentication, you can access the user either directly in the view function or via the g variable.
```python
from core.context import g
class DemoView(BaseView):
    authentication_classes = [TokenAuthentication, ]

    @api_description(summary="User Detail", response_model=Res(UserItemResponse))
    async def detail(self, _id: int):
        user = User.objects.aget(User.id == _id, raise_not_found=True)
        return self.message(data=user)

    @api_description(summary="User Search", response_model=Res(UserListResponse), authentication_classes=[])
    def get(self, query: UserQueryParams = Depends(UserQueryParams)):
        self.request  # Access the request object directly via self
        self.user     # Directly access the user object
        g.user        # Alternatively, access user via the global g variable
        total, users = User.objects.search(query)
        return self.message(data={'total': total, 'results': users}
```

### Adding Plugins


`fbuild add_plugin `

```shell
$ cd myproject/src
# Current supported plugin list: db, db[database], db[redis], db[es], migrate, all
$ fbuild add_plugin plugin_name
$ fbuild add_plugin 'db[database]'
$ fbuild add_plugin 'db[es]'
$ fbuild add_plugin all
```

#### Available Plugins
- **db**: Provides support for all databases.
- **db[database]**: Provides support for a generic database.
- **db[redis]**: Provides Redis database support.
- **db[es]**: Provides Elasticsearch support.
- **celery**: Provides support for the Celery task queue.
- **migrate**: Provides Alembic migration support, with commands similar to Django's makemigrations and migrate.
- **all**: Installs all available plugins.

#### Other Command Line Options

```shell
$ fbuild --help
Usage: fbuild [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  startproject    Create project folder
  add_plugin      Register a plugin for the application.
  makemigrations  Run the alembic revision, like Django python manage.py makemigrations
  showmigrations  Run the alembic history, like Django python manage.py showmigrations
  migrate         Run the alembic upgrade head, like Django python migrate

```

### Middleware

The project includes built-in middleware for logging API information, tracking request durations, handling CORS (Cross-Origin Resource Sharing), and customizing error response structures.

- **src/middleware/middle.py**

### Configuration Files

The project provides basic configurations for the database, timezone, log file paths, and more. During local development, you can override these settings using the `dev.py` file.

- **src/config/settings.py**

### Log Configuration

**Using loguru to manage logs**

- src/common.log.py

### Error Handling
- Human-readable exception messages
 
![](./docs/asset/img/error.jpg)

- Custom API exceptions
```python
from exceptions.custom_exception import ParamsError
from exceptions.http_status import HTTP_500_INTERNAL_SERVER_ERROR


# Directly use in the API
async def post(request: Request):
    raise ParamsError(message="username must be string")


# The response will be:
# http_code: 400
res: {"code": 400, "message": "username must be string"}

# You can specify the http_code
ParamsError(message="username must be string", http_code=HTTP_500_INTERNAL_SERVER_ERROR)

# You can also create custom error classes
from exceptions.base import ApiError


class ValidatePhoneError(ApiError):
    default_code = ParamCheckError
    default_message = "Please provide a valid phone number"
    default_http_code = HTTP_400_BAD_REQUEST

```

### Start the Project

```shell
cd src
python server.py
```

### Access the API Documentation
- The API documentation is grouped by app name. You can add comments to the API names and parameters.
- The response structure is {"code": 0, "data": [], "message": ""} once it's completed.
  ![apidocs2](./docs/asset/img/api_docs2.png)
  ![apidocs](./docs/asset/img/apidocs.png)


### Project Structure
An overview of the project structure generated by `fastapi-build`:

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

### Contributing Guidelines

Thank you for your interest in contributing to `fastapi-build`! Please follow the steps below to submit your code:

1. Fork this repository
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

### License

This project is licensed under the MIT License. Please see the LICENSE file for more details.
