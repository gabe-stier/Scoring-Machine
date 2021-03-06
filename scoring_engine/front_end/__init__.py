"""
Scoring machine that is used within a CCDC Competition environment  to be able to know if firewalls are effectively
working
"""
import os
from logging.config import dictConfig

from flask import Flask, render_template, request, url_for

from scoring_engine.front_end import blueprints as bp
from scoring_engine.front_end.database import get_last_score
from scoring_engine.front_end.utilities import Loggers as log, cwd


def app():
	"""Main function of the Flask website"""
	flask_app = Flask(__name__)
	flask_app.config.from_pyfile('/opt/scoring-engine/application.conf')
	flask_app.secret_key = b'tr&6aH+tripRa!rUm9Ju'

	@flask_app.route('/')
	@flask_app.route('/scoring')
	def index():
		"""Returns the basic page"""
		return score_page()

	@flask_app.route('/status-codes')
	def codes():
		"""Returns the status codes page to provide the user with information"""
		url_for('static', filename='base.css')
		url_for('static', filename='info.css')
		return render_template('info.tmpl.j2')

	@flask_app.before_request
	def log_request():
		"""Logs all the requests that the Flask website receives"""
		log.Web.info(
				f'{request.remote_addr} [{request.method}] requested {request.path}')
		url_for('static', filename='favicon.ico')

	def not_found(e):
		"""Returns a not found page if the request is not found"""
		return render_template('not_found.html.j2'), 404

	def internal_error(e):
		"""Internal Error page"""
		log.Error.error(e.get_response())
		return render_template('internal_error.html.j2'), 500

	flask_app.register_error_handler(404, not_found)
	flask_app.register_error_handler(500, internal_error)
	flask_app.register_blueprint(bp.sr)
	flask_app.register_blueprint(bp.config_bp)

	setup_logging()

	return flask_app


def setup_logging():
	"""Sets up the logging for the Flask Website"""
	try:
		os.mkdir('/var/log/scoring-engine', mode=0o666)
	except FileExistsError as e:
		pass
	except Exception as e:
		print('Front End Error \\/', e, sep='\n')
	try:
		os.mkdir('/var/log/scoring-engine/web-page', mode=0o666)

	except FileExistsError as e:
		pass
	except Exception as e:
		print('Front End Error \\/', e, sep='\n')

	dictConfig({
		'version':    1,
		'formatters': {
			'error':   {
				'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
				},
			'default': {
				'format': '[%(asctime)s] %(levelname)s: %(message)s',
				},
			'request': {
				'format': '[%(asctime)s]: REQUEST: %(message)s'
				}
			},
		'handlers':   {
			'default': {
				'class':     'logging.handlers.TimedRotatingFileHandler',
				'formatter': 'default',
				'filename':  os.path.join('/var/log/scoring-engine/web-page', 'full.log'),
				'when':      'midnight'
				},
			'main':    {
				'class':     'logging.handlers.TimedRotatingFileHandler',
				'formatter': 'default',
				'filename':  os.path.join('/var/log/scoring-engine/web-page', 'main.log'),
				'when':      'midnight'
				},
			'scoring': {
				'class':     'logging.handlers.TimedRotatingFileHandler',
				'formatter': 'default',
				'filename':  os.path.join('/var/log/scoring-engine/web-page', 'scoring.log'),
				'when':      'midnight'
				},
			'web':     {
				'class':     'logging.handlers.TimedRotatingFileHandler',
				'formatter': 'default',
				'filename':  os.path.join('/var/log/scoring-engine/web-page', 'web.log'),
				'when':      'midnight'
				},
			'error':   {
				'class':     'logging.handlers.TimedRotatingFileHandler',
				'formatter': 'request',
				'filename':  os.path.join('/var/log/scoring-engine/web-page', 'error.log'),
				'when':      'midnight'
				}
			},
		'loggers':    {
			'':        {
				'level':    'DEBUG',
				'handlers': ['default']
				},
			'main':    {
				'level':    'INFO',
				'handlers': ['main']
				},
			'scoring': {
				'Level':    'INFO',
				'handlers': ['scoring']
				},
			'error':   {
				'level':    'ERROR',
				'handlers': ['error', 'main']
				},
			'web':     {
				'level':    'INFO',
				'handlers': ['main', 'web']
				}
			}
		})


def score_page():
	"""Used to show the current score of the services"""
	url_for('static', filename='base.css')
	url_for('static', filename='index.css')

	def return_bool(item):
		if str(item).lower() == 'false':
			return False
		elif str(item).lower() == 'true':
			return True
		else:
			return None

	try:
		status = get_last_score()[0]
	except Exception as e:
		log.Error.error(e)
	dnsl_srv = return_bool(status[0])
	dnsw_srv = return_bool(status[1])
	ecomm_srv = return_bool(status[2])
	splunk_srv = return_bool(status[3])
	pop3_srv = return_bool(status[4])
	smtp_srv = return_bool(status[5])

	return render_template('index.html.j2', dnsl=dnsl_srv, dnsw=dnsw_srv, ecomm=ecomm_srv, pop3=pop3_srv,
	                       smtp=smtp_srv, splunk=splunk_srv)
