from celery.schedules import crontab


CELERY_IMPORTS = ('app.celery_local.background_tasks')
CELERY_TASK_RESULT_EXPIRES = 30
CELERY_TIMEZONE = 'America/Chicago'

CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERYBEAT_SCHEDULE = {
    'score-dns-linux': {
        'task': 'app.celery_local.background_tasks.score_linux_dns',
        'schedule': crontab(minute="1", second="30"),
    }
}