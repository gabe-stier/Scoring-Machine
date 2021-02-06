import os
import sys
from platform import system
from subprocess import call

from setuptools import setup
from setuptools.command.install import install

service_config = """[SPLUNK]
IP = bing.com
PORT = 80
HashFile = splunk.sh3
SQLTable = splunk

[ECOMMERCE]
IP = google.com
PORT = 80
HashFile = ecomm.sh3
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
FROM_USER_PASSWORD = Changeme1!
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
"""
application_config = """BACK_END_LOCATION = 'localhost:5001'
MYSQL_USER = 'scoring_engine'
MYSQL_PASSWORD = 'Changeme1!'
MYSQL_HOST = '127.0.0.1'
CONFIG_PASSWORD = 'ThisIsAGoodPassword1'
REQUIRE_CONFIG_PASSWORD = 'no'
"""

back_service = """[Unit]
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
"""
front_service = """[Unit]
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
"""


class PreInstallCommand(install):
	def run(self):
		if system() == 'Linux':
			install.run(self)
			self.generate_files()
		else:
			print("Stopping install. Only Linux distro's are supported.")
			sys.exit(1)

	@staticmethod
	def generate_files():
		if not os.path.exists('/etc/systemd/system/scoring.engine.back.service'):
			print('Generating backend service file.')
			with open('/etc/systemd/system/scoring.engine.back.service', 'w') as f:
				print(back_service, file=f)
			call('systemctl daemon-reload'.split())

		if not os.path.exists('/etc/systemd/system/scoring.engine.front.service'):
			print('Generating frontend service file.')
			with open('/etc/systemd/system/scoring.engine.front.service', 'w') as f:
				print(front_service, file=f)
			call('systemctl daemon-reload'.split())

		if not os.path.exists('/opt/scoring-engine'):
			print('Generating configuration files.')
			os.mkdir('/opt/scoring-engine')

		if not os.path.exists('/opt/scoring-engine/application.conf'):
			with open('/opt/scoring-engine/application.conf', 'w') as f:
				print(application_config, file=f)

		if not os.path.exists('/opt/scoring-engine/service.conf'):
			with open('/opt/scoring-engine/service.conf', 'w') as f:
				print(service_config, file=f)

		if not os.path.exists('/opt/scoring-engine/scoring-baseline'):
			os.mkdir('/opt/scoring-engine/scoring-baseline')
		if not os.path.exists('/opt/scoring-engine/scoring-baseline/ecomm.sh3'):
			with open('/opt/scoring-engine/scoring-baseline/ecomm.sh3', 'w') as f:
				print("", file=f)
		if not os.path.exists('/opt/scoring-engine/scoring-baseline/splunk.sh3'):
			with open('/opt/scoring-engine/scoring-baseline/splunk.sh3', 'w') as f:
				print("", file=f)


setup(cmdclass={'install': PreInstallCommand})
