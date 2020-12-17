from hashlib import blake2b
import os
from datetime import datetime
import logging
import mysql.connector as conn
from enum import Enum, auto
from configparser import ConfigParser


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
            return token


class Loggers:
    '''
        Log handlers used for this scoring machine
    '''
    Main = logging.getLogger("main")
    Scoring = logging.getLogger("scoring")
    Web = logging.getLogger("web")
    Error = logging.getLogger('error')


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
        print('backend',self.host, self.username, self.password, flush=True)
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

    def generate_database(self):
        cur = self.db.cursor()
        cur.execute('CREATE DATABASE IF NOT EXISTS scoring_engine')

    def generate_tables(self):
        cur = self.db.cursor()
        with open('sql/basic_db.sql') as f:
            schema = f.read()
            cur.execute(schema)


try:
    db = Database(host=config['MYSQL_HOST'],
                  username=config['MYSQL_USER'],
                  password=config['MYSQL_PASSWORD'])
except Exception as e:
    print('back ---------', e, flush=True)
