from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import json
import cgi

import back_end.actions as action
from back_end.util import generate_token

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
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

        # refuse to receive non-json content
        if ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return

        # read the message and convert it into a python dictionary
        length = int(self.headers.getheader('content-length'))
        message = json.loads(self.rfile.read(length))
        if message['token'] == token:
            if message['action'] == 'score':
                action.score_service(message['data'])
                response = {
                    'response': "Accepted",
                    'return': message
                }
            elif message['action'] == 'config':
                action.update_config(message['data'])
                response = {
                    'response': "Accepted",
                    'return': message
                }
            else:
                response = {
                    "error": 'Invalid Action'
                }
        else:
            self._set_headers(code=401)
            response = {
                "error": "Invalid Token"
            }
            self.wfile.write(json.dumps(response))
            return

        self._set_headers()
        self.wfile.write(json.dumps(response))


def run(server_class=HTTPServer, handler_class=Server, port=18651):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)

    print(f'Starting httpd on port {port}...')
    httpd.serve_forever()


if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
