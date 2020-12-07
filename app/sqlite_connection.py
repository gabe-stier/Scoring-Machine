'''
Created on Nov 25, 2020

@author: gabez
'''
import sqlite3
from app.utilities import Loggers as log


def init_db():
    conn = connect()
    with open('app/etc/basic_db.sql', 'r', encoding='utf8') as f:
        try:
            conn.executescript(f.read())
        except Exception as e:
            print(e)
            log.Error.error(e)
        conn.close()


def connect():
    return sqlite3.connect('scoring.db')
