import os
from shutil import copyfile
from threading import Thread
from time import sleep

from scoring_engine import back_end as back
from scoring_engine import front_end as front

from gunicorn.app.base import BaseApplication


def start_server():
    options = {
        'bind': '0.0.0.0:80',
        'workers': 4
    }

    print('Starting Gunicorn')
    print('Starting Back_end Server')
    Thread(target=back.start()).start()
    Thread(target=Gunicorn_Application(app=front.app(), options=options).run()).start()


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
