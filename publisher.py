#!/usr/bin/env python
from __future__ import with_statement
from kombu import Connection, Producer
import datetime
import sys
import json
import os
from kombu.common import maybe_declare
from kombu.pools import producers
from apscheduler.schedulers import blocking
import MySQLdb

ttw = 60

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

def geturls():
        db = dbc()
        sql = "SELECT url FROM `sites`"
        return db.select(sql)

def publish_checks():
        urls = geturls()
        print urls
        for url in urls:
                print "adding check for %s" % url
                message = '{ "test_type": "standard", "url": "%s"}' % (url)
                connection = Connection('amqp://pingnaut:vSVHy1lIGQLKoq01ZCvNbMaD3rPkf6hvrvGp5N7U@localhost:5672/pingnaut')
                with producers[connection].acquire(block=True, timeout=60) as conn:
                        conn.publish(json.loads(message), exchange = 'checks', serializer="json")
                        print "wrote: %s" % message


sched = blocking.BlockingScheduler()
sched.add_job(publish_checks, 'interval', seconds = ttw)
publish_checks()
print "sleeping for %s seconds" % ttw
sched.start()
