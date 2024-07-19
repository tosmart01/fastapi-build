# -- coding: utf-8 --
# @Time : 2024/5/15 17:04
# @Author : PinBar
# @File : base_view.py
import inspect
from typing import Union, Type

from fastapi import APIRouter, Depends

from auth.base_authentication import BaseTokenAuthentication
from core.context import g


base_router = APIRouter()


class BaseView:
    authentication_classes = [BaseTokenAuthentication]
    permissions_classes = []

    def __init__(self, path: str = None, tags: list[str] = None, resource_id: str = '_id',
                 query_post_suffix: str = '/list'):
        self.tags = tags or [self.__class__.__name__]
        self.path = path
        self.resource_id = resource_id
        self.query_post_suffix = query_post_suffix
        self.register_routes()

    @property
    def request(self):
        return g.request

    @property
    def user(self):
        return g.user

    @property
    def user_id(self):
        return g.user.id

    def get_dependencies(self, extra_params: dict, method):
        custom_permission_classes = extra_params.pop('permission_classes', None)
        custom_authentication_classes = extra_params.pop('authentication_classes', None)
        authentication_classes = (custom_authentication_classes if custom_authentication_classes is not None
                                  else self.authentication_classes)
        permission_classes = (custom_permission_classes if custom_permission_classes is not None else
                              self.permissions_classes)
        dependencies = [Depends(_(name='')(method)) for _ in authentication_classes] + \
                       [Depends(_(method)) for _ in permission_classes]
        depend_async_session: bool = extra_params.pop("depend_async_session", False)
        if depend_async_session:
            try:
                from db.backends.mysql import get_db
            except ImportError:
                pass
            else:
                dependencies.insert(0, Depends(get_db))
        return dependencies

    def register_routes(self):
        resource_id = "/{" + self.resource_id + "}"
        method_map = {
            "get": {'path': self.path, 'methods': ['GET'], },
            'detail': {'path': self.path + resource_id, 'methods': ['GET']},
            'post': {'path': self.path, 'methods': ['POST'], },
            'query_post': {'path': self.path + self.query_post_suffix, 'methods': ['POST'], },
            'put': {'path': self.path + resource_id, 'methods': ['PUT'], },
            'multi_put': {'path': self.path, 'methods': ['PUT']},
            'delete': {'path': self.path + resource_id, 'methods': ['DELETE'], },
            'multi_delete': {'path': self.path, 'methods': ['DELETE'], },
        }
        for method_name, router_info in method_map.items():
            method = getattr(self, method_name, None)
            if self.is_method_overridden(method_name):
                extra_params = getattr(method, '_extra_params', {})
                dependencies = self.get_dependencies(extra_params, method)
                base_router.add_api_route(router_info['path'], method,
                                          methods=router_info['methods'],
                                          dependencies=dependencies,
                                          tags=self.tags, **extra_params)

    def is_method_overridden(self, method_name: str) -> bool:
        subclass_method = getattr(self, method_name, None)
        base_method = getattr(BaseView, method_name, None)
        if not subclass_method or not base_method:
            return False
        # Check if the method is overridden
        return inspect.getmodule(subclass_method) != inspect.getmodule(base_method)

    @staticmethod
    def message(code: int = 0, message: str = 'success', data: Union[dict, None, list, str] = None):
        return {
            "code": code,
            "message": message,
            "data": data
        }

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


def path(path: str = '/', view_cls: Type[BaseView] = None, tags: list[str] = None, resource_id: str = "_id",
         query_post_suffix: str = '/list', methods: list[str] = None
         ):
    if inspect.isfunction(view_cls):
        return base_router.add_api_route(path, view_cls, methods=methods, tags=tags)
    elif inspect.isclass(view_cls):
        return view_cls(path, tags, resource_id, query_post_suffix)
