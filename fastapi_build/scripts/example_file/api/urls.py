from core.base_view import path
from .demo import DemoView

urlpatterns = [
    path('/demo', DemoView, tags=["demo"]),
]
