from typing import Any

from gunicorn.app.base import BaseApplication
from gunicorn.util import import_app


class GunicornApplication(BaseApplication):
    def __init__(self, app: str, host: str, port: int, workers: int = 1, **kwargs: Any):
        self.options = {
            "bind": f"{host}:{port}",
            "workers": workers,
            "worker_class": "uvicorn.workers.UvicornWorker",
            **kwargs,
        }
        self.application = app
        super().__init__()

    def load_config(self):
        for key, value in self.options.items():
            if key in self.cfg.settings and value is not None:
                self.cfg.set(key.lower(), value)

    def load(self):
        return import_app(self.application)
