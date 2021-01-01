from setuptools import setup
from subprocess import call
from setuptools.command.install import install
from setuptools.command.develop import develop
from platform import linux_distribution, system
import sys


class PreDevelopCommand(develop):
    def run(self):
        os = system()
        if os == 'Linux':
            pkg_manager_yum = call('which yum'.split())
            pkg_manager_apt = call('which apt'.split())
            if pkg_manager_apt == 0 and pkg_manager_yum == 1:
                call('apt update'.split())
                call('apt install -y build-essential python3-dev python2.7-dev \
                        libldap2-dev libsasl2-dev slapd ldap-utils tox lcov valgrind'.split())
            elif pkg_manager_apt == 1 and pkg_manager_yum == 0:
                call('yum update'.split())
                call('yum groupinstall "Development tools"'.split())
                call('yum install openldap-devel python-devel'.split())
            else:
                print('Unknown package manager. Continuing with package install.')
            try:
                develop.run(self)
            except Exception as e:
                print("An Error has occured. Most likely the correct packages were not installed.",
                      "Check 'https://www.python-ldap.org/en/python-ldap-3.3.0/installing.html#build-prerequisites' to install the correct packages for your distro.", sep='\n')
                print(e)
        else:
            print("Stopping install. Only Linux distro's are supported.")
            sys.exit(1)


class PreInstallCommand(install):
    def run(self):
        os = system()
        if os == 'Linux':
            pkg_manager_yum = call('which yum'.split())
            pkg_manager_apt = call('which apt'.split())
            if pkg_manager_apt == 0 and pkg_manager_yum == 1:
                call('apt update'.split())
                call('apt install -y build-essential python3-dev python2.7-dev \
                        libldap2-dev libsasl2-dev slapd ldap-utils tox lcov valgrind'.split())
            elif pkg_manager_apt == 1 and pkg_manager_yum == 0:
                call('yum update'.split())
                call('yum groupinstall "Development tools"'.split())
                call('yum install openldap-devel python-devel'.split())
            else:
                print('Unknown package manager. Continuing with package install.')
            try:
                develop.run(self)
            except Exception as e:
                print("An Error has occured. Most likely the correct packages were not installed.",
                      "Check 'https://www.python-ldap.org/en/python-ldap-3.3.0/installing.html#build-prerequisites' to install the correct packages for your distro.", sep='\n')
                print(e)
        else:
            print("Stopping install. Only Linux distro's are supported.")
            sys.exit(1)


setup()
