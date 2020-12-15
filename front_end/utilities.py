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
