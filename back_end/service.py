from datetime import datetime
from hashlib import sha3_512
from nslookup import Nslookup
import random
import os
import http
import smtplib
import ldap
from ldap import AUTH_UNKNOWN

import scoring_functions as score
from utilities import db
from utilities import Loggers as log
from socket import timeout
from smtplib import SMTPException
import poplib


class Scoring:

    last_scored = datetime.now()
    table_name = ""
    ip = ""
    port = ""

    def __init__(self, table_name=None, ip=None, port=None):
        self.ip = ip
        self.port = port

    def get_last_scored(self):
        return self.last_scored

    def get_ip(self):
        return self.ip

    def get_port(self):
        return self.port

    def get_table(self):
        return self.table_name

    def set_table(self, table):
        self.table_name = table

    def set_ip(self, ip):
        self.ip = ip

    def set_port(self, port):
        self.port = port

    def set_last_scored(self, date):
        self.last_scored = date

    def score(self):
        self.last_scored = datetime.now()

    def add_status(self, table, status):
        bool_status = 'Error'
        if status == 1:
            bool_status = 'True'
        elif status == 0:
            bool_status = 'False'
        else:
            bool_status = 'Error'

        log.Scoring.info(
            f"Just scored {table} with a result of {bool_status}")
        db.insert_score(
            f'INSERT INTO {table} (test_date, success) VALUES ("{str(self.last_scored)}","{bool_status}")')


class DNS(Scoring):
    domains = []

    def __init__(self, *args, **kargs):
        Scoring.__init__(self, *args, **kargs)

    def score(self):
        Scoring.score(self)
        dns_query = Nslookup(dns_servers=[self.ip])
        log.Main.info('Show Domains')
        log.Main.info(self.domains)
        log.Main.info('End Domains')
        try:
            domain = random.choice(self.domains)
            answer = dns_query.dns_lookup(domain)
        except Exception as e:
            log.Error.error(e)
        file_name = f'back_end/etc/scoring/{domain}.dns'
        self.set_base()
        with open(file_name, 'r') as f:
            good_ans = f.read()
            str_ans = f'{answer.answer}\n'
            if good_ans == str_ans:
                self.add_status(self.table_name, 1)
            else:
                self.add_status(self.table_name, 0)

    def set_base(self):
        dns_query = Nslookup(dns_servers=[self.ip])
        log.Main.info('Setting the base!')
        for domain in self.domains:
            file_name = f'back_end/etc/scoring/{domain}.dns'
            if not (os.path.exists(file_name) and os.stat(file_name).st_size != 0):
                answer = dns_query.dns_lookup(domain)
                with open(file_name, 'w+') as f:
                    f.write(f'{answer.answer}\n')

    def set_domains(self, domains):
        self.domains = domains.split('/')

    def get_domains(self):
        return ';'.join(self.domains)


class SMTP(Scoring):

    info_table = None
    email_from = ''

    def __init__(self, *args, **kargs):
        Scoring.__init__(self, *args, **kargs)

    def set_info(self, file):
        self.info_table = file

    def get_info(self):
        return self.info_table

    def set_from(self, email):
        self.email_from = email

    def get_from(self):
        return self.email_from

    def score(self):
        try:
            Scoring.score(self)
            sender = score.SMTP.get_from()
            receivers = db.get_smtp_info()
            if receivers is None:
                raise Exception("Configuration has not been set yet for SMTP to be scored correctly")
            message = f'''
            From: <{sender}>
            To: <{receivers[0]}>
            Subject: Scoring Message
            
            This message is used to score.
            '''
            smtpobj = smtplib.SMTP(self.ip, self.port)
            smtpobj.sendmail(sender, receivers, message)
            status = 1
        except SMTPException:
            status = 0
        except Exception as e:
            log.Error.error(e)
            status = 2
        finally:
            self.add_status(self.table_name, status)


class POP3(Scoring):

    info_table = None

    def __init__(self, *args, **kargs):
        Scoring.__init__(self, *args, **kargs)

    def set_info(self, table):
        self.info_table = table

    def get_info(self):
        return self.info_table

    def score(self):
        Scoring.score(self)
        status = 0
        try:
            pop = poplib.POP3(self.ip, self.port)
            user = db.get_pop3_info()
            if user is None:
                raise Exception("Configuration has not been set yet for POP3 to be scored correctly")
            pop.user(user[0])
            pop.pass_(user[1])
            email_number = random.randint(0, pop.stat())
            (msg, body, octets) = pop.retr(email_number)
            if f'From: {score.SMTP.get_from()}' in body:
                status = 1
            else:
                status = 0
            pop.quit()
        except Exception:
            status = 2
            log.Error.error(e)
        finally:
            self.add_status(self.table_name, status)


class LDAP(Scoring):

    information_table = None

    def __init__(self, *args, **kargs):
        Scoring.__init__(self, *args, **kargs)
        pass

    def set_info(self, info):
        self.information_table = info

    def get_info(self):
        return self.information_table

    def score(self):
        Scoring.score(self)
        status = 0
        try:
            connection = ldap.initialize(f'ldap://{self.ip}')
            connection.set_option(ldap.OPT_REFERRALS, 0)
            user = db.get_ldap_info()
            if user is None:
                raise Exception("Configuration has not been set yet for LDAP to be scored correctly")
            connection.simple_bind_s(user[0], user[1])
            status = 1
        except AUTH_UNKNOWN:
            status = 0
        except Exception as e:
            log.Error.error(e)
            status = 2
            print(e)
        finally:
            self.add_status('ldap', status)
        pass


class Web(Scoring):

    hash_file = 'etc/scoring'

    def __init__(self, *args, **kargs):
        Scoring.__init__(self, *args, **kargs)

    def set_hash(self, file):
        self.hash_file = file

    def get_hash(self):
        return self.hash_file

    def score(self):
        Scoring.score(self)
        try:
            site = http.client.HTTPConnection(self.ip, self.port, timeout=5)
            site.request('GET', '/')
            site_response = site.getresponse()
            site.close()
            site_string = f'{site_response.getheaders()[0]}\n\nStatus: {site_response.status}\n\n{site_response.read()}'
            site_hash = sha3_512()
            site_hash.update(site_string.encode())
            self.set_base()
            with open(f'back_end/{self.hash_file}', 'r') as f:
                good_hash = f.read()
                if good_hash == site_hash.hexdigest():
                    self.add_status(self.table_name, 1)
                else:
                    self.add_status(self.table_name, 0)
        except timeout as te:
            self.add_status(self.table_name, 0)
        except Exception as e:
            log.Error.error(e)

    def set_base(self):
        try:
            site = http.client.HTTPConnection(self.ip, self.port, timeout=5)
            site.request('GET', '/')
            site_response = site.getresponse()
            site.close()
            site_string = f'{site_response.getheaders()[0]}\n\nStatus: {site_response.status}\n\n{site_response.read()}'
            site_hash = sha3_512()
            site_hash.update(site_string.encode())
            f = open(f'back_end/{self.hash_file}', 'w+')
            f.write(site_hash.hexdigest())
            f.close()
        except timeout as te:
            self.add_status(self.table_name, 0)
        except Exception as e:
            log.Error.error(e)
