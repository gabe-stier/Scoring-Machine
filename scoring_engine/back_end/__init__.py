"""Main file of the scoring engine"""
import cgi
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from logging.config import dictConfig

from scoring_engine.back_end import actions as action
from scoring_engine.back_end.background import start_scoring
from scoring_engine.back_end.utilities import generate_token, Loggers as log

token = generate_token()
DEBUG = False


class Server(BaseHTTPRequestHandler):
	"""Class used as the request server to process information from Flask and score the services that
	are in the competition network."""

	def _set_headers(self, code=200):
		"""Sets headers for response"""
		self.send_response(code)
		self.send_header('Content-type', 'application/json')
		self.end_headers()

	def do_HEAD(self):
		"""Sets headers for a HEAD request"""
		self._set_headers()

	def do_GET(self):
		"""Reponds to a GET request"""
		self.send_response(405)
		self.log_message()
		self.log_request(status_code=405, response_code=42)
		self.end_headers()

	def do_POST(self):
		"""Responds to a POST request"""
		self.log_message()
		ctype, pdict = cgi.parse_header(self.headers['content-type'])

		# Returns 400 if the request to the server is not in json form.
		if ctype != 'application/json':
			self._set_headers(400)
			self.log_request(status_code=400, response_code=40)
			self.response_code = 40
			self.end_headers()
			response = {
				'response': "Wrong Content-Type",
				"code":     40,
				}
			self.wfile.write(json.dumps(response).encode())
			return

		length = int(self.headers['content-length'])
		message = json.loads(self.rfile.read(length))

		# Main if stack that runs if the token is correct or if the DEBUG value is set to True
		if (self.headers['token'] == token) or DEBUG:
			if message['action'] == 'score':
				if action.score_service(message['data']):
					response = {
						'response':  "Accepted",
						"code":      22,
						'data sent': message
						}
					self.response_code = 22
				else:
					response = {
						'response':  "Invalid service",
						"code":      44,
						'data sent': message
						}
					self.response_code = 44
			elif message['action'] == 'config':
				act = action.update_config(message['data'])
				if act:
					response = {
						'response':  "Accepted",
						"code":      21,
						'data sent': message
						}
					self.response_code = 21
				elif not act:
					response = {
						'response':  "Invalid service",
						"code":      44,
						'data sent': message
						}
					self.response_code = 44
				elif act is None:
					response = {
						'response':  'Invalid Configuration',
						"code":      45,
						'data sent': message
						}
					self.response_code = 45

			else:
				self._set_headers(code=400)
				self.response_code = 43
				response = {
					"error":     'Invalid Action',
					"code":      43,
					'data sent': message
					}
				self.wfile.write(json.dumps(response).encode())
				return
		else:
			self._set_headers(code=401)
			self.response_code = 41
			response = {
				"error":     "Invalid Token",
				"code":      41,
				'data sent': message
				}
			self.wfile.write(json.dumps(response).encode())
			return

		self._set_headers()
		self.wfile.write(json.dumps(response).encode())

	def log_message(self):
		"""Logs all requests that the server handles"""
		log.Web.info(f'Request from {self.client_address[0]}')

	def log_request(self, status_code='-', response_code='-'):
		"""Logs all responses made by the server"""
		log.Web.info(
				f'Request from {self.client_address[0]} with a status code of {status_code} and response code of {self.response_code}')


def start(server_class=HTTPServer, handler_class=Server, port=5001):
	"""Main function that starts the request server"""
	print("Starting Scoring Server", flush=True)
	if 'DEBUG' in os.environ:
		global DEBUG
		DEBUG = os.environ['DEBUG']
	setup_logging()
	start_scoring()
	server_address = ('', port)
	httpd = server_class(server_address, handler_class)

	print(f'Starting httpd on port {server_address}...', flush=True)
	log.Main.info(f'Starting httpd on port {server_address}...')
	httpd.serve_forever()


def setup_logging():
	"""Sets up the loggers used within the request server"""
	try:
		os.mkdir('/var/log/scoring-engine', mode=0o666)
	except FileExistsError as e:
		pass
	except Exception as e:
		print('Back End Error \\/', e, sep='\n')
	try:
		os.mkdir('/var/log/scoring-engine/scorer', mode=0o666)
	except FileExistsError as e:
		pass
	except Exception as e:
		print('Back End Error \\/', e, sep='\n')

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
				'filename':  os.path.join('/var/log/scoring-engine/scorer', 'full.log'),
				'when':      'midnight'
				},
			'main':    {
				'class':     'logging.handlers.TimedRotatingFileHandler',
				'formatter': 'default',
				'filename':  os.path.join('/var/log/scoring-engine/scorer', 'main.log'),
				'when':      'midnight'
				},
			'scoring': {
				'class':     'logging.handlers.TimedRotatingFileHandler',
				'formatter': 'default',
				'filename':  os.path.join('/var/log/scoring-engine/scorer', 'scoring.log'),
				'when':      'midnight'
				},
			'web':     {
				'class':     'logging.handlers.TimedRotatingFileHandler',
				'formatter': 'default',
				'filename':  os.path.join('/var/log/scoring-engine/scorer', 'web.log'),
				'when':      'midnight'
				},
			'error':   {
				'class':     'logging.handlers.TimedRotatingFileHandler',
				'formatter': 'request',
				'filename':  os.path.join('/var/log/scoring-engine/scorer', 'error.log'),
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


if __name__ == "__main__":
	start()
