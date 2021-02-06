"""The location of that background threads. These threads run anywhere between 45 seconds to 2 minutes."""
import random
import time
from threading import Thread

import mysql.connector as conn
import pkg_resources

from scoring_engine.back_end.config_tasks import (
	__set_dns_windows_default, __set_ecomm_default, __set_splunk_default,
	__set_dns_linux_default)
from scoring_engine.back_end.scoring_tasks import (
	score_dns_linux, score_dns_windows,
	score_ecomm, score_pop3,
	score_smtp, score_splunk)
from scoring_engine.back_end.utilities import Loggers as log, read_config


def splunk_loop():
	"""Loop that scores Splunk"""
	while True:
		random_sleep = random.randint(45, 120)
		log.Scoring.info(
				f'Automated scoring of Splunk. \n\tThere will be a break of {random_sleep} seconds before the next scoring.')
		score_splunk()
		time.sleep(random_sleep)


def ecomm_loop():
	"""Loop that scores Ecommerce"""
	while True:
		random_sleep = random.randint(45, 120)
		log.Scoring.info(
				f'Automated scoring of Ecomm. \n\tThere will be a break of {random_sleep} seconds before the next scoring.')
		score_ecomm()
		time.sleep(random_sleep)


def dns_linux_loop():
	"""Loop that scores Linux DNS"""
	while True:
		random_sleep = random.randint(45, 120)
		log.Scoring.info(
				f'Automated scoring of DNS Linux. \n\tThere will be a break of {random_sleep} seconds before the next scoring.')
		score_dns_linux()
		time.sleep(random_sleep)


def dns_windows_loop():
	"""Loop that scores Windows DNS"""
	while True:

		random_sleep = random.randint(45, 120)
		log.Scoring.info(
				f'Automated scoring of DNS Windows. \n\tThere will be a break of {random_sleep} seconds before the next scoring.')
		score_dns_windows()
		time.sleep(random_sleep)


def smtp_loop():
	"""Loop that scores SMTP"""
	while True:
		random_sleep = random.randint(45, 120)
		log.Scoring.info(
				f'Automated scoring of SMTP. \n\tThere will be a break of {random_sleep} seconds before the next scoring.')
		score_smtp()
		time.sleep(random_sleep)


def pop3_loop():
	"""Loop that scores POP3"""
	while True:
		random_sleep = random.randint(45, 120)
		log.Scoring.info(
				f'Automated scoring of POP3. \n\tThere will be a break of {random_sleep} seconds before the next scoring.')
		score_pop3()
		time.sleep(random_sleep)



def open_database():
	"""Creates a connection to the database used to store the scores."""
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
	"""Connects to the MySQL database and creates all of the needed tables"""
	config = read_config()
	db = conn.connect(
			host=config['MYSQL_HOST'],
			username=config['MYSQL_USER'],
			password=config['MYSQL_PASSWORD']
			)
	cur = db.cursor()
	cur.execute('CREATE DATABASE IF NOT EXISTS scoring_engine')
	results = cur.execute(pkg_resources.resource_string(__name__, '../sql/basic_db.sql'), multi=True)
	for result in results:
		result
	results = cur.execute(pkg_resources.resource_string(__name__, '../sql/views.sql'), multi=True)
	for result in results:
		result
	db.commit()
	db.close()


def build_defaults():
	"""Creates the scoring objectives of DNS, Splunk, and Ecomm"""
	log.Main.info('Creating Defaults')
	__set_dns_linux_default()
	__set_dns_windows_default()
	__set_splunk_default()
	__set_ecomm_default()


def start_scoring():
	"""Thread Controller"""
	init_db()
	build_defaults()

	def start_threads():
		splunk_thread = Thread(target=splunk_loop)
		ecomm_thread = Thread(target=ecomm_loop)
		dnsw_thread = Thread(target=dns_windows_loop)
		dnsl_thread = Thread(target=dns_linux_loop)
		pop3_thread = Thread(target=pop3_loop)
		smtp_thread = Thread(target=smtp_loop)

		splunk_thread.start()
		ecomm_thread.start()
		dnsw_thread.start()
		dnsl_thread.start()
		pop3_thread.start()
		smtp_thread.start()

	start_threads()
