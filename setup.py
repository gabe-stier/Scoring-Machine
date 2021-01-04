import os
import sys
from platform import system
from subprocess import call

from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install

service_config = '''[LDAP]
IP = 0.0.0.0
PORT = 389
InformationTable = ldap_info
SQLTable = ldap

[SPLUNK]
IP = bing.com
PORT = 80
HashFile = etc/scoring/splunk.sh3
SQLTable = splunk

[ECOMMERCE]
IP = google.com
PORT = 80
HashFile = etc/scoring/ecomm.sh3
SQLTable = ecomm

[POP3]
IP = 0.0.0.0
PORT = 110
SQLTable = pop3
USER = user
PASSWORD = Changeme1!

[SMTP]
IP = 0.0.0.0
PORT = 25
SQLTable = smtp
FROM_USER = admin
TO_USER = user
DOMAIN = team.local

[WINDOWS_DNS]
IP = 8.8.8.8
PORT = 53
SQLTable = dns_windows
DOMAINS = google.com,yahoo.com,bing.com

[LINUX_DNS]
IP = 1.1.1.1
PORT = 53
SQLTable = dns_linux
DOMAINS = google.com,yahoo.com,bing.com
'''
application_config = '''BACK_END_LOCATION = 'localhost:5001'
MYSQL_USER = 'scoring_engine'
MYSQL_PASSWORD = 'Changeme1!'
MYSQL_HOST = '127.0.0.1'
CONFIG_PASSWORD = 'ThisIsAGoodPassword1'
REQUIRE_CONFIG_PASSWORD = 'no'
'''

back_service = '''[Unit]
Description=Scoring Engine Backend
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/engine-back
TimeoutStartSec=0
Restart=on-failure
RestartSec=20s

[Install]
WantedBy=multi-user.target
'''
front_service = '''[Unit]
Description=Scoring Engine Frontend
After=scoring.engine.back.service

[Service]
Type=simple
ExecStart=/usr/local/bin/engine-front
TimeoutStartSec=0
Restart=on-failure
RestartSec=20s

[Install]
WantedBy=multi-user.target
'''


class PreDevelopCommand(develop):
	def run(self):
		if system() == 'Linux':
			self.generate_files()
			develop.run(self)
		else:
			print("Stopping install. Only Linux distro's are supported.")
			sys.exit(1)

	@staticmethod
	def generate_files(self):
		if not os.path.exists('/etc/systemd/system/scoring.engine.back.service'):
			try:
				with open('/etc/systemd/system/scoring.engine.back.service', 'w') as f:
					print(back_service, file=f)
				call('systemclt daemon-reload'.split())
			except OSError as ioe:
				sys.exit("Please run this command as root.")
				return False

		if not os.path.exists('/etc/systemd/system/scoring.engine.front.service'):
			try:
				with open('/etc/systemd/system/scoring.engine.front.service', 'w') as f:
					print(front_service, file=f)
				call('systemclt daemon-reload'.split())
			except OSError:
				sys.exit("Please run this command as root.")
				return False

		if not os.path.exists('/opt/scoring-engine'):
			try:
				os.mkdir('/opt/scoring-engine')
			except OSError:
				sys.exit("Please run this command as root.")

		if not os.path.exists('/opt/scoring-engine/application.conf'):
			try:
				with open('/opt/scoring-engine/application.conf', 'w') as f:
					print(application_config, file=f)

			except PermissionError:
				sys.exit("Please run this command as root.")

		if not os.path.exists('/opt/scoring-engine/service.conf'):
			try:
				with open('/opt/scoring-engine/service.conf', 'w') as f:
					print(service_config, file=f)
			except PermissionError:
				sys.exit("Please run this command as root.")


class PreInstallCommand(install):
	def run(self):
		if system() == 'Linux':
			self.generate_files()
			install.run(self)
		else:
			print("Stopping install. Only Linux distro's are supported.")
			sys.exit(1)

	@staticmethod
	def generate_files():
		if not os.path.exists('/etc/systemd/system/scoring.engine.back.service'):
			with open('/etc/systemd/system/scoring.engine.back.service', 'w') as f:
				print(back_service, file=f)
			call('systemctl daemon-reload'.split())

		if not os.path.exists('/etc/systemd/system/scoring.engine.front.service'):
			with open('/etc/systemd/system/scoring.engine.front.service', 'w') as f:
				print(front_service, file=f)
			call('systemctl daemon-reload'.split())

		if not os.path.exists('/opt/scoring-engine'):
			os.mkdir('/opt/scoring-engine')

		if not os.path.exists('/opt/scoring-engine/application.conf'):
			with open('/opt/scoring-engine/application.conf', 'w') as f:
				print(application_config, file=f)

		if not os.path.exists('/opt/scoring-engine/service.conf'):
			with open('/opt/scoring-engine/service.conf', 'w') as f:
				print(service_config, file=f)


setup(cmdclass={'install': PreInstallCommand})
