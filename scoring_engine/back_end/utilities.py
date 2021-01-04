"""Module that contains all the items that are used within each sub-module"""

import logging
import os
from datetime import datetime
from enum import Enum, auto
from hashlib import blake2b


def read_config():
    """Reads the application.conf file."""
    with open("/opt/scoring-engine/application.conf", 'r') as f:
        content = f.read()
        paths = content.split("\n")
        config_dict = {}
        for path in paths:
            setting = path.split(" = ")
            if '' in setting:
                break
            config_dict[setting[0]] = setting[1].replace('\'', '')
    return config_dict


config = read_config()


def generate_token():
    """Generates a token that is used between Flask and the Request Server"""
    if os.path.exists('/tmp/scoring_token'):
        with open('/tmp/scoring_token', 'r') as f:
            return f.read()
    else:
        with open('/tmp/scoring_token', 'w') as f:
            m = blake2b(salt=b'semo')
            m.update(str(datetime.now()).encode())
            token = m.hexdigest()
            f.write(token)
            return token


class Loggers:
    """Log handlers used for this scoring machine"""
    Main = logging.getLogger("main")
    Scoring = logging.getLogger("scoring")
    Web = logging.getLogger("web")
    Error = logging.getLogger('error')


class Services(Enum):
    """List of the Services used."""
    SPLUNK = auto(),
    ECOMM = auto(),
    DNS_LINUX = auto(),
    DNS_WINDOWS = auto(),
    POP3 = auto(),
    LDAP = auto(),
    SMTP = auto()
