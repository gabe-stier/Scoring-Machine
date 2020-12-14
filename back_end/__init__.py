from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import json
import cgi

import actions as action
from util import generate_token

token = generate_token()


class Server(BaseHTTPRequestHandler):
    def _set_headers(self, code=200):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_HEAD(self):
        self._set_headers()

    # GET sends back a Hello world message
    def do_GET(self):
        self.send_response(405)
        self.end_headers()
        return

    # POST echoes the message adding a JSON field
    def do_POST(self):

        ctype, pdict = cgi.parse_header(self.headers['content-type'])

        # refuse to receive non-json content
        if ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return

        # read the message and convert it into a python dictionary
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
                response = {
                    "error": 'Invalid Action',
                    "internal status code": 43,
                    'data sent': message
                }
                return
        else:
            self._set_headers(code=401)
            response = {
                "error": "Invalid Token",
                "internal status code": 41,
                'data sent': message
            }
            self.wfile.write(json.dumps(response).encode())
            return

        self._set_headers()
        self.wfile.write(json.dumps(response).encode())


def run(server_class=HTTPServer, handler_class=Server, port=5001):
    server_address = ('', port)
    print(server_address)
    httpd = server_class(server_address, handler_class)

    print(f'Starting httpd on port {server_address}...', flush=True)
    httpd.serve_forever()


print("Hello", flush=True)

if __name__ == "__main__":
    run()
