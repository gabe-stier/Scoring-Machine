from configparser import ConfigParser

import mysql.connector as conn

from front_end.utilities import Loggers as log
from front_end.utilities import Scores as Service


def open_database():
    try:
        db = None
        config = read_config()
        db = conn.connect(
            host=config['MYSQL_HOST'],
            username=config['MYSQL_USER'],
            password=config['MYSQL_PASSWORD'],
            database='scoring_engine'
        )
        return db
    except Exception as e:
        log.Error.error(e)
        print(e, flush=True)

def read_config():
    with open("config/application.conf", 'r') as f:
        content = f.read()
        paths = content.split("\n")
        config_dict = {}
        for path in paths:
            setting = path.split(" = ")
            config_dict[setting[0]] = setting[1].replace('\'', '')

    return config_dict


def get_last_score():
    try:
        db = open_database()
        cursor = db.cursor(buffered=True)
        cursor.execute('SELECT * FROM scores')
        result = cursor.fetchall()
        db.close()
        return result
    except Exception as e:
        log.Error.error(e)
        print(e, flush=True)


def get_top_scores(service: Service, count=5):
    db = open_database()
    # TODO Update this method.
    cursor = db.cursor()
    if service == Service.ECOMM:
        table = 'ecomm'
    elif service == Service.SMTP:
        table = 'smtp'
    elif service == Service.POP3:
        table = 'pop3'
    elif service == Service.LDAP:
        table = 'ldap'
    elif service == Service.DNS_LINUX:
        table = 'dns_linux'
    elif service == Service.DNS_WINDOWS:
        table = 'dns_windows'
    elif service == Service.SPLUNK:
        table = 'splunk'
    cursor.execute(
        f'SELECT test_date,success FROM {table} ORDER BY test_id DESC LIMIT {count};')
    result = cursor.fetchone()
    db.close()
    return result
