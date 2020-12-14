'''
Scoring machine that is used with in the cyberrange to be able to know if firewalls are effectively working 
'''
from flask import Flask, render_template, request, url_for
from flask import make_response as respond
from app.utilities import Loggers as log
import app.background_tasks as bg
from logging.config import dictConfig
from app.blueprints import sr as score_request
from app.blueprints import config_bp as configuration_bp
from app.sqlite_connection import init_db, connect
import app.scoring_functions as score
import os
import sys
from redis import Redis
from celery_task import background_tasks as bgt

def app():
    app = Flask(__name__)
    app.config.from_pyfile('app/config/application.conf')
    # app.redis = Redis.from_url('redis://localhost:6379')
    # app.task_queue = rq.Queue('scoring-tasks', connection=app.redis)
    bg.rq.init_app(app)
    app.secret_key = b'tr&6aH+tripRa!rUm9Ju'
    celery = bgt(app)

    ''' HTML Pages '''
    @app.route('/')
    @app.route('/scoring')
    def index():
        return score_page()

    @app.before_request
    def log_request():
        log.Web.info(
            f'{request.remote_addr} [{request.method}] requested {request.path}')
        url_for('static', filename='favicon.ico')

    def not_found(e):
        return render_template('not_found.html.j2'), 404

    def internal_error(e):
        print(e)
        log.Error.error(e.get_response())
        return render_template('internal_error.html.j2'), 500

    app.register_error_handler(404, not_found)
    app.register_error_handler(500, internal_error)

    app.register_blueprint(score_request)
    app.register_blueprint(configuration_bp)

    setup_logging(app)
    init_db()
    score.set_service_config()
    start_scoring()

    return app


def setup_logging(app):
    try:
        os.mkdir(app.config['LOG_LOCATION'], mode=0o666)
        os.mkdir(os.path.join(
            app.config['LOG_LOCATION'], 'logs'), mode=0o666)

    except FileExistsError as e:
        pass
    except Exception as e:
        print(e)

    dictConfig({
        'version': 1,
        'formatters': {
            'error': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            },
            'default': {
                'format': '[%(asctime)s] %(levelname)s: %(message)s',
            },
            'request': {
                'format': '[%(asctime)s]: REQUEST: %(message)s'
            }
        },
        'handlers': {
            'default': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'formatter': 'default',
                'filename': os.path.join(app.config['LOG_LOCATION'], 'full.log'),
                'when': 'midnight'
            },
            'main': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'formatter': 'default',
                'filename': os.path.join(app.config['LOG_LOCATION'], 'main.log'),
                'when': 'midnight'
            },
            'scoring': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'formatter': 'default',
                'filename': os.path.join(app.config['LOG_LOCATION'], 'scoring.log'),
                'when': 'midnight'
            },
            'web': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'formatter': 'default',
                'filename': os.path.join(app.config['LOG_LOCATION'], 'web.log'),
                'when': 'midnight'
            },
            'error': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'formatter': 'request',
                'filename': os.path.join(app.config['LOG_LOCATION'], 'error.log'),
                'when': 'midnight'
            }
        },
        'loggers': {
            '': {
                'level': 'DEBUG',
                'handlers': ['default']
            },
            'main': {
                'level': 'INFO',
                'handlers': ['main']
            },
            'scoring': {
                'Level': 'INFO',
                'handlers': ['scoring']
            },
            'error': {
                'level': 'ERROR',
                'handlers': ['error', 'main']
            },
            'web': {
                'level': 'INFO',
                'handlers': ['main', 'web']}
        }
    })


def score_page():
    url_for('static', filename='base.css')
    url_for('static', filename='index.css')

    def get_success(table):
        status = None
        try:
            conn = connect()
            cur = conn.execute(
                f'SELECT * FROM {table} ORDER BY success DESC LIMIT 1;')

            for row in cur:
                if row[2] == 1:
                    status = True
                elif row[2] == 0:
                    status = False
                else:
                    status = None
        except Exception as e:
            print(e)
            status = None
        finally:
            conn.close()
            return status

    ldap_srv = get_success('ldap')
    dnsl_srv = get_success('dns_linux')
    dnsw_srv = get_success('dns_windows')
    ecomm_srv = get_success('ecomm')
    pop3_srv = get_success('pop3')
    smtp_srv = get_success('smtp')
    splunk_srv = get_success('splunk')

    return render_template('index.html.j2', ldap=ldap_srv, dnsl=dnsl_srv, dnsw=dnsw_srv, ecomm=ecomm_srv,
                           pop3=pop3_srv, smtp=smtp_srv, splunk=splunk_srv)


def start_scoring():
    test = bg.score_ecomm.queue()
    print(test, flush=True)
    bg.score_ecomm.cron('2 * * * *', 'score-ecomm', timeout=60)
    bg.score_ldap.cron('2 * * * *', 'score-ldap', timeout=60)
    bg.score_linux_dns.cron('2 * * * *', 'score-ldns', timeout=60)
    bg.score_pop3.cron('2 * * * *', 'score-pop3', timeout=60)
    bg.score_smtp.cron('2 * * * *', 'score-smtp', timeout=60)
    bg.score_splunk.cron('2 * * * *', 'score-splunk', timeout=60)
    bg.score_windows_dns.cron('2 * * * *', 'score-wdns', timeout=60)

