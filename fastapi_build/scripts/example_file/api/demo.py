from core.base_view import BaseView


class DemoView(BaseView):
    authentication_classes = []

    def get(self):
        return self.response(message="hello world")
