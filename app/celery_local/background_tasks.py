
# from app.celery_task import background_tasks
import app.scoring_functions as score
import celery


''' Background tasks '''


@celery.task
def score_windows_dns():
    score.Windows_DNS.score()


@celery.task
def score_linux_dns():
    score.Linux_DNS.score()


@celery.task
def score_ldap():
    score.LDAP.score()


@celery.task
def score_ecomm():
    score.Ecommerce.score()


@celery.task
def score_splunk():
    score.Splunk.score()


@celery.task
def score_pop3():
    score.POP3.score()


@celery.task
def score_smtp():
    score.SMTP.score()
