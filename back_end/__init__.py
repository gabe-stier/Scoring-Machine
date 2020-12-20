from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import json
import cgi
import os
import logging
from logging.config import dictConfig

import actions as action
from utilities import generate_token,config
from utilities import Loggers as log
from scoring_functions import set_service_config
from background import start_scoring

token = generate_token()

DEBUG = False


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
        self.log_request(status_code=405, response_code=42)
        self.end_headers()
        return

    def do_POST(self):
        self.log_message()
        ctype, pdict = cgi.parse_header(self.headers['content-type'])

        if ctype != 'application/json':
            self._set_headers(400)
            self.log_request(status_code=400, response_code=40)
            self.response_code = 40
            self.end_headers()
            response = {
                'response': "Wrong Content-Type",
                "code": 40,
            }
            self.wfile.write(json.dumps(response).encode())
            return

        length = int(self.headers['content-length'])
        message = json.loads(self.rfile.read(length))
        if (self.headers['token'] == token) or DEBUG == True:
            if message['action'] == 'score':
                if action.score_service(message['data']):
                    response = {
                        'response': "Accepted",
                        "code": 22,
                        'data sent': message
                    }
                    self.response_code = 22
                else:
                    response = {
                        'response': "Invalid service",
                        "code": 44,
                        'data sent': message
                    }
                    self.response_code = 44
            elif message['action'] == 'config':
                act = action.update_config(message['data'])
                if act == True:
                    response = {
                        'response': "Accepted",
                        "code": 21,
                        'data sent': message
                    }
                    self.response_code = 21
                elif act == False:
                    response = {
                        'response': "Invalid service",
                        "code": 44,
                        'data sent': message
                    }
                    self.response_code = 44
                elif act == None:
                    response = {
                        'response': 'Invalid Configuration',
                        "code": 45,
                        'data sent': message
                    }
                    self.response_code = 45

            else:
                self._set_headers(code=400)
                # self.log_request(status_code=400, response_code=43)
                self.response_code = 43
                response = {
                    "error": 'Invalid Action',
                    "code": 43,
                    'data sent': message
                }
                self.wfile.write(json.dumps(response).encode())
                return
        else:
            self._set_headers(code=401)
            # self.log_request(status_code=401, response_code=41)
            self.response_code = 41
            response = {
                "error": "Invalid Token",
                "code": 41,
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
            f'Request from {self.client_address[0]} with a status code of {status_code} and response code of {self.response_code}')


def start(server_class=HTTPServer, handler_class=Server, port=5001):
    global DEBUG
    if (os.environ['DEBUG'] == 'True'):
        DEBUG = True
    else:
        DEBUG = False
    setup_logging()
    set_service_config()
    start_scoring()
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
        print('Back End Error \\/', e, sep='\n')
    try:
        os.mkdir('/var/log/scoring-machine/scorer', mode=0o666)
    except FileExistsError as e:
        pass
    except Exception as e:
        print('Back End Error \\/', e, sep='\n')

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
