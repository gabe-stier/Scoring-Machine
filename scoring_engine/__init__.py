# import scoring_engine.back_end as back
# import scoring_engine.front_end as front
from gunicorn.app.base import BaseApplication
import os
import platform

def start_server():
    print(os.getcwd(), flush=True)
    if platform.system().lower() == 'linux':
        
    # Gunicorn_Application(app=front.app(), options=None).run()
    # back.start()
    


class Gunicorn_Application(BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application
