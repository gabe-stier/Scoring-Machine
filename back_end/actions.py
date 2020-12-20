from scoring_functions import Windows_DNS, Linux_DNS, Ecommerce, Splunk, POP3, SMTP, LDAP

def update_config(data):
    service = data['service']
    return True

def score_service(data):
    service = data['service']
    if service.lower() == 'dns':
        machine = data['machine']
        if machine.lower() == 'linux':
            Linux_DNS.score()
            pass
        elif machine.lower() == 'windows':
            Windows_DNS.score()
            pass
        else:
            return False
    elif service.lower() == 'splunk':
        Splunk.score()
    elif service.lower() == 'ecomm':
        Ecommerce.score()
    elif service.lower() == 'smtp':
        SMTP.score()
    elif service.lower() == 'ldap':
        LDAP.score()
    elif service.lower() == 'pop3':
        POP3.score()
    else:
        return False
    return True