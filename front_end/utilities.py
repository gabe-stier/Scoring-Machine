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

cwd = os.getcwd()


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

                m.update(str(datetime.now()).encode())
                token = m.hexdigest()
                f.write(token)
                print(token, flush=True)
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

    def __init__(self):
        pass

    def init_app(self, app):
        try:
            self.host = str(app.config['MYSQL_HOST']),
            self.username = str(app.config['MYSQL_USER']),
            self.password = str(app.config['MYSQL_PASSWORD'])

            self.db = conn.connect(
                host=app.config['MYSQL_HOST'],
                user=app.config['MYSQL_USER'],
                password=app.config['MYSQL_PASSWORD']
            )
            self.generate_database()
            self.generate_tables()
            self.generate_views()
            self.db.close()
            self.db = conn.connect(
                host=app.config['MYSQL_HOST'],
                user=app.config['MYSQL_USER'],
                password=app.config['MYSQL_PASSWORD'],
                database='scoring_engine'
            )
        except Exception as e:
            print(e, flush=True)

    def get_db(self):
        return self.db

    def get_last_score(self):
        cursor = self.db.cursor()
        cursor.execute('SELECT * FROM scores;')
        result = cursor.fetchall()
        return result

    def get_top_scores(self, service: Scores, count=5):
        cursor = self.db.cursor()
        if service == Scores.ECOMM:
            table = 'ecomm'
        elif service == Scores.SMTP:
            table = 'smtp'
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
            f'SELECT test_date,success FROM {table} ORDER BY test_id DESC LIMIT {count};')
        result = cursor.fetchone()
        return result

    def generate_database(self):
        cur = self.db.cursor()
        cur.execute('CREATE DATABASE IF NOT EXISTS scoring_engine')
        self.db.commit()

    def generate_tables(self):
        cur = self.db.cursor()
        with open(f'{cwd}/sql/basic_db.sql') as f:
            schema = f.read()
            results = cur.execute(schema, multi=True)
            for result in results:
                result
            self.db.commit()

    def generate_views(self):
        cur = self.db.cursor()
        with open(f'{cwd}/sql/views.sql') as f:
            schema = f.read()
            results = cur.execute(schema, multi=True)
            for result in results:
                result
            self.db.commit()


db = Database()
