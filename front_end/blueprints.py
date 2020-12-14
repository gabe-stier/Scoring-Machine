'''
Created on Nov 26, 2020

@author: gabez
'''
from flask import Blueprint, url_for, render_template, make_response, request, redirect, session
from flask.views import MethodView
from front_end.utilities import Loggers as log


sr = Blueprint('score', __name__, url_prefix='/request-score')


@sr.route('/')
def score_page():
    url_for('static', filename='base.css')
    url_for('static', filename='index.css')
    url_for('static', filename='scoring.css')
    ldap_srv = False
    dnsl_srv = False
    dnsw_srv = False
    ecomm_srv = False
    pop3_srv = False
    smtp_srv = False
    splunk_srv = False

    return make_response(render_template('scoring.html.j2', ldap=ldap_srv, dnsl=dnsl_srv, dnsw=dnsw_srv, ecomm=ecomm_srv, pop3=pop3_srv, smtp=smtp_srv, splunk=splunk_srv))


class Score_LDAP(MethodView):
    def get(self):
        url_for('static', filename='base.css')
        url_for('static', filename='scoring.css')
        return render_template('score-page.html.j2', service='LDAP')


class Score_Ecomm(MethodView):
    def get(self):
        url_for('static', filename='base.css')
        url_for('static', filename='scoring.css')
        return render_template('score-page.html.j2', service='Ecommerce')


class Score_DNS_Windows(MethodView):
    def get(self):
        url_for('static', filename='base.css')
        url_for('static', filename='scoring.css')
        return render_template('score-page.html.j2', service='DNS - Windows')


class Score_DNS_Linux(MethodView):
    def get(self):
        url_for('static', filename='base.css')
        url_for('static', filename='scoring.css')
        return render_template('score-page.html.j2', service='DNS - Linux')


class Score_POP3(MethodView):
    def get(self):
        url_for('static', filename='base.css')
        url_for('static', filename='scoring.css')
        return render_template('score-page.html.j2', service='POP3')


class Score_SMTP(MethodView):
    def get(self):
        url_for('static', filename='base.css')
        url_for('static', filename='scoring.css')
        return render_template('score-page.html.j2', service='SMTP')


class Score_Splunk(MethodView):
    def get(self):
        url_for('static', filename='base.css')
        url_for('static', filename='scoring.css')
        return render_template('score-page.html.j2', service='Splunk')


sr.add_url_rule('/ldap', view_func=Score_LDAP.as_view('ldap'))
sr.add_url_rule('/ecomm', view_func=Score_Ecomm.as_view('ecomm'))
sr.add_url_rule(
    '/dns-windows', view_func=Score_DNS_Windows.as_view('dns_windows'))
sr.add_url_rule('/dns-linux', view_func=Score_DNS_Linux.as_view('dns_linux'))
sr.add_url_rule('/pop3', view_func=Score_POP3.as_view('pop3'))
sr.add_url_rule('/smtp', view_func=Score_SMTP.as_view('smtp'))
sr.add_url_rule('/splunk', view_func=Score_Splunk.as_view('splunk'))
