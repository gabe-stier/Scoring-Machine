import asyncio
from utilities import Scores as Service
from scoring_functions import Windows_DNS, Linux_DNS, Ecommerce, Splunk, POP3, SMTP, LDAP


async def score_splunk():
    Splunk.score()


async def score_ecomm():
    Ecommerce.score()


async def score_ldap():
    LDAP.score()


async def score_dns_linux():
    Linux_DNS.score()


async def score_dns_windows():
    Windows_DNS.score()


async def score_pop3():
    POP3.score()


async def score_smtp():
    SMTP.score()


def run_task(service: Service):
    if service == Service.DNS_WINDOWS:
        Windows_DNS.score()
    if service == Service.DNS_LINUX:
        Linux_DNS.score()
    if service == Service.SPLUNK:
        Splunk.score()
    if service == Service.ECOMM:
        Ecommerce.score()
    if service == Service.LDAP:
        LDAP.score()
    if service == Service.POP3:
        POP3.score()
    if service == Service.SMTP:
        SMTP.score()
