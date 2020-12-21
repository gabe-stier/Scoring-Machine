import scoring_tasks as st


def update_config(data):
    service = data['service']
    return True


def score_service(data):
    service = data['service']
    if service.lower() == 'dns':
        machine = data['machine']
        if machine.lower() == 'linux':
            st.score_dns_linux()
        elif machine.lower() == 'windows':
            st.score_dns_windows()
            pass
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
