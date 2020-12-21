import asyncio
import http
import os
import poplib
import random
import smtplib
import time
from configparser import ConfigParser
from datetime import datetime
from hashlib import sha3_512
from smtplib import SMTPException
from socket import timeout
from threading import Thread

import ldap
import mysql.connector as conn
from ldap import AUTH_UNKNOWN
from nslookup import Nslookup

from utilities import Loggers as log
from utilities import Scores as Service


def run_task(service: Service):
    if service == Service.DNS_WINDOWS:
        score_dns_windows()
    if service == Service.DNS_LINUX:
        score_dns_linux()
    if service == Service.SPLUNK:
        score_splunk()
    if service == Service.ECOMM:
        score_ecomm()
    if service == Service.LDAP:
        score_ldap()
    if service == Service.POP3:
        score_pop3()
    if service == Service.SMTP:
        score_smtp()


def score_splunk():
    config = ConfigParser()
    config.read('back_end/config/service.conf')

    ip = config['SPLUNK']['ip']
    table_name = config['SPLUNK']['sqltable']
    hash_file = config['SPLUNK']['hashfile']
    port = config['SPLUNK']['port']
    db = open_database()
    try:
        site = http.client.HTTPConnection(ip, port, timeout=5)
        site.request('GET', '/')
        site_response = site.getresponse()
        site.close()
        site_string = f'{site_response.getheaders()[0]}\n\nStatus: {site_response.status}\n\n{site_response.read()}'
        site_hash = sha3_512()
        site_hash.update(site_string.encode())
        with open(f'back_end/{hash_file}', 'r') as f:
            good_hash = f.read()
            if good_hash == site_hash.hexdigest():
                set_score(db, table_name, 1)
            else:
                set_score(db, table_name, 0)
    except timeout:
        set_score(db, table_name, 0)
    except Exception as e:
        set_score(db, table_name, 2)
        log.Error.error(e)

def get_ldap_info(db):
        cur = db.cursor(buffered=True)
        result = cur.execute('SELECT username, password FROM ldap_info')
        if result is not None:
            user = random.choice(result.fetchall())
        else:
            user = None
        return user

def score_ldap():
    status = 0
    config = ConfigParser()
    config.read('back_end/config/service.conf')

    ip = config['LDAP']['ip']
    table = config['LDAP']['SQLTable']

    db = open_database()

    try:
        connection = ldap.initialize(f'ldap://{ip}')
        connection.set_option(ldap.OPT_REFERRALS, 0)
        user = get_ldap_info(db)
        if user is None:
            raise Exception(
                "Configuration has not been set yet for LDAP to be scored correctly")
        connection.simple_bind_s(user[0], user[1])
        status = 1
    except AUTH_UNKNOWN:
        status = 0
    except Exception as e:
        log.Error.error(e)
        status = 2
        print(e)
    finally:
        set_score(db, table, status)


def score_ecomm():
    config = ConfigParser()
    config.read('back_end/config/service.conf')

    ip = config['ECOMMERCE']['ip']
    table_name = config['ECOMMERCE']['sqltable']
    hash_file = config['ECOMMERCE']['hashfile']
    port = config['ECOMMERCE']['port']
    db = open_database()
    try:
        site = http.client.HTTPConnection(ip, port, timeout=5)
        site.request('GET', '/')
        site_response = site.getresponse()
        site.close()
        site_string = f'{site_response.getheaders()[0]}\n\nStatus: {site_response.status}\n\n{site_response.read()}'
        site_hash = sha3_512()
        site_hash.update(site_string.encode())
        with open(f'back_end/{hash_file}', 'r') as f:
            good_hash = f.read()
            if good_hash == site_hash.hexdigest():
                set_score(db, table_name, 1)
            else:
                set_score(db, table_name, 0)
    except timeout:
        set_score(db, table_name, 0)
    except Exception as e:
        set_score(db, table_name, 2)
        log.Error.error(e)


def score_pop3():
    db = open_database()
    config = ConfigParser()
    config.read('back_end/config/service.conf')
    ip = config['POP3']['ip']
    port = config['POP3']['port']
    table_name = config['POP3']['SQLTable']
    status = 0
    try:
        pop = poplib.POP3(ip, port)
        user = db.get_pop3_info()
        if user is None:
            raise Exception(
                "Configuration has not been set yet for POP3 to be scored correctly")
        pop.user(config['POP3']['user'])
        pop.pass_(config['POP3']['password'])
        email_number = random.randint(0, pop.stat())
        (msg, body, octets) = pop.retr(email_number)
        sender = f"{config['SMTP']['from_user']}@{config['SMTP']['domain']}"
        if f'From: {sender}' in body:
            status = 1
        else:
            status = 0
        pop.quit()
    except Exception as e:
        status = 2
        log.Error.error(e)
    finally:
        set_score(db, table_name, status)


def get_receivers(db):
    cur = db.cursor(buffered=True)
    result = cur.execute('SELECT to_user FROM smtp_info')
    if result is not None:
        to_user = result.fetchall()
    else:
        to_user = None
    return to_user


def score_smtp():
    try:
        db = open_database()
        config = ConfigParser()
        config.read('back_end/config/service.conf')

        sender = f"{config['SMTP']['from_user']}@{config['SMTP']['domain']}"
        receivers = get_receivers(db)
        ip = config['SMTP']['ip']
        port = config['SMTP']['port']
        table = config['SMTP']['SQLTable']

        if receivers is None:
            raise Exception(
                "Configuration has not been set yet for SMTP to be scored correctly")
        message = f'''
        From: <{sender}>
        To: <{receivers[0]}>
        Subject: Scoring Message
        
        This message is used to score.
        '''
        smtpobj = smtplib.SMTP(ip, port)
        smtpobj.sendmail(sender, receivers, message)
        status = 1
    except SMTPException:
        status = 0
    except Exception as e:
        log.Error.error(e)
        status = 2
    finally:
        set_score(db, table, status)


def score_dns_linux():
    config = ConfigParser()
    config.read('back_end/config/service.conf')

    ip = config['LINUX_DNS']['ip']
    table = config['LINUX_DNS']['sqltable']
    domains = config['LINUX_DNS']['domains'].split('/')

    db = open_database()

    dns_query = Nslookup(dns_servers=[ip])
    try:
        domain = random.choice(domains)
        answer = dns_query.dns_lookup(domain)
    except Exception as e:
        log.Error.error(e)
    file_name = f'back_end/etc/scoring/{domain}.dns'
    with open(file_name, 'r') as f:
        good_ans = f.read()
        str_ans = f'{answer.answer}\n'
        if good_ans == str_ans:
            set_score(db, table, 1)
        else:
            set_score(db, table, 0)


def score_dns_windows():
    config = ConfigParser()
    config.read('back_end/config/service.conf')

    ip = config['WINDOWS_DNS']['ip']
    table = config['WINDOWS_DNS']['sqltable']
    domains = config['WINDOWS_DNS']['domains'].split('/')

    db = open_database()

    dns_query = Nslookup(dns_servers=[ip])
    try:
        domain = random.choice(domains)
        answer = dns_query.dns_lookup(domain)
    except Exception as e:
        log.Error.error(e)
    file_name = f'back_end/etc/scoring/{domain}.dns'
    with open(file_name, 'r') as f:
        good_ans = f.read()
        str_ans = f'{answer.answer}\n'
        if good_ans == str_ans:
            set_score(db, table, 1)
        else:
            set_score(db, table, 0)


def set_score(db, table, status):
    bool_status = 'Error'
    cursor = db.cursor(buffered=True)
    if status == 1:
        bool_status = 'True'
    elif status == 0:
        bool_status = 'False'
    else:
        bool_status = 'Error'

    log.Scoring.info(f"Just scored {table} with a result of {bool_status}")
    cursor.execute(
        f"INSERT INTO {table} (test_date, success) VALUES (\"{str(datetime.now())}\",\"{str(bool_status)}\")")#, (str(datetime.now()), bool_status))
    db.commit()
    db.close()


def open_database():
    db = None
    config = read_config()
    db = conn.connect(
        host=config['MYSQL_HOST'],
        username=config['MYSQL_USER'],
        password=config['MYSQL_PASSWORD'],
        database='scoring_engine'
    )
    return db


def read_config():
    with open("config/application.conf", 'r') as f:
        content = f.read()
        paths = content.split("\n")
        config_dict = {}
        for path in paths:
            setting = path.split(" = ")
            config_dict[setting[0]] = setting[1].replace('\'', '')

    return config_dict
