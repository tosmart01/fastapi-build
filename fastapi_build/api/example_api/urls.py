from . import APP_NAME
from core.base_view import path
from .example_view import ExampleView


urlpatterns = [
    path('/test', ExampleView, tags=[APP_NAME])
]