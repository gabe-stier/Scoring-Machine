import http
import os
from configparser import ConfigParser
from hashlib import sha3_512

import mysql.connector as conn
from nslookup import Nslookup

from scoring_engine.back_end.utilities import Loggers as log, read_config


def __config_task(config):
	"""Writes config to file"""
	new_file_name = f'/opt/scoring-engine/service.conf.new'
	old_file_name = f'/opt/scoring-engine/service.conf'
	with open(new_file_name, 'w') as new_file:
		config.write(new_file)
	os.rename(new_file_name, old_file_name)


def config_splunk(ip: str, port: int):
	"""Updates the splunk section of the config"""
	log.Main.info('Updating Configuration of Splunk')
	old_file_name = f'/opt/scoring-engine/service.conf'
	config = ConfigParser()
	config.read(old_file_name)
	config['SPLUNK']['ip'] = ip
	config['SPLUNK']['port'] = port
	__config_task(config)
	__set_splunk_default()


def config_ecomm(ip: str, port: int):
	"""Updates the ecomm section of the config"""
	log.Main.info('Updating Configuration of Ecommerce')
	old_file_name = f'/opt/scoring-engine/service.conf'
	config = ConfigParser()
	config.read(old_file_name)
	config['ECOMMERCE']['ip'] = ip
	config['ECOMMERCE']['port'] = port
	__config_task(config)
	__set_ecomm_default()


def config_ldap(ip: str, users: list):
	"""Updates the ldap section of the config"""
	log.Main.info('Updating Configuration of LDAP')
	old_file_name = f'/opt/scoring-engine/service.conf'
	config = ConfigParser()
	config.read(old_file_name)
	config['LDAP']['ip'] = ip
	user_lists = []
	for user in users:
		user_lists.append((user['username'], user['password']))
	db = open_database()
	cur = db.cursor(buffered=True)
	cur.execute("TRUNCATE ldap_info")
	cur.executemany(
			"INSERT INTO ldap_info (`username`, `password`) VALUES (%s, %s)", user_lists)
	db.commit()
	db.close()
	__config_task(config)


def config_smtp(ip: str, user_1: str, user_1_pwd: str, user_2: str, domain: str):
	"""Updates the smtp section of the config"""
	log.Main.info('Updating Configuration of SMTP')
	old_file_name = f'/opt/scoring-engine/service.conf'
	config = ConfigParser()
	config.read(old_file_name)
	config['SMTP']['ip'] = ip
	config['SMTP']['from_user'] = user_1
	config['SMTP']['from_user_password'] = user_1_pwd
	config['SMTP']['to_user'] = user_2
	config['SMTP']['domain'] = domain
	__config_task(config)


def config_pop3(ip: str, username: str, password: str):
	"""Updates the pop3 section of the config"""
	log.Main.info('Updating Configuration of POP3')
	old_file_name = f'/opt/scoring-engine/service.conf'
	config = ConfigParser()
	config.read(old_file_name)
	config['POP3']['ip'] = ip
	config['POP3']['user'] = username
	config['POP3']['password'] = password
	__config_task(config)


def config_dns_windows(ip: str, domains: list):
	"""Updates the Windows DNS section of the config"""
	log.Main.info('Updating Configuration of Windows DNS')
	old_file_name = f'/opt/scoring-engine/service.conf'
	config = ConfigParser()
	config.read(old_file_name)
	config['WINDOWS_DNS']['ip'] = ip
	config['WINDOWS_DNS']['domains'] = ','.join(domains)
	__config_task(config)
	__set_dns_windows_default()


def config_dns_linux(ip: str, domains: list):
	"""Updates the Linux DNS section of the config"""
	log.Main.info('Updating Configuration of Linux DNS')
	old_file_name = f'/opt/scoring-engine/service.conf'
	config = ConfigParser()
	config.read(old_file_name)
	config['LINUX_DNS']['ip'] = ip
	config['LINUX_DNS']['domains'] = ','.join(domains)
	__config_task(config)
	__set_dns_linux_default()


def open_database():
	"""Creates a connection to the database used to store the scores."""
	config = read_config()
	db = conn.connect(
			host=config['MYSQL_HOST'],
			username=config['MYSQL_USER'],
			password=config['MYSQL_PASSWORD'],
			database='scoring_engine'
			)
	return db


def __set_splunk_default():
	"""Sets the defaults after an update occurs"""
	config = ConfigParser()
	config.read('/opt/scoring-engine/service.conf')

	splunk_ip = config['SPLUNK']['ip']
	splunk_port = config['SPLUNK']['port']
	splunk_hash_file = config['SPLUNK']['hashfile']
	log.Main.info('Creating Default of Splunk')

	try:
		site = http.client.HTTPConnection(splunk_ip, splunk_port, timeout=5)
		site.request('GET', '/')
		site_response = site.getresponse()
		site.close()
		site_string = f'{site_response.getheaders()[0]}\n\nStatus: {site_response.status}\n\n{site_response.read()}'
		site_hash = sha3_512()
		site_hash.update(site_string.encode())
		f = open(f'/opt/scoring-engine/score-baseline/{splunk_hash_file}', 'w')
		f.write(site_hash.hexdigest())
		f.close()
	except Exception as e:
		log.Error.error(e)


def set_defaults():
	__set_splunk_default()
	__set_dns_linux_default()
	__set_dns_windows_default()
	__set_ecomm_default()


def __set_dns_linux_default():
	"""Sets the defaults after an update occurs"""
	config = ConfigParser()
	config.read('/opt/scoring-engine/service.conf')

	dns_ip = config['LINUX_DNS']['ip']
	domains = config['LINUX_DNS']['domains'].split(',')
	log.Main.info('Creating Default of DNS')
	try:
		dns_query = Nslookup(dns_servers=[dns_ip])
		log.Main.info('Setting the base!')
		for domain in domains:
			file_name = f'/opt/scoring-engine/score-baseline/{domain}.dns'
			if not (os.path.exists(file_name) and os.stat(file_name).st_size != 0):
				answer = dns_query.dns_lookup(domain)
				with open(file_name, 'w') as f:
					f.write(f'{answer.answer}\n')
	except Exception as e:
		log.Error.error(e)


def __set_dns_windows_default():
	"""Sets the defaults after an update occurs"""
	config = ConfigParser()
	config.read('/opt/scoring-engine/service.conf')

	dns_ip = config['WINDOWS_DNS']['ip']
	domains = config['WINDOWS_DNS']['domains'].split(',')
	log.Main.info('Creating Default of DNS')
	try:
		dns_query = Nslookup(dns_servers=[dns_ip])
		log.Main.info('Setting the base!')
		for domain in domains:
			file_name = f'/opt/scoring-engine/score-baseline/{domain}.dns'
			if not (os.path.exists(file_name) and os.stat(file_name).st_size != 0):
				answer = dns_query.dns_lookup(domain)
				with open(file_name, 'w') as f:
					f.write(f'{answer.answer}\n')
	except Exception as e:
		log.Error.error(e)


def __set_ecomm_default():
	"""Sets the defaults after an update occurs"""
	config = ConfigParser()
	config.read('/opt/scoring-engine/service.conf')

	ecomm_ip = config['ECOMMERCE']['ip']
	ecomm_port = config['ECOMMERCE']['port']
	ecomm_hash_file = config['ECOMMERCE']['hashfile']
	log.Main.info('Creating Default of Ecommerce')

	try:
		site = http.client.HTTPConnection(ecomm_ip, ecomm_port, timeout=5)
		site.request('GET', '/')
		site_response = site.getresponse()
		site.close()
		site_string = f'{site_response.getheaders()[0]}\n\nStatus: {site_response.status}\n\n{site_response.read()}'
		site_hash = sha3_512()
		site_hash.update(site_string.encode())
		f = open(f'/opt/scoring-engine/score-baseline/{ecomm_hash_file}', 'w')
		f.write(site_hash.hexdigest())
		f.close()
	except Exception as e:
		log.Error.error(e)
