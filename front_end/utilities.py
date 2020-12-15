'''
Created on Nov 26, 2020

@author: gabez
'''

import logging
from hashlib import blake2b
import os
from datetime import datetime
import mysql.connector as conn
from enum import Enum, auto
from configparser import ConfigParser


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
        try:
            self.db = conn.connect(
                host=self.host,
                user=self.username,
                password=self.password
            )
            self.generate_database()
            self.db.close()
            self.db = conn.connect(
                host=self.host,
                user=self.username,
                password=self.password,
                database='scoring_engine'
            )
            self.generate_tables()
        except Exception as e:
            print(e, flush=True)
            # pass

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

    def get_top_scores(self, service: Scores, count=5):
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
        cursor.execute(
            f'SELECT * FROM {table} ORDER BY test_id DESC LIMIT {count};')
        result = cursor.fetchall()
        return result

    def generate_database(self):
        cur = self.db.cursor()
        cur.execute('CREATE DATABASE IF NOT EXISTS scoring_engine')

    def generate_tables(self):
        cur = self.db.cursor()
        with open('front_end/etc/basic_db.sql') as f:
            schema = f.read()
            cur.execute(schema)


config = ConfigParser()
config.read('front_end/config/mysql.conf')
db = Database(host=config['DEFAULT']['MYSQL_LOCATION'],
                username=config['DEFAULT']['MYSQL_USER'],
                password=config['DEFAULT']['MYSQL_PWD'])
