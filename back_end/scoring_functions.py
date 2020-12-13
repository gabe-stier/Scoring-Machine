'''
Created on Nov 26, 2020

@author: gabez
'''

from back_end.service import LDAP as ldap
from back_end.service import Authentication, Web, DNS
from back_end.service import SMTP as SMTP_class
from back_end.service import POP3 as POP3_class
from back_end.utilities import Loggers as log

from configparser import ConfigParser
import os

Windows_DNS = DNS()
Linux_DNS = DNS()
Ecommerce = Web()
Splunk = Web()
POP3 = POP3_class()
SMTP = SMTP_class()
LDAP = ldap()
Auth = Authentication()


def set_service_config():
    config = ConfigParser()
    try:
        config.read('back_end/config/service.conf')
        
        ldap_config = config['LDAP']
        splunk_config = config['SPLUNK']
        ecommerce_config = config['ECOMMERCE']
        pop3_config = config['POP3']
        smtp_config = config['SMTP']
        wdns_config = config['WINDOWS_DNS']
        ldns_config = config['LINUX_DNS']
        auth_config = config['CONFIGURATION']

        LDAP.set_ip(ldap_config['ip'])
        LDAP.set_port(ldap_config['port'])
        LDAP.set_table(ldap_config['sqltable'])
        LDAP.set_info(ldap_config['informationtable'])

        Splunk.set_ip(splunk_config['ip'])
        Splunk.set_port(splunk_config['port'])
        Splunk.set_table(splunk_config['sqltable'])
        Splunk.set_hash(splunk_config['hashfile'])

        Ecommerce.set_ip(ecommerce_config['ip'])
        Ecommerce.set_port(ecommerce_config['port'])
        Ecommerce.set_table(ecommerce_config['sqltable'])
        Ecommerce.set_hash(ecommerce_config['hashfile'])

        SMTP.set_ip(smtp_config['ip'])
        SMTP.set_port(smtp_config['port'])
        SMTP.set_table(smtp_config['sqltable'])
        SMTP.set_info(smtp_config['informationtable'])

        POP3.set_ip(pop3_config['ip'])
        POP3.set_port(pop3_config['port'])
        POP3.set_table(pop3_config['sqltable'])
        POP3.set_info(pop3_config['informationtable'])

        Windows_DNS.set_ip(wdns_config['ip'])
        Windows_DNS.set_port(wdns_config['port'])
        Windows_DNS.set_table(wdns_config['sqltable'])
        Windows_DNS.set_domains(wdns_config['domains'])   

        Linux_DNS.set_ip(ldns_config['ip'])
        Linux_DNS.set_port(ldns_config['port'])
        Linux_DNS.set_table(ldns_config['sqltable'])
        Linux_DNS.set_domains(ldns_config['domains'])

        Auth.set_pwd(auth_config['adminpassword'])
        Auth.set_require(auth_config['requirepassword'])
        save_service_config()
    except Exception as e:
        print(e, "ERROR", flush=True)
        log.Error.error(e)


def save_service_config():
    config = ConfigParser()

    config['LDAP'] = {
        'IP': LDAP.get_ip(),
        'PORT': LDAP.get_port(),
        'InformationTable': LDAP.get_info(),
        'SQLTable': LDAP.get_table()
    }

    config['SPLUNK'] = {
        'IP': Splunk.get_ip(),
        'PORT': Splunk.get_port(),
        'HashFile': Splunk.get_hash(),
        'SQLTable': Splunk.get_table()
    }

    config['ECOMMERCE'] = {
        'IP': Ecommerce.get_ip(),
        'PORT': Ecommerce.get_port(),
        'HashFile': Ecommerce.get_hash(),
        'SQLTable': Ecommerce.get_table()
    }

    config['POP3'] = {
        'IP': POP3.get_ip(),
        'PORT': POP3.get_port(),
        'InformationTable': POP3.get_info(),
        'SQLTable': POP3.get_table()
    }

    config['SMTP'] = {
        'IP': SMTP.get_ip(),
        'PORT': SMTP.get_port(),
        'InformationTable': SMTP.get_info(),
        'SQLTable': SMTP.get_table()
    }

    config['WINDOWS_DNS'] = {
        'IP': Windows_DNS.get_ip(),
        'PORT': Windows_DNS.get_port(),
        'SQLTable': Windows_DNS.get_table(),
        'DOMAINS': Windows_DNS.get_domains().join('/')
    }

    config['LINUX_DNS'] = {
        'IP': Linux_DNS.get_ip(),
        'PORT': Linux_DNS.get_port(),
        'SQLTable': Linux_DNS.get_table(),
        'DOMAINS': Linux_DNS.get_domains().join('/')
    }

    config['CONFIGURATION'] = {
        'AdminPassword': Auth.get_pwd(),
        'RequirePassword': Auth.get_require()
    }

    with open('back_end/service.conf', 'w') as file:
        config.write(file)
