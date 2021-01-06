"""File that handles all the request actions that come to the server."""
from scoring_engine.back_end import scoring_tasks as st, config_tasks as ct


def update_config(data):
	"""Function that is used when an update request comes in to the server."""
	service = data['service']
	ip = data['ip']
	if service.lower() == 'dns':
		machine = data['machine']
		if machine.lower() == 'linux':
			ct.config_dns_linux(ip, data['domains'])
		elif machine.lower() == 'windows':
			ct.config_dns_windows(ip, data['domains'])
		else:
			return False
	elif service.lower() == 'splunk':
		ct.config_splunk(ip, data['port'])
	elif service.lower() == 'ecomm':
		ct.config_ecomm(ip, data['port'])
	elif service.lower() == 'smtp':
		ct.config_smtp(ip, data['user 1'], data['user 1 pwd'], data['user 2'], data['domain'])
	elif service.lower() == 'ldap':
		ct.config_ldap(ip, data['users'])
	elif service.lower() == 'pop3':
		ct.config_pop3(ip, data['username'], data['password'])
	else:
		return False
	return True


def score_service(data):
	"""Function that is used when a score request comes in to the server."""
	service = data['service']
	if service.lower() == 'dns':
		machine = data['machine']
		if machine.lower() == 'linux':
			st.score_dns_linux()
		elif machine.lower() == 'windows':
			st.score_dns_windows()
		else:
			return False
	elif service.lower() == 'splunk':
		st.score_splunk()
	elif service.lower() == 'ecomm':
		st.score_ecomm()
	elif service.lower() == 'smtp':
		st.score_smtp()
	elif service.lower() == 'ldap':
		st.score_ldap()
	elif service.lower() == 'pop3':
		st.score_pop3()
	else:
		return False
	return True
