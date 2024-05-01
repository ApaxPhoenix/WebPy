from core import WebPyCore

class WebPyApp:
    def __init__(self):
        self.app = WebPyCore

    def route(self, path):
        return self.app.route(path)

    def run(self, ip='127.0.0.1', port=8085):
        self.app.run(ip=ip, port=port)