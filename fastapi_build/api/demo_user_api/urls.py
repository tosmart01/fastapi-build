from . import APP_NAME
from .view import DemoView, LoginView
from core.base_view import path

urlpatterns = [
    path('/user', DemoView, tags=[APP_NAME]),
    path('/login', LoginView, tags=[APP_NAME])
]
