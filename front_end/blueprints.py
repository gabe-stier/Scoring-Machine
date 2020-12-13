'''
Created on Nov 26, 2020

@author: gabez
'''
from flask import Blueprint, url_for, render_template, make_response, request, redirect, session
from flask.views import MethodView
from app.utilities import Loggers as log
import app.scoring_functions as score
from app.sqlite_connection import connect
import requests


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

    def post(self):
        return redirect(request.referrer)


class Score_Ecomm(MethodView):
    def get(self):
        url_for('static', filename='base.css')
        url_for('static', filename='scoring.css')
        return render_template('score-page.html.j2', service='Ecommerce')

    def post(self):
        score.Ecommerce.score()
        return redirect(request.referrer)


class Score_DNS_Windows(MethodView):
    def get(self):
        url_for('static', filename='base.css')
        url_for('static', filename='scoring.css')
        return render_template('score-page.html.j2', service='DNS - Windows')

    def post(self):
        score.Windows_DNS.score()
        return redirect(request.referrer)


class Score_DNS_Linux(MethodView):
    def get(self):
        url_for('static', filename='base.css')
        url_for('static', filename='scoring.css')
        return render_template('score-page.html.j2', service='DNS - Linux')

    def post(self):
        score.Linux_DNS.score()
        return redirect(request.referrer)


class Score_POP3(MethodView):
    def get(self):
        url_for('static', filename='base.css')
        url_for('static', filename='scoring.css')
        return render_template('score-page.html.j2', service='POP3')

    def post(self):
        return redirect(request.referrer)


class Score_SMTP(MethodView):
    def get(self):
        url_for('static', filename='base.css')
        url_for('static', filename='scoring.css')
        return render_template('score-page.html.j2', service='SMTP')

    def post(self):
        return redirect(request.referrer)


class Score_Splunk(MethodView):
    def get(self):
        url_for('static', filename='base.css')
        url_for('static', filename='scoring.css')
        return render_template('score-page.html.j2', service='Splunk')

    def post(self):
        score.Splunk.score()
        return redirect(request.referrer)


sr.add_url_rule('/ldap', view_func=Score_LDAP.as_view('ldap'))
sr.add_url_rule('/ecomm', view_func=Score_Ecomm.as_view('ecomm'))
sr.add_url_rule(
    '/dns-windows', view_func=Score_DNS_Windows.as_view('dns_windows'))
sr.add_url_rule('/dns-linux', view_func=Score_DNS_Linux.as_view('dns_linux'))
sr.add_url_rule('/pop3', view_func=Score_POP3.as_view('pop3'))
sr.add_url_rule('/smtp', view_func=Score_SMTP.as_view('smtp'))
sr.add_url_rule('/splunk', view_func=Score_Splunk.as_view('splunk'))

config_bp = Blueprint('config', __name__, url_prefix='/config')


@config_bp.route('/')
def config_index():
    return render_template('config.html.j2', service='None')


@config_bp.before_request
def login_check():
    require_password = score.Auth.get_require()
    if request.method == 'GET' or request.path == '/config/login' or not require_password or 'data' in session:
        pass
    else:
        session['data'] = request.form
        return redirect(url_for('config.config_login', redirect_loc=request.endpoint))


class Config_Login(MethodView):
    def get(self):
        url_for('static', filename='base.css')
        url_for('static', filename='login.css')
        if 'error' in request.args:
            err = request.args.get('error')
            if str(err).lower() != 'false':
                login_error = False
            else:
                login_error = True
        else:
            login_error = False
        return render_template('login.html.j2', error=login_error, redir=request.args.get('redirect_loc'))

    def post(self):
        pwd = request.form['cptn_pwd']
        redirect_loc = False
        if 'redirect_loc' in request.args:
            redirect_loc = request.args.get('redirect_loc')
        if redirect_loc == False:
            return render_template('internal_error.html.j2')
        if pwd == score.Auth.get_pwd():
            log.Main.info(
                f"Updating of Config. Password has been entered.{redirect_loc}")
            return redirect(url_for(redirect_loc))
        else:
            return redirect(url_for('config.config_login', error=True, redirect_loc=redirect_loc))


class Config_LDAP(MethodView):
    def get(self):
        url_for('static', filename='base.css')
        url_for('static', filename='config.css')
        if 'data' in session:
            try:
                log.Main.info(
                    "Updating of LDAP Config. Password has been entered.")
                score.LDAP.set_ip(session['data']['ldap_ip'])
                count = 1
                conn = connect()
                while f'username_{count}' in request.form:
                    conn.execute('INSERT INTO ldap_info (username, password) VALUES (?,?)', (str(
                        session['data'][f'username_{count}']), str(session['data'][f'userpwd_{count}'])))
                    conn.commit()
                    count += 1
                conn.close()
                score.save_service_config()
            except Exception as e:
                log.Error.error(e)
                return render_template('internal_error.html.j2')

            session.pop('data')
        else:
            return render_template('config.html.j2', service='LDAP')

    def post(self):
        try:
            log.Main.info("Updating of LDAP Config. Password is not required.")
            score.LDAP.set_ip(request.form['ldap_ip'])
            count = 1
            conn = connect()
            while f'username_{count}' in request.form:
                conn.execute('INSERT INTO ldap_info (username, password) VALUES (?,?)', (str(
                    request.form[f'username_{count}']), str(request.form[f'userpwd_{count}'])))
                conn.commit()
                count += 1
            conn.close()
            score.save_service_config()
        except Exception as e:
            log.Error.error(e)
            return render_template('internal_error.html.j2')
        return redirect(request.referrer)


class Config_Ecomm(MethodView):
    def get(self):
        url_for('static', filename='base.css')
        url_for('static', filename='config.css')
        if 'data' in session:
            try:
                log.Main.info(
                    "Updating of Ecomm Config. Password has been entered.")
                score.Ecommerce.set_ip(session['data']['ecomm_ip'])
                score.Ecommerce.set_hash(session['data']['ecomm_ip'])
                score.Ecommerce.set_port(session['data']['ecomm_port'])
                score.save_service_config()
            except Exception as e:
                log.Error.error(e)
                return render_template('internal_error.html.j2')

            session.pop('data')
        else:
            return render_template('config.html.j2', service='Ecommerce')

    def post(self):
        try:
            log.Main.info(
                "Updating of Ecomm Config. Password is not required.")
            score.Ecommerce.set_ip(request.form['ecomm_ip'])
            score.Ecommerce.set_hash(request.form['ecomm_ip'])
            score.Ecommerce.set_port(request.form['ecomm_port'])
            score.save_service_config()
        except Exception as e:
            log.Error.error(e)
            return render_template('internal_error.html.j2')
        return redirect(request.referrer)


class Config_DNS_Windows(MethodView):
    def get(self):
        url_for('static', filename='base.css')
        url_for('static', filename='config.css')
        return render_template('config.html.j2', service='DNS - Windows')

    def post(self):
        return redirect(request.referrer)


class Config_DNS_Linux(MethodView):
    def get(self):
        url_for('static', filename='base.css')
        url_for('static', filename='config.css')
        return render_template('config.html.j2', service='DNS - Linux')

    def post(self):
        return redirect(request.referrer)


class Config_POP3(MethodView):
    def get(self):
        url_for('static', filename='base.css')
        url_for('static', filename='config.css')
        return render_template('config.html.j2', service='POP3')

    def post(self):
        return redirect(request.referrer)


class Config_SMTP(MethodView):
    def get(self):
        url_for('static', filename='base.css')
        url_for('static', filename='config.css')
        return render_template('config.html.j2', service='SMTP')

    def post(self):
        return redirect(request.referrer)


class Config_Splunk(MethodView):
    def get(self):
        url_for('static', filename='base.css')
        url_for('static', filename='config.css')
        if 'data' in session:
            try:
                log.Main.info(
                    "Updating of Splunk Config. Password has been entered.")
                score.Ecommerce.set_ip(session['data']['ecomm_ip'])
                score.Ecommerce.set_hash(session['data']['ecomm_ip'])
                score.Ecommerce.set_port(session['data']['ecomm_port'])
                score.save_service_config()
            except Exception as e:
                log.Error.error(e)
                return render_template('internal_error.html.j2')

            session.pop('data')
        return render_template('config.html.j2', service='Splunk')

    def post(self):
        try:
            log.Main.info(
                "Updating of Splunk Config. Password is not required.")
            score.Splunk.set_ip(request.form['splunk_ip'])
            score.Splunk.set_hash(request.form['splunk_ip'])
            score.Splunk.set_port(request.form['splunk_port'])
            score.save_service_config()
        except Exception as e:
            log.Error.error(e)
            return render_template('internal_error.html.j2')
        return redirect(request.referrer)


config_bp.add_url_rule('/ldap', view_func=Config_LDAP.as_view('ldap'))
config_bp.add_url_rule('/ecomm', view_func=Config_Ecomm.as_view('ecomm'))
config_bp.add_url_rule(
    '/dns-windows', view_func=Config_DNS_Windows.as_view('dns_windows'))
config_bp.add_url_rule(
    '/dns-linux', view_func=Config_DNS_Linux.as_view('dns_linux'))
config_bp.add_url_rule('/pop3', view_func=Config_POP3.as_view('pop3'))
config_bp.add_url_rule('/smtp', view_func=Config_SMTP.as_view('smtp'))
config_bp.add_url_rule('/splunk', view_func=Config_Splunk.as_view('splunk'))
config_bp.add_url_rule(
    '/login', view_func=Config_Login.as_view('config_login'))
