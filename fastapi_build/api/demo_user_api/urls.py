from . import APP_NAME
from .view import DemoView
from core.base_view import path

urlpatterns = [
    path('/user', DemoView, tags=[APP_NAME])
]
