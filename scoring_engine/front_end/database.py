import mysql.connector as conn

from scoring_engine.front_end.utilities import Loggers as log
from scoring_engine.front_end.utilities import Scores as Service


def open_database():
    '''Opens connection to the database'''
    try:
        db = None
        config = read_config()
        db = conn.connect(
            host=config['MYSQL_HOST'],
            username=config['MYSQL_USER'],
            password=config['MYSQL_PASSWORD'],
            database='scoring_engine'
        )
        return db
    except Exception as e:
        log.Error.error(e)


def read_config():
    '''Reads the configuration of the application'''
    with open("/usr/local/scoring_engine/application.conf", 'r') as f:
        content = f.read()
        paths = content.split("\n")
        config_dict = {}
        for path in paths:
            setting = path.split(" = ")
            config_dict[setting[0]] = setting[1].replace('\'', '')

    return config_dict


def get_last_score():
    '''Gets the last score of all the machines.'''
    try:
        db = open_database()
        cursor = db.cursor(buffered=True)
        cursor.execute('SELECT * FROM scores')
        result = cursor.fetchall()
        db.close()
        return result
    except Exception as e:
        log.Error.error(e)
