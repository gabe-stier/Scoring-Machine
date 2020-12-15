'''
Created on Nov 26, 2020

@author: gabez
'''

import logging
from hashlib import blake2b
import os
from datetime import datetime
import mysql.connector as conn
from flask import current_app
from enum import Enum, auto


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


class Scores(Enum):
    SPLUNK = auto(),
    ECOMM = auto(),
    DNS_LINUX = auto(),
    DNS_WINDOWS = auto(),
    POP3 = auto(),
    LDAP = auto(),
    SMTP = auto()


class Database:
    host = ''
    username = ''
    password = ''
    db = None

    def __init__(self, host='localhost', username='scoring_engine', password='ChangeMe1!'):
        self.host = host
        self.username = username
        self.password = password
        self.db = conn.connect(
            host=self.host,
            user=self.username,
            password=self.password
        )

    def get_db(self):
        return self.db

    def get_last_score(self, service: Scores):
        cursor = self.db.cursor()
        if service == Scores.ECOMM:
            table = 'ecomm'
        elif service == Scores.SMTP:
            table = 'smpt'
        elif service == Scores.POP3:
            table = 'pop3'
        elif service == Scores.LDAP:
            table = 'ldap'
        elif service == Scores.DNS_LINUX:
            table = 'dns_linux'
        elif service == Scores.DNS_WINDOWS:
            table = 'dns_windows'
        elif service == Scores.SPLUNK:
            table = 'splunk'
        cursor.execute(f'SELECT * FROM {table} ORDER BY test_id DESC LIMIT 1;')
        result = cursor.fetchall()
        return result

    def get_top_scores(self, service: Scores, count = 5):
        cursor = self.db.cursor()
        if service == Scores.ECOMM:
            table = 'ecomm'
        elif service == Scores.SMTP:
            table = 'smpt'
        elif service == Scores.POP3:
            table = 'pop3'
        elif service == Scores.LDAP:
            table = 'ldap'
        elif service == Scores.DNS_LINUX:
            table = 'dns_linux'
        elif service == Scores.DNS_WINDOWS:
            table = 'dns_windows'
        elif service == Scores.SPLUNK:
            table = 'splunk'
        cursor.execute(f'SELECT * FROM {table} ORDER BY test_id DESC LIMIT {count};')
        result = cursor.fetchall()
        return result


db = Database(host=current_app.config['MYSQL_LOCATION'],
              username=current_app.config['MYSQL_USER'],
              password=current_app.config['MYSQL_PWD'])
