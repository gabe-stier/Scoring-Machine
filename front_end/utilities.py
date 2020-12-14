'''
Created on Nov 26, 2020

@author: gabez
'''

import logging
from hashlib import blake2b
import os
from datetime import datetime


class Loggers:
    '''
        Log handlers used for this scoring machine
    '''
    Main = logging.getLogger("main")
    Scoring = logging.getLogger("scoring")
    Web = logging.getLogger("web")
    Error = logging.getLogger('error')


class Token:
    token = 'NULL'

    def __init__(self):
        if os.path.exists('/tmp/scoring_token'):
            with open('/tmp/scoring_token', 'r') as f:
                self.token = f.read()
        else:
            with open('/tmp/scoring_token', 'w') as f:
                m = blake2b(salt=b'semo')

                m.update(datetime.now().encode())
                token = m.hexdigest()
                f.write(token)
                self.token = token
        self.token = 'c6d78d77ec9528a860c817ba726bc1336c6498c801c24d5416019d548378c8843230c8cb01a0831d0b09e93890341fba254a69c47530bfab4fd4cbe2d7c471c3'
