import logging
import os
import random
from configparser import ConfigParser
from datetime import datetime
from enum import Enum, auto
from hashlib import blake2b

import mysql.connector as conn


def read_config():
    with open("config/application.conf", 'r') as f:
        content = f.read()
        paths = content.split("\n")
        config_dict = {}
        for path in paths:
            setting = path.split(" = ")
            config_dict[setting[0]] = setting[1].replace('\'', '')

    return config_dict


config = read_config()


def generate_token():
    if os.path.exists('/tmp/scoring_token'):
        with open('/tmp/scoring_token', 'r') as f:
            return f.read()
    else:
        with open('/tmp/scoring_token', 'w') as f:
            m = blake2b(salt=b'semo')
            m.update(str(datetime.now()).encode())
            token = m.hexdigest()
            f.write(token)
            print(token, flush=True)
            return token


class Loggers:
    '''
        Log handlers used for this scoring machine
    '''
    Main = logging.getLogger("main")
    Scoring = logging.getLogger("scoring")
    Web = logging.getLogger("web")
    Error = logging.getLogger('error')


class Services(Enum):
    SPLUNK = auto(),
    ECOMM = auto(),
    DNS_LINUX = auto(),
    DNS_WINDOWS = auto(),
    POP3 = auto(),
    LDAP = auto(),
    SMTP = auto()
