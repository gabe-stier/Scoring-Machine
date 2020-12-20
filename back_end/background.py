from threading import Thread
import time
import tasks
import random
from utilities import Loggers as log
from utilities import Scores as Service
from tasks import run_task


def splunk_loop():
    while True:
        log.Scoring.info('Automated scoring of Splunk.')
        run_task(Service.SPLUNK)
        random_sleep = random.randint(45, 120)
        time.sleep(random_sleep)


def ecomm_loop():
    while True:
        log.Scoring.info('Automated scoring of Ecomm.')
        run_task(Service.ECOMM)
        random_sleep = random.randint(45, 120)
        time.sleep(random_sleep)


def dns_linux_loop():
    while True:
        log.Scoring.info('Automated scoring of DNS Linux.')
        run_task(Service.DNS_LINUX)
        random_sleep = random.randint(45, 120)
        time.sleep(random_sleep)


def dns_windows_loop():
    while True:
        log.Scoring.info('Automated scoring of DNS Windows.')
        run_task(Service.DNS_WINDOWS)
        random_sleep = random.randint(45, 120)
        time.sleep(random_sleep)


def smtp_loop():
    while True:
        log.Scoring.info('Automated scoring of SMTP.')
        run_task(Service.SMTP)
        random_sleep = random.randint(45, 120)
        time.sleep(random_sleep)


def pop3_loop():
    while True:
        log.Scoring.info('Automated scoring of POP3.')
        run_task(Service.POP3)
        random_sleep = random.randint(45, 120)
        time.sleep(random_sleep)


def ldap_loop():
    while True:
        log.Scoring.info('Automated scoring of LDAP.')
        run_task(Service.LDAP)
        random_sleep = random.randint(45, 120)
        time.sleep(random_sleep)


def start_scoring():
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
