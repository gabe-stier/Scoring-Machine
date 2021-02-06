"""
Created on Nov 26, 2020

@author: gabez
"""
import json

import requests
from flask import (
	Blueprint, current_app, make_response, redirect,
	render_template, request, session, url_for)
from flask.views import MethodView

from scoring_engine.front_end.database import get_last_score
from scoring_engine.front_end.utilities import Loggers as log, Token

token = Token()

sr = Blueprint('score', __name__, url_prefix='/request-score')


@sr.route('/')
def score_page():
	"""Shows a score page. General was going to be used to how charts of the past 5 scores but decided against that.\n
	If someone wants to take over that. You can. Just start creating!"""
	url_for('static', filename='base.css')
	url_for('static', filename='index.css')
	url_for('static', filename='scoring.css')

	def return_bool(item):
		if str(item).lower() == 'false':
			return False
		elif str(item).lower() == 'true':
			return True
		else:
			return None

	try:
		status = get_last_score()
	except Exception as e:
		log.Error.error(e)
	status = status[0]
	dnsl_srv = return_bool(status[0])
	dnsw_srv = return_bool(status[1])
	ecomm_srv = return_bool(status[2])
	splunk_srv = return_bool(status[3])
	pop3_srv = return_bool(status[4])
	smtp_srv = return_bool(status[5])

	return make_response(
			render_template('scoring.html.j2',dnsl=dnsl_srv, dnsw=dnsw_srv, ecomm=ecomm_srv,
			                pop3=pop3_srv,
			                smtp=smtp_srv, splunk=splunk_srv))


class Score_Ecomm(MethodView):
	"""Controls the score request for Ecomm"""

	def post(self):
		forward = {
			'action': 'score',
			"data":   {
				"service": "ecomm"
				}
			}
		status = send_post(forward)
		if status[0] == 500:
			return render_template('internal_error.html.j2'), 500
		elif not (status[0] == 20 or status[0] == 22):
			return redirect(url_for('score_page', status=status[0], info=status[1]))
		return redirect(request.referrer)


class Score_DNS_Windows(MethodView):
	"""Controls the score request for Windows DNS"""

	def post(self):
		forward = {
			'action': 'score',
			"data":   {
				"service": "dns",
				'machine': 'windows'
				}
			}
		status = send_post(forward)
		if status[0] == 500:
			return render_template('internal_error.html.j2'), 500
		elif not (status[0] == 20 or status[0] == 22):
			return redirect(url_for('score_page', status=status[0], info=status[1]))
		return redirect(request.referrer)


class Score_DNS_Linux(MethodView):
	"""Controls the score request for Linux DNS"""

	def post(self):
		forward = {
			'action': 'score',
			"data":   {
				"service": "dns",
				"machine": "linux"
				}
			}
		status = send_post(forward)
		if status[0] == 500:
			return render_template('internal_error.html.j2'), 500
		elif not (status[0] == 20 or status[0] == 22):
			return redirect(url_for('score_page', status=status[0], info=status[1]))
		return redirect(request.referrer)


class Score_POP3(MethodView):
	"""Controls the score request for POP3"""

	def post(self):
		forward = {
			'action': 'score',
			"data":   {
				"service": "pop3"
				}
			}
		status = send_post(forward)
		if status[0] == 500:
			return render_template('internal_error.html.j2'), 500
		elif not (status[0] == 20 or status[0] == 22):
			return redirect(url_for('score_page', status=status[0], info=status[1]))
		return redirect(request.referrer)


class Score_SMTP(MethodView):
	"""Controls the score request for SMTP"""

	def post(self):
		forward = {
			'action': 'score',
			"data":   {
				"service": "smtp"
				}
			}
		status = send_post(forward)
		if status[0] == 500:
			return render_template('internal_error.html.j2'), 500
		elif not (status[0] == 20 or status[0] == 22):
			return redirect(url_for('score_page', status=status[0], info=status[1]))
		return redirect(request.referrer)


class Score_Splunk(MethodView):
	"""Controls the score request for Splunk"""

	def post(self):
		forward = {
			'action': 'score',
			"data":   {
				"service": "splunk"
				}
			}
		status = send_post(forward)
		if status[0] == 500:
			return render_template('internal_error.html.j2'), 500
		elif not (status[0] == 20 or status[0] == 22):
			return redirect(url_for('score_page', status=status[0], info=status[1]))
		return redirect(request.referrer)

sr.add_url_rule('/ecomm', view_func=Score_Ecomm.as_view('ecomm'))
sr.add_url_rule(
		'/dns-windows', view_func=Score_DNS_Windows.as_view('dns_windows'))
sr.add_url_rule('/dns-linux', view_func=Score_DNS_Linux.as_view('dns_linux'))
sr.add_url_rule('/pop3', view_func=Score_POP3.as_view('pop3'))
sr.add_url_rule('/smtp', view_func=Score_SMTP.as_view('smtp'))
sr.add_url_rule('/splunk', view_func=Score_Splunk.as_view('splunk'))

config_bp = Blueprint('config', __name__, url_prefix='/config')


@config_bp.route('/')
def config_index():
	"""General HTML page"""
	return render_template('config.html.j2', service='None')


@config_bp.before_request
def login_check():
	"""Checks to see if a login for configuration is needed"""
	require_password = current_app.config['REQUIRE_CONFIG_PASSWORD']
	if not (request.method == 'GET' or request.path == '/config/login' or (
			str(require_password).lower() == 'no') or 'data' in session):
		session['data'] = request.form
		return redirect(url_for('config.config_login', redirect_loc=request.endpoint))


class Config_Login(MethodView):
	"""Controls the config request for Login page"""

	def get(self):
		url_for('static', filename='base.css')
		url_for('static', filename='login.css')
		if 'error' in request.args:
			err = request.args.get('error')
			if str(err).lower() != 'false':
				login_error = False
			else:
				login_error = True
		else:
			login_error = False
		return render_template('login.html.j2', error=login_error, redir=request.args.get('redirect_loc'))

	def post(self):
		pwd = request.form['cptn_pwd']
		redirect_loc = False
		if 'redirect_loc' in request.args:
			redirect_loc = request.args.get('redirect_loc')
		if not redirect_loc:
			return render_template('internal_error.html.j2')
		if pwd == current_app.config['CONFIG_PASSWORD']:
			log.Main.info(
					f"Updating of Config. Password has been entered.{redirect_loc}")
			return redirect(url_for(redirect_loc))

		else:
			return redirect(url_for('config.config_login', error=True, redirect_loc=redirect_loc))


class Config_Ecomm(MethodView):
	"""Controls the config request for Ecomm"""

	def get(self):
		url_for('static', filename='base.css')
		url_for('static', filename='config.css')
		if 'data' in session:
			log.Main.info(
					"Updating of Ecomm Config. Password has been entered.")
			forward = {
				'action': 'config',
				'token':  token.token,
				'data':   {
					'service': 'ecomm',
					'ip':      session['data']['ecomm_ip'],
					'port':    session['data']['ecomm_port']
					}
				}
			status = send_post(forward)
			session.pop('data')
			if status[0] == 500:
				return render_template('internal_error.html.j2'), 500
			elif not (status[0] == 20 or status[0] == 21):
				return render_template('config.html.j2', service='Ecommerce', status=status[0], info=status[1])

		return render_template('config.html.j2', service='Ecommerce')

	def post(self):
		log.Main.info("Updating of Ecomm Config. Password is not required.")
		forward = {
			'action': 'config',
			'data':   {
				'service': 'ecomm',
				'ip':      request.form['ecomm_ip'],
				'port':    request.form['ecomm_port']
				}
			}
		status = send_post(forward)
		if status[0] == 500:
			return render_template('internal_error.html.j2'), 500
		elif not (status[0] == 20 or status[0] == 21):
			return render_template('config.html.j2', service='Ecommerce', status=status[0], info=status[1])
		return redirect(request.referrer)


class Config_DNS_Windows(MethodView):
	"""Controls the config request for Windows DNS"""

	def get(self):
		url_for('static', filename='base.css')
		url_for('static', filename='config.css')
		if 'data' in session:
			log.Main.info(
					"Updating of Windows DNS Config. Password has been entered.")
			domains = session['data']['dnsw_domains'].split(';')
			forward = {
				'action': 'config',
				'token':  token.token,
				'data':   {
					'service': 'dns',
					'machine': 'windows',
					'ip':      session['data']['dnsw_ip'],
					'domains': domains
					}
				}
			status = send_post(forward)
			session.pop('data')
			if status[0] == 500:
				return render_template('internal_error.html.j2'), 500
			elif not (status[0] == 20 or status[0] == 21):
				return render_template('config.html.j2', service='DNS - Windows', status=status[0], info=status[1])

		return render_template('config.html.j2', service='DNS - Windows')

	def post(self):
		log.Main.info(
				"Updating of Windows DNS Config. Password is not required.")
		domains = request.form['dnsw_domains'].split(';')
		forward = {
			'action': 'config',
			'token':  token.token,
			'data':   {
				'service': 'dns',
				'machine': 'windows',
				'ip':      request.form['dnsw_ip'],
				'domains': domains
				}
			}
		status = send_post(forward)
		if status[0] == 500:
			return render_template('internal_error.html.j2'), 500
		elif not (status[0] == 20 or status[0] == 21):
			return render_template('config.html.j2', service='DNS - Windows', status=status[0], info=status[1])

		return redirect(request.referrer)


class Config_DNS_Linux(MethodView):
	"""Controls the config request for Linux DNS"""

	def get(self):
		url_for('static', filename='base.css')
		url_for('static', filename='config.css')
		if 'data' in session:
			log.Main.info(
					"Updating of Linux DNS Config. Password has been entered.")
			domains = session['data']['dnsl_domains'].split(';')
			forward = {
				'action': 'config',
				'token':  token.token,
				'data':   {
					'service': 'dns',
					'machine': 'linux',
					'ip':      session['data']['dnsl_ip'],
					'domains': domains
					}
				}
			status = send_post(forward)
			session.pop('data')

			if status[0] == 500:
				return render_template('internal_error.html.j2'), 500
			elif not (status[0] == 20 or status[0] == 21):
				return render_template('config.html.j2', service='DNS - Linux', status=status[0], info=status[1])
		return render_template('config.html.j2', service='DNS - Linux')

	def post(self):
		log.Main.info(
				"Updating of Linux DNS Config. Password is not required.")
		domains = request.form['dnsl_domains'].split(';')
		forward = {
			'action': 'config',
			'data':   {
				'service': 'dns',
				'machine': 'linux',
				'ip':      request.form['dnsl_ip'],
				'domains': domains
				}
			}
		status = send_post(forward)
		if status[0] == 500:
			return render_template('internal_error.html.j2'), 500
		elif not (status[0] == 20 or status[0] == 21):
			return render_template('config.html.j2', service='DNS - Linux', status=status[0], info=status[1])

		return redirect(request.referrer)


class Config_POP3(MethodView):
	"""Controls the config request for POP3"""

	def get(self):
		url_for('static', filename='base.css')
		url_for('static', filename='config.css')
		if 'data' in session:
			log.Main.info(
					"Updating of POP3 Config. Password has been entered.")
			forward = {
				'action': 'config',
				'token':  token.token,
				'data':   {
					'service':  'pop3',
					'ip':       session['data']['pop_ip'],
					'username': session['data']['pop_user'],
					'password': session['data']['pop_pwd']
					}
				}
			status = send_post(forward)
			session.pop('data')
			if status[0] == 500:
				return render_template('internal_error.html.j2'), 500
			elif not (status[0] == 20 or status[0] == 21):
				return render_template('config.html.j2', service='POP3', status=status[0], info=status[1])

		return render_template('config.html.j2', service='POP3')

	def post(self):
		log.Main.info(
				"Updating of POP3 Config. Password is not required.")
		forward = {
			'action': 'config',
			'data':   {
				'service':  'pop3',
				'ip':       request.form['pop_ip'],
				'username': request.form['pop_user'],
				'password': request.form['pop_pwd']
				}
			}
		status = send_post(forward)
		if status[0] == 500:
			return render_template('internal_error.html.j2'), 500
		elif not (status[0] == 20 or status[0] == 21):
			return render_template('config.html.j2', service='POP3', status=status[0], info=status[1])

		return redirect(request.referrer)


class Config_SMTP(MethodView):
	"""Controls the config request for SMTP"""

	def get(self):
		url_for('static', filename='base.css')
		url_for('static', filename='config.css')
		if 'data' in session:
			log.Main.info(
					"Updating of Windows DNS Config. Password has been entered.")
			forward = {
				'action': 'config',
				'token':  token.token,
				'data':   {
					'service': 'smtp',
					'ip':      session['data']['smtp_ip'],
					'user 1':  session['data']['smtp_usr1'],
					'user 1 pwd': session['data']['smtp_usr1_pwd'],
					'user 2':  session['data']['smtp_usr2'],
					'domain':  session['data']['smtp_domain']
					}
				}
			status = send_post(forward)
			session.pop('data')
			if status[0] == 500:
				return render_template('internal_error.html.j2'), 500
			elif not (status[0] == 20 or status[0] == 21):
				return render_template('config.html.j2', service='SMTP', status=status[0], info=status[1])

		return render_template('config.html.j2', service='SMTP')


	def post(self):
		log.Main.info(
				"Updating of Windows DNS Config. Password is not required.")
		forward = {
			'action': 'config',
			'data':   {
				'service':    'smtp',
				'ip':         request.form['smtp_ip'],
				'user 1':     request.form['smtp_usr1'],
				'user 1 pwd': request.form['smtp_usr1_pwd'],
				'user 2':     request.form['smtp_usr2'],
				'domain':     request.form['smtp_domain']
				}
			}
		status = send_post(forward)
		if status[0] == 500:
			return render_template('internal_error.html.j2'), 500
		elif not (status[0] == 20 or status[0] == 21):
			return render_template('config.html.j2', service='SMTP', status=status[0], info=status[1])

		return redirect(request.referrer)


class Config_Splunk(MethodView):
	"""Controls the config request for Splunk"""

	def get(self):
		url_for('static', filename='base.css')
		url_for('static', filename='config.css')
		if 'data' in session:
			log.Main.info(
					"Updating of Splunk Config. Password has been entered.")
			forward = {
				'action': 'config',
				'token':  token.token,
				'data':   {
					'service': 'splunk',
					'ip':      session['data']['splunk_ip'],
					'port':    session['data']['splunk_port']
					}
				}
			status = send_post(forward)
			session.pop('data')
			if status[0] == 500:
				return render_template('internal_error.html.j2'), 500
			elif not (status[0] == 20 or status[0] == 21):
				return render_template('config.html.j2', service='Splunk', status=status[0], info=status[1])

		return render_template('config.html.j2', service='Splunk')

	def post(self):
		log.Main.info("Updating of Splunk Config. Password is not required.")
		forward = {
			'action': 'config',
			'data':   {
				'service': 'splunk',
				'ip':      request.form['splunk_ip'],
				'port':    request.form['splunk_port']
				}
			}
		status = send_post(forward)
		if status[0] == 500:
			return render_template('internal_error.html.j2'), 500
		elif not (status[0] == 20 or status[0] == 21):
			return render_template('config.html.j2', service='Splunk', status=status[0], info=status[1])
		return redirect(request.referrer)


config_bp.add_url_rule('/ecomm', view_func=Config_Ecomm.as_view('ecomm'))
config_bp.add_url_rule(
		'/dns-windows', view_func=Config_DNS_Windows.as_view('dns_windows'))
config_bp.add_url_rule(
		'/dns-linux', view_func=Config_DNS_Linux.as_view('dns_linux'))
config_bp.add_url_rule('/pop3', view_func=Config_POP3.as_view('pop3'))
config_bp.add_url_rule('/smtp', view_func=Config_SMTP.as_view('smtp'))
config_bp.add_url_rule('/splunk', view_func=Config_Splunk.as_view('splunk'))
config_bp.add_url_rule(
		'/login', view_func=Config_Login.as_view('config_login'))


def send_post(data):
	"""
		Forwards on post data from the form request to the backend server.

		Status Response Codes:
			20 - Good Request
			21 - Config Accepted
			22 - Attempting to Score
			40 - Did not send data in correct format
			41 - Invalid Token
			42 - Wrong Method
			43 - Invalid Action
			44 - Invalid Service
			45 - Invalid Configuration
	"""
	try:
		url = current_app.config["BACK_END_LOCATION"]
		headers = {'token': token.token}
		rsp = requests.post(
				url=f'http://{url}', json=data, headers=headers)
		data = json.loads(rsp.content)
		status_code = data['code']
	except Exception as e:
		log.Error.error(e)
		status_code = 500
	if status_code == 40:
		info = 'Did not send data in correct format.'
	elif status_code == 41:
		info = 'Invalid Token'
	elif status_code == 42:
		info = 'Wrong Method'
	elif status_code == 43:
		info = 'Invalid Action'
	elif status_code == 44:
		info = 'Invalid Service'
	elif status_code == 45:
		info = 'Invalid Configuration'
	else:
		info = ''

	return (status_code, info)
