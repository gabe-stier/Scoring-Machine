'''
Scoring machine that is used with in the cyberrange to be able to know if firewalls are effectively working 
'''
from flask import Flask, render_template, request, url_for
from flask import make_response as respond
from logging.config import dictConfig
from front_end.utilities import Loggers as log
import front_end.blueprints as bp
import os
import sys

def app():
    app = Flask(__name__)
    app.config.from_pyfile('config/application.conf')
    app.secret_key = b'tr&6aH+tripRa!rUm9Ju'

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
    app.register_blueprint(bp.sr)
    app.register_blueprint(bp.config_bp)


    setup_logging(app)

    return app


def setup_logging(app):
    try:
        os.mkdir('/var/log/scoring-machine/web-page', mode=0o666)

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
                'filename': os.path.join('/var/log/scoring-machine/web-page', 'full.log'),
                'when': 'midnight'
            },
            'main': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'formatter': 'default',
                'filename': os.path.join('/var/log/scoring-machine/web-page', 'main.log'),
                'when': 'midnight'
            },
            'scoring': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'formatter': 'default',
                'filename': os.path.join('/var/log/scoring-machine/web-page', 'scoring.log'),
                'when': 'midnight'
            },
            'web': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'formatter': 'default',
                'filename': os.path.join('/var/log/scoring-machine/web-page', 'web.log'),
                'when': 'midnight'
            },
            'error': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'formatter': 'request',
                'filename': os.path.join('/var/log/scoring-machine/web-page', 'error.log'),
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
        # try:
        #     conn = connect()
        #     cur = conn.execute(
        #         f'SELECT * FROM {table} ORDER BY success DESC LIMIT 1;')

        #     for row in cur:
        #         if row[2] == 1:
        #             status = True
        #         elif row[2] == 0:
        #             status = False
        #         else:
        #             status = None
        # except Exception as e:
        #     print(e)
        #     status = None
        # finally:
        #     conn.close()
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

