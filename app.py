from core import WebPyCore


class WebPyApp:
    def __init__(self):
        self.app = WebPyCore

    def route(self, path, methods=None):
        """Decorator to register routes"""
        if methods is None:
            methods = ['GET']

        def decorator(handler):
            self.app.route(path, methods)(handler)
            return handler
        return decorator

    def run(self, ip='127.0.0.1', port=8080):
        self.app.run(ip=ip, port=port)
