import http
import os
import random
import time
from configparser import ConfigParser
from hashlib import sha3_512
from threading import Thread

import mysql.connector as conn
from nslookup import Nslookup

from back_end.scoring_tasks import (score_dns_linux, score_dns_windows,
                                    score_ecomm, score_ldap, score_pop3,
                                    score_smtp, score_splunk)
from back_end.utilities import Loggers as log


def splunk_loop():
    while True:
        random_sleep = random.randint(45, 120)
        log.Scoring.info(
            f'Automated scoring of Splunk. \n\tThere will be a break of {random_sleep} seconds before the next scoring.')
        score_splunk()
        time.sleep(random_sleep)


def ecomm_loop():
    while True:
        random_sleep = random.randint(45, 120)
        log.Scoring.info(
            f'Automated scoring of Ecomm. \n\tThere will be a break of {random_sleep} seconds before the next scoring.')
        score_ecomm()
        time.sleep(random_sleep)


def dns_linux_loop():
    while True:
        random_sleep = random.randint(45, 120)
        log.Scoring.info(
            f'Automated scoring of DNS Linux. \n\tThere will be a break of {random_sleep} seconds before the next scoring.')
        score_dns_linux()
        time.sleep(random_sleep)


def dns_windows_loop():
    while True:

        random_sleep = random.randint(45, 120)
        log.Scoring.info(
            f'Automated scoring of DNS Windows. \n\tThere will be a break of {random_sleep} seconds before the next scoring.')
        score_dns_windows()
        time.sleep(random_sleep)


def smtp_loop():
    while True:
        random_sleep = random.randint(45, 120)
        log.Scoring.info(
            f'Automated scoring of SMTP. \n\tThere will be a break of {random_sleep} seconds before the next scoring.')
        score_smtp()
        time.sleep(random_sleep)


def pop3_loop():
    while True:
        random_sleep = random.randint(45, 120)
        log.Scoring.info(
            f'Automated scoring of POP3. \n\tThere will be a break of {random_sleep} seconds before the next scoring.')
        score_pop3()
        time.sleep(random_sleep)


def ldap_loop():
    while True:
        random_sleep = random.randint(45, 120)
        log.Scoring.info(
            f'Automated scoring of LDAP. \n\tThere will be a break of {random_sleep} seconds before the next scoring.')
        score_ldap()
        time.sleep(random_sleep)


def read_config():
    with open("config/application.conf", 'r') as f:
        content = f.read()
        paths = content.split("\n")
        config_dict = {}
        for path in paths:
            setting = path.split(" = ")
            config_dict[setting[0]] = setting[1].replace('\'', '')

    return config_dict


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


def init_db():
    config = read_config()
    db = conn.connect(
        host=config['MYSQL_HOST'],
        username=config['MYSQL_USER'],
        password=config['MYSQL_PASSWORD']
    )
    cur = db.cursor()
    cur.execute('CREATE DATABASE IF NOT EXISTS scoring_engine')
    with open(f'{os.getcwd()}/sql/basic_db.sql') as f:
        schema = f.read()
        # results =
        cur.execute(schema, multi=True)
        # for result in results:
        #     result
    with open(f'{os.getcwd()}/sql/views.sql') as f:
        schema = f.read()
        # results =
        cur.execute(schema, multi=True)
        # for result in results:
        #     result
    db.commit()
    db.close()


def build_defaults():
    print('Creating Defaults')
    config = ConfigParser()
    config.read('back_end/config/service.conf')

    dns_ip = config['WINDOWS_DNS']['ip']
    domains = config['WINDOWS_DNS']['domains'].split('/')
    print('Creating Default of DNS')
    try:
        dns_query = Nslookup(dns_servers=[dns_ip])
        log.Main.info('Setting the base!')
        for domain in domains:
            file_name = f'back_end/etc/scoring/{domain}.dns'
            if not (os.path.exists(file_name) and os.stat(file_name).st_size != 0):
                answer = dns_query.dns_lookup(domain)
                with open(file_name, 'w+') as f:
                    f.write(f'{answer.answer}\n')
    except Exception as e:
        log.Error.error(e)
        print(e)

    splunk_ip = config['SPLUNK']['ip']
    splunk_port = config['SPLUNK']['port']
    splunk_hash_file = config['SPLUNK']['hashfile']
    print('Creating Default of Splunk')

    try:
        site = http.client.HTTPConnection(splunk_ip, splunk_port, timeout=5)
        site.request('GET', '/')
        site_response = site.getresponse()
        site.close()
        site_string = f'{site_response.getheaders()[0]}\n\nStatus: {site_response.status}\n\n{site_response.read()}'
        site_hash = sha3_512()
        site_hash.update(site_string.encode())
        f = open(f'{os.getcwd()}/back_end/{splunk_hash_file}', 'w+')
        f.write(site_hash.hexdigest())
        f.close()
    except Exception as e:
        log.Error.error(e)

    ecomm_ip = config['ECOMMERCE']['ip']
    ecomm_port = config['ECOMMERCE']['port']
    ecomm_hash_file = config['ECOMMERCE']['hashfile']
    print('Creating Default of Ecommerce')

    try:
        site = http.client.HTTPConnection(ecomm_ip, ecomm_port, timeout=5)
        site.request('GET', '/')
        site_response = site.getresponse()
        site.close()
        site_string = f'{site_response.getheaders()[0]}\n\nStatus: {site_response.status}\n\n{site_response.read()}'
        site_hash = sha3_512()
        site_hash.update(site_string.encode())
        f = open(f'{os.getcwd()}/back_end/{ecomm_hash_file}', 'w+')
        f.write(site_hash.hexdigest())
        f.close()
    except Exception as e:
        log.Error.error(e)


def start_scoring():
    init_db()
    build_defaults()

    def start_threads():
        splunk_thread = Thread(target=splunk_loop)
        ecomm_thread = Thread(target=ecomm_loop)
        ldap_thread = Thread(target=ldap_loop)
        dnsw_thread = Thread(target=dns_windows_loop)
        dnsl_thread = Thread(target=dns_linux_loop)
        pop3_thread = Thread(target=pop3_loop)
        smtp_thread = Thread(target=smtp_loop)

        splunk_thread.start()
        ecomm_thread.start()
        ldap_thread.start()
        dnsw_thread.start()
        dnsl_thread.start()
        pop3_thread.start()
        smtp_thread.start()
    # start_threads()
