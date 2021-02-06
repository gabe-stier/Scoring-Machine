"""
Created on Nov 26, 2020

@author: gabez
"""

import logging
import os
from datetime import datetime
from enum import Enum, auto
from hashlib import blake2b

cwd = os.getcwd()


class Loggers:
    """Log handlers used for this scoring machine"""
    Main = logging.getLogger("main")
    Scoring = logging.getLogger("scoring")
    Web = logging.getLogger("web")
    Error = logging.getLogger('error')


class Token:
    """Generates a token that is used between Flask and the Request Server"""
    token = 'NULL'

    def __init__(self):
        if os.path.exists('/tmp/scoring_token'):
            with open('/tmp/scoring_token', 'r') as f:
                self.token = f.read()
        else:
            with open('/tmp/scoring_token', 'w') as f:
                m = blake2b(salt=b'semo')

                m.update(str(datetime.now()).encode())
                token = m.hexdigest()
                f.write(token)
                self.token = token


class Scores(Enum):
    """List of the Services used."""
    SPLUNK = auto(),
    ECOMM = auto(),
    DNS_LINUX = auto(),
    DNS_WINDOWS = auto(),
    POP3 = auto(),
    SMTP = auto()
