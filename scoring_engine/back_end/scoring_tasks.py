import http
import poplib
import random
import smtplib
from configparser import ConfigParser
from datetime import datetime
from hashlib import sha3_512
from smtplib import SMTPException
from socket import timeout

import ldap
import mysql.connector as conn
from ldap import AUTH_UNKNOWN, CONNECT_ERROR
from nslookup import Nslookup

from scoring_engine.back_end.utilities import Loggers as log, read_config


def score_splunk():
	"""Scores Splunk"""
	config = ConfigParser()
	config.read('/opt/scoring-engine/service.conf')
	log.Scoring.info('Attempting to score Splunk.')
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
		with open(f'/opt/scoring-engine/score-baseline/{hash_file}', 'r') as f:
			good_hash = f.read()
			if good_hash == site_hash.hexdigest():
				set_score(db, table_name, 1)
				log.Scoring.info('Score of Splunk returned with a "Success"')
			else:
				set_score(db, table_name, 0)
				log.Scoring.info('Score of Splunk returned with a "Fail"')
	except timeout:
		set_score(db, table_name, 0)
	except Exception as e:
		set_score(db, table_name, 2)
		log.Scoring.info('Score of Splunk returned with an "Error"')
		log.Error.error(e)


def get_ldap_info():
	"""Gets user information to test ldap connection"""
	db = open_database()
	cur = db.cursor(buffered=True)
	cur.execute('SELECT username, password FROM ldap_info')
	users = cur.fetchall()
	if users is not None:
		user = random.choice(users)
	else:
		user = None
	log.Scoring.info(f'Scoring LDAP with the user account of {user}')
	db.close()
	return user


def score_ldap():
	"""Scores LDAP"""
	status = 0
	config = ConfigParser()
	config.read('/opt/scoring-engine/service.conf')
	log.Scoring.info('Attempting to score LDAP')

	ip = config['LDAP']['ip']
	table = config['LDAP']['SQLTable']

	try:
		connection = ldap.initialize(f'ldap://{ip}')
		connection.set_option(ldap.OPT_REFERRALS, 0)
		user = get_ldap_info()
		db = open_database()
		if user is None:
			raise Exception(
					"Configuration has not been set yet for LDAP to be scored correctly")
		connection.simple_bind_s(user[0], user[1])
		status = 1
		log.Scoring.info('Score of LDAP returned with a "Success"')
	except AUTH_UNKNOWN:
		status = 0
		log.Scoring.info('Score of LDAP returned with a "Fail"')
	except CONNECT_ERROR:
		status = 0
		log.Scoring.info('Score of LDAP returned with a "Fail"')
	except Exception as e:
		log.Error.error(e)
		status = 2
		log.Scoring.info('Score of LDAP returned with an "Error"')
	finally:
		set_score(db, table, status)


def score_ecomm():
	"""Scores Ecomm"""
	config = ConfigParser()
	config.read('/opt/scoring-engine/service.conf')
	log.Scoring.info('Attempting to score Ecommerce')

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
		with open(f'/opt/scoring-engine/score-baseline/{hash_file}', 'r') as f:
			good_hash = f.read()
			if good_hash == site_hash.hexdigest():
				set_score(db, table_name, 1)
				log.Scoring.info(
						'Score of Ecommerce returned with a "Success"')
			else:
				set_score(db, table_name, 0)
				log.Scoring.info('Score of Ecommerce returned with a "Fail"')
	except timeout:
		set_score(db, table_name, 0)
		log.Scoring.info('Score of Ecommerce returned with a "Fail"')
	except Exception as e:
		set_score(db, table_name, 2)
		log.Scoring.info('Score of Ecommerce returned with an "Error"')
		log.Error.error(e)


def score_pop3():
	"""Scores POP3"""
	db = open_database()
	config = ConfigParser()
	config.read('/opt/scoring-engine/service.conf')
	log.Scoring.info('Attempting to score POP3')

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
			log.Scoring.info('Score of POP3 returned with a "Success"')
		else:
			status = 0
			log.Scoring.info('Score of POP3 returned with a "Fail"')
		pop.quit()
	except Exception as e:
		status = 2
		log.Scoring.info('Score of POP3 returned with an "Error"')
		log.Error.error(e)
	finally:
		set_score(db, table_name, status)


def score_smtp():
	"""Scores SMTP"""
	try:
		db = open_database()
		config = ConfigParser()
		config.read('/opt/scoring-engine/service.conf')
		log.Scoring.info('Attempting to score SMTP')

		sender = f"{config['SMTP']['from_user']}@{config['SMTP']['domain']}"
		ip = config['SMTP']['ip']
		port = config['SMTP']['port']
		table = config['SMTP']['SQLTable']
		receiver = f"{config['SMTP']['to_user']}@{config['SMTP']['domain']}"

		message = f"""From: <{sender}>
        To: <{receiver}>
        Subject: Scoring Message
        
        This message is used to score.
        """
		smtpobj = smtplib.SMTP(ip, port)
		smtpobj.sendmail(sender, receiver, message)
		smtpobj.quit()
		status = 1
		log.Scoring.info('Score of SMTP returned with a "Success"')
	except SMTPException:
		status = 0
		log.Scoring.info('Score of SMTP returned with a "Fail"')
	except Exception as e:
		log.Error.error(e)
		status = 2
		log.Scoring.info('Score of SMTP returned with an "Error"')
	finally:
		set_score(db, table, status)


def score_dns_linux():
	"""Scores Linux DNS"""
	config = ConfigParser()
	config.read('/opt/scoring-engine/service.conf')
	log.Scoring.info('Attempting to score Linux DNS')

	ip = config['LINUX_DNS']['ip']
	table = config['LINUX_DNS']['sqltable']
	domains = config['LINUX_DNS']['domains'].split(',')

	db = open_database()

	dns_query = Nslookup(dns_servers=[ip])
	try:
		domain = random.choice(domains)
		answer = dns_query.dns_lookup(domain)
		file_name = f'/opt/scoring-engine/score-baseline/{domain}.dns'
		with open(file_name, 'r') as f:
			good_ans = f.read()
			str_ans = f'{answer.answer}\n'
			if good_ans == str_ans:
				set_score(db, table, 1)
				log.Scoring.info(
						'Score of Linux DNS returned with a "Success"')
			else:
				set_score(db, table, 0)
				log.Scoring.info('Score of Linux DNS returned with a "Fail"')
	except Exception as e:
		log.Error.error(e)
		set_score(db, table, 2)
		log.Scoring.info('Score of Linux DNS returned with an "Error"')


def score_dns_windows():
	"""Scores Windows DNS"""
	config = ConfigParser()
	config.read('/opt/scoring-engine/service.conf')
	log.Scoring.info('Attempting to score Windows DNS')

	ip = config['WINDOWS_DNS']['ip']
	table = config['WINDOWS_DNS']['sqltable']
	domains = config['WINDOWS_DNS']['domains'].split(',')

	db = open_database()

	dns_query = Nslookup(dns_servers=[ip])
	try:
		domain = random.choice(domains)
		answer = dns_query.dns_lookup(domain)
		file_name = f'/opt/scoring-engine/score-baseline/{domain}.dns'
		with open(file_name, 'r') as f:
			good_ans = f.read()
			str_ans = f'{answer.answer}\n'
			if good_ans == str_ans:
				set_score(db, table, 1)
				log.Scoring.info(
						'Score of Windows DNS returned with a "Success"')
			else:
				set_score(db, table, 0)
				log.Scoring.info('Score of Windows DNS returned with a "Fail"')
	except Exception as e:
		log.Error.error(e)
		set_score(db, table, 2)
		log.Scoring.info('Score of Windows DNS returned with an "Error"')


def set_score(db, table, status):
	"""Connection to the database.
	Sets the score in the database."""
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
			f"INSERT INTO {table} (test_date, success) VALUES (\"{str(datetime.now())}\",\"{str(bool_status)}\")")  # , (str(datetime.now()), bool_status))
	db.commit()
	db.close()


def open_database():
	"""Creates a connection to the database used to store the scores."""
	log.Main.debug('Attempting to open connection to database to update scores.')
	db = None
	try:
		config = read_config()
		db = conn.connect(
				host=config['MYSQL_HOST'],
				username=config['MYSQL_USER'],
				password=config['MYSQL_PASSWORD'],
				database='scoring_engine'
				)
	except Exception as e:
		log.Error.error(e)
		log.Main.debug('Failed to connecto to database.')
	finally:
		return db
