'''
Created on Nov 25, 2020

@author: gabez
'''
from celery import Celery
import app.celery_local.config as celery_config


def background_tasks(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    celery.conf.beat_schedule = {
        'score-dns-linux': {
            'task': 'app.celery_local.background_tasks.score_linux_dns',
            'schedule': 30.0,
        }
    }
    app.conf.timezone = 'America/Chicago'

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
