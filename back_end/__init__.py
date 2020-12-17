from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import json
import cgi
import os
import logging
from logging.config import dictConfig

import actions as action
from utilities import generate_token
from utilities import Loggers as log
from utilities import config 

token = generate_token()


class Server(BaseHTTPRequestHandler):
    def _set_headers(self, code=200):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_HEAD(self):
        self._set_headers()

    def do_GET(self):
        self.send_response(405)
        self.log_message()
        self.log_request(status_code=405,response_code=42)
        self.end_headers()
        return

    def do_POST(self):
        self.log_message()
        ctype, pdict = cgi.parse_header(self.headers['content-type'])

        if ctype != 'application/json':
            self._set_headers(400)
            self.log_request(status_code=400 ,response_code=40)
            self.end_headers()
            response = {
                'response': "Wrong Content-Type",
                "internal status code": 40,
            }
            self.wfile.write(json.dumps(response).encode())
            return

        length = int(self.headers['content-length'])
        message = json.loads(self.rfile.read(length))
        print(message, flush=True)
        if message['token'] == token:
            message.pop('token')
            if message['action'] == 'score':
                action.score_service(message['data'])
                response = {
                    'response': "Accepted",
                    "internal status code": 22,
                    'data sent': message
                }
            elif message['action'] == 'config':
                action.update_config(message['data'])
                response = {
                    'response': "Accepted",
                    "internal status code": 21,
                    'data sent': message
                }
            else:
                self._set_headers(code=400)
                self.log_request(status_code=400,response_code=43)
                response = {
                    "error": 'Invalid Action',
                    "internal status code": 43,
                    'data sent': message
                }
                self.wfile.write(json.dumps(response).encode())
                return
        else:
            self._set_headers(code=401)
            self.log_request(status_code=401, response_code=41)
            response = {
                "error": "Invalid Token",
                "internal status code": 41,
                'data sent': message
            }
            self.wfile.write(json.dumps(response).encode())
            return

        self._set_headers()
        self.wfile.write(json.dumps(response).encode())

    def log_message(self):
        log.Web.info(f'Request from {self.client_address[0]}')

    def log_request(self, status_code='-', response_code='-'):
        log.Web.info(
            f'Request from {self.client_address[0]} with a status code of {status_code} and response code of {response_code}')


def start(server_class=HTTPServer, handler_class=Server, port=5001):
    setup_logging()
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)

    print(f'Starting httpd on port {server_address}...', flush=True)
    httpd.serve_forever()


def setup_logging():
    try:
        os.mkdir('/var/log/scoring-machine', mode=0o666)
    except FileExistsError as e:
        pass
    except Exception as e:
        print(e)
    try:
        os.mkdir('/var/log/scoring-machine/scorer', mode=0o666)
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
                'filename': os.path.join('/var/log/scoring-machine/scorer', 'full.log'),
                'when': 'midnight'
            },
            'main': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'formatter': 'default',
                'filename': os.path.join('/var/log/scoring-machine/scorer', 'main.log'),
                'when': 'midnight'
            },
            'scoring': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'formatter': 'default',
                'filename': os.path.join('/var/log/scoring-machine/scorer', 'scoring.log'),
                'when': 'midnight'
            },
            'web': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'formatter': 'default',
                'filename': os.path.join('/var/log/scoring-machine/scorer', 'web.log'),
                'when': 'midnight'
            },
            'error': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'formatter': 'request',
                'filename': os.path.join('/var/log/scoring-machine/scorer', 'error.log'),
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


print("Starting Scoring Server", flush=True)

if __name__ == "__main__":
    start()
