#!/usr/bin/env python
import json
import os
import sys
import MySQLdb
from bottle import route, run, get, abort, post, request, template, redirect, default_app, debug, TEMPLATE_PATH, response

config_file = "/etc/pingnaut/config.json"
if os.path.isfile(config_file) == True:
    with open(config_file) as data_file:
        config = json.load(data_file)
else:
    sys.exit("ERROR: no config file %s found!" % config_file)

class dbc(object):
        def __init__(self):
                self.db_host = config['celery']['task_data']['db_host']
                self.db_username = config['celery']['task_data']['db_username']
                self.db_password = config['celery']['task_data']['db_password']
                self.db_name = config['celery']['task_data']['db_name']
        def insert(self, statement):
                conn = MySQLdb.Connection(host=self.db_host, user=self.db_username, passwd=self.db_password, db=self.db_name)
                curs = conn.cursor()
                curs.execute(statement)
                conn.commit()
                conn.close()
        def select(self, statement):
                conn = MySQLdb.Connection(host=self.db_host, user=self.db_username, passwd=self.db_password, db=self.db_name)
                curs = conn.cursor()
                curs.execute(statement)
                conn.commit()
                result = curs.fetchall()
                return result
        def close(self):
                conn.close()

@route('/')
def list():
	db = dbc()
	sql = "SELECT * FROM `results` ORDER BY `timestamp` DESC limit 15"
	x = db.select(sql)
        return template('list', res=x)

run(host='0.0.0.0', port=8080, debug=True)

#+---------------+---------------+-------------------+------+-----+-------------------+-----------------------------+---------------------------------+---------+
#| Field         | Type          | Collation         | Null | Key | Default           | Extra                       | Privileges                      | Comment |
#+---------------+---------------+-------------------+------+-----+-------------------+-----------------------------+---------------------------------+---------+
#| id            | int(10)       |                   | NO   | PRI |                   | auto_increment              | select,insert,update,references |         |
#| response_time | float         |                   | NO   |     |                   |                             | select,insert,update,references |         |
#| source        | varchar(512)  | latin1_swedish_ci | NO   |     |                   |                             | select,insert,update,references |         |
#| traceroute    | text          | latin1_swedish_ci | YES  |     |                   |                             | select,insert,update,references |         |
#| url           | varchar(1024) | latin1_swedish_ci | YES  |     |                   |                             | select,insert,update,references |         |
#| timestamp     | timestamp     |                   | NO   |     | CURRENT_TIMESTAMP | on update CURRENT_TIMESTAMP | select,insert,update,references |         |
#+---------------+---------------+-------------------+------+-----+-------------------+-----------------------------+---------------------------------+---------+
