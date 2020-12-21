from configparser import ConfigParser
import os


def __config_task(config):
    new_file_name = ''
    old_file_name = ''
    with open(new_file_name, 'w+') as new_file:
        config.write(new_file)
    os.rename(new_file_name, old_file_name)


def config_splunk(ip: str, port: int):
    old_file_name = f'config/service.conf'
    config = ConfigParser()
    config.read(old_file_name)
    config['SPLUNK']['ip'] = ip
    config['SPLUNK']['port'] = port
    __config_task(config)


def config_ecomm(ip: str, port: int):
    old_file_name = f'config/service.conf'
    config = ConfigParser()
    config.read(old_file_name)
    config['ECOMMERCE']['ip'] = ip
    config['ECOMMERCE']['port'] = port
    __config_task(config)


def config_ldap(ip: str, users: dict):
    old_file_name = f'config/service.conf'
    config = ConfigParser()
    config.read(old_file_name)
    config['LDAP']['ip'] = ip
    # =-=-=-=--=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
    __config_task(config)


def config_smtp(ip: str, user_1: str, user_2: str, domain: str):
    old_file_name = f'config/service.conf'
    config = ConfigParser()
    config.read(old_file_name)
    config['SMTP']['ip'] = ip
    config['SMTP']['from_user'] = user_1
    config['SMTP']['to_user'] = user_2
    config['SMTP']['domain'] = domain

    __config_task(config)


def config_pop3(ip: str, username: str, password: str):
    old_file_name = f'config/service.conf'
    config = ConfigParser()
    config.read(old_file_name)
    config['POP3']['ip'] = ip
    config['POP3']['user'] = username
    config['POP3']['password'] = password
    __config_task(config)


def config_dns_windows(ip: str, domains: list):
    old_file_name = f'config/service.conf'
    config = ConfigParser()
    config.read(old_file_name)
    config['WINDOWS_DNS']['ip'] = ip
    config['WINDOWS_DNS']['domains'] = domains
    __config_task(config)


def config_dns_linux(ip: str, domains: list):
    old_file_name = f'config/service.conf'
    config = ConfigParser()
    config.read(old_file_name)
    config['LINUX_DNS']['ip'] = ip
    config['LINUX_DNS']['domains'] = domains
    __config_task(config)
