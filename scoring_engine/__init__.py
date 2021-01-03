import os
import sys
from shutil import copyfile
from subprocess import call
from threading import Thread

import pkg_resources
from gunicorn.app.base import BaseApplication

from scoring_engine import back_end as back, front_end as front


def system_command():
	args = sys.argv[1:]
	if "--help" in args or '-h' in args:
		print('Scoring Engine Help:',
		      '-> main command: scoring-engine',
		      '-> Base Arguments:',
		      '\t--start,\t-st\tStarts a component of the machine\t\tDefault: all',
		      '\t--stop,\t\t-sp\tStops a component of the machine\t\tDefault: all',
		      '\t--boot,\t\t-bt\tManages boot start a component of the machine\tDefault: all',
		      '\t--restart,\t-rt\tRestarts a component of the machine\t\tDefault: all',
		      '\t--config,\t-c\tInformation about configuration files\t\tDefault: location',
		      '\t--help,\t\t-h\tThe help command',
		      '-> Modifiers:',
		      '\t--all,\t\t-a\tPoints to front and back of the machine\t\tUsed for: start, stop, boot, restart',
		      '\t--front,\t-f\tPoints to front of the machine\t\t\tUsed for: start, stop, boot, restart',
		      '\t--back,\t\t-b\tPoints to the back of the machine\t\tUsed for: start, stop, boot, restart',
		      '\t--enable,\t-e\tSets component to start on machine boot\t\tUsed for: boot\t REQUIRED for boot command',
		      '\t--disable,\t-d\tSets component to not start on machine boot\tUsed for: boot\t \
				REQUIRED for boot command',
		      '\t--location,\t-l\tShows location of configuration files\t\tUsed for: config',
		      '\t--reset,\t-r\tResets configuration files\t\t\tUsed for: config',
		      sep='\n')
	if "--start" in args or '-st' in args:
		result = False
		if "--all" in args or '-a' in args:
			result = start_server('all')
		elif '--back' in args or '-b' in args:
			result = start_server('back')
		elif '--front' in args or '-f' in args:
			result = start_server('front')
		else:
			result = start_server('all')
		if result:
			print('Start complete')
		else:
			print('Start failed')

	elif "--stop" in args or '-sp' in args:
		result = False
		if "--all" in args or '-a' in args:
			result = stop_server('all')
		elif '--back' in args or '-b' in args:
			result = stop_server('back')
		elif '--front' in args or '-f' in args:
			result = stop_server('front')
		else:
			result = stop_server('all')
		if result:
			print('Stopping complete')
		else:
			print('Stopping Failed')

	elif "--boot" in args or '-bt' in args:
		result = False
		if '--enable' in args or '-e' in args:
			if "--all" in args or '-a' in args:
				result = boot_start_enable('all')
			if '--back' in args or '-b' in args:
				result = boot_start_enable('back')
			if '--front' in args or '-f' in args:
				result = boot_start_enable('front')
			else:
				result = boot_start_enable('all')
			if result:
				print('Boot enable successful')
			else:
				print('Boot enable failed.')
		elif '--disable' in args or '-d' in args:
			if "--all" in args or '-a' in args:
				result = boot_start_disable('all')
			if '--back' in args or '-b' in args:
				result = boot_start_disable('back')
			if '--front' in args or '-f' in args:
				result = boot_start_disable('front')
			else:
				result = boot_start_disable('all')
			if result:
				print('Boot disable successful')
			else:
				print('Boot disable failed.')
		else:
			print('Need --enable or --disable')

	elif "--restart" in args or '-rt' in args:
		result = False
		if "--all" in args or '-a' in args:
			result = restart_server('all')
		elif '--back' in args or '-b' in args:
			result = restart_server('back')
		elif '--front' in args or '-f' in args:
			result = restart_server('front')
		else:
			result = restart_server('all')
		if result:
			print('Restart successful.')
		else:
			print('Restart failed.')

	elif "--config" in args or '-c' in args:
		create_configuration_files(True)
	else:
		print("Scoring Engine:", "Unknown argument, scoring-engine --help")


def start_front_server():
	options = {
		'bind':    '0.0.0.0:80',
		'workers': 4,
		'timeout': 120
		}

	print('Starting Gunicorn')
	Thread(target=Gunicorn_Application(
			app=front.app(), options=options).run()).start()


def start_back_server():
	print('Starting Back_end Server')
	Thread(target=back.start()).start()


def create_configuration_files():
	pass


def generate_files():
	if not os.path.exists('/etc/systemd/system/scoring.engine.back.service'):
		try:
			os.symlink('/usr/local/scoring_machine/services/scoring.engine.back.service', '/etc/systemd/system',
			           target_is_directory=True)
			call('systemclt daemon-reload'.split())
		except OSError as ioe:
			sys.exit("Please run this command as root.")
			return False

	if not os.path.exists('/etc/systemd/system/scoring.engine.front.service'):
		try:
			os.symlink('/usr/local/scoring_machine/services/scoring.engine.front.service', '/etc/systemd/system',
			           target_is_directory=True)
			call('systemclt daemon-reload'.split())
		except OSError as ioe:
			sys.exit("Please run this command as root.")
			return False

	if not os.path.exists('/opt/scoring-engine/scoring-engine'):
		try:
			os.mkdir('/opt/scoring-engine/scoring-engine')
		except OSError as ioe:
			sys.exit("Please run this command as root.")

	if not os.path.exists('/opt/scoring-engine/application.conf'):
		try:
			copyfile(pkg_resources.resource_filename(__name__, "scoring_engine/service/application.conf"),
			         '/opt/scoring-engine/application.conf')
		except PermissionError as ioe:
			sys.exit("Please run this command as root.")

	if not os.path.exists('/opt/scoring-engine/service.conf'):
		try:
			copyfile(pkg_resources.resource_filename(__name__, "scoring_engine/service/service.conf"),
			         '/opt/scoring-engine/service.conf')
		except PermissionError as ioe:
			sys.exit("Please run this command as root.")


def boot_start_enable(part):
	if part == 'all':
		return boot_start_enable('front') and boot_start_enable('back')
	elif part == 'back':
		exit_code = call('systemctl enable scoring.engine.back'.split())
		if exit_code != 0:
			return False
		return True
	elif part == 'front':
		exit_code = call('systemctl enable scoring.engine.front'.split())
		if exit_code != 0:
			return False
		return True


def boot_start_disable(part):
	if part == 'all':
		return boot_start_disable('front') and boot_start_disable('back')
	elif part == 'back':
		exit_code = call('systemctl enable scoring.engine.back'.split())
		if exit_code != 0:
			return False
		return True
	elif part == 'front':
		exit_code = call('systemctl enable scoring.engine.front'.split())
		if exit_code != 0:
			return False
		return True


def start_server(part):
	if part == 'all':
		return start_server('front') and start_server('back')
	elif part == 'back':
		try:
			call('systemctl start scoring.engine.back.service'.split())
		except Exception as e:
			print('Something failed...')
			print(e)
			return False
		return True
	elif part == 'front':
		try:
			call('systemctl start scoring.engine.front.service'.split())
		except Exception as e:
			print('Something failed...')
			print(e)
			return False
		return True


def stop_server(part):
	if part == 'all':
		return stop_server('back') and stop_server('front')
	elif part == 'back':
		exit_code = call(f'systemctl stop scoring.engine.back.service'.split())
		if exit_code != 0:
			return False
		return True
	elif part == 'front':
		exit_code = call(
				f'systemctl stop scoring.engine.front.service'.split())
		if exit_code != 0:
			return False
		return True


def restart_server(part):
	return stop_server(part) and start_server(part)


class Gunicorn_Application(BaseApplication):

	def __init__(self, app, options=None):
		self.options = options or {}
		self.application = app
		super().__init__()

	def load_config(self):
		config = {key: value for key, value in self.options.items()
		          if key in self.cfg.settings and value is not None}
		for key, value in config.items():
			self.cfg.set(key.lower(), value)

	def load(self):
		return self.application
