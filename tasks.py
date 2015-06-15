#!/usr/bin/env python
from celery import Celery
import json
import urllib
import time
import datetime
import subprocess
import os
import shlex
import socket
import re
import statsd
import MySQLdb

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

class AutoVivification(dict):
        """Implementation of perl's autovivification feature."""
        def __getitem__(self, item):
                try:
                        return dict.__getitem__(self, item)
                except KeyError:
                        value = self[item] = type(self)()
                        return value

def runcom(command_line):
        process = subprocess.Popen(shlex.split(command_line), stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        out, error = process.communicate()
        return out

app = Celery('tasks', backend=config['celery']['backend'], broker=config['celery']['broker'])

@app.task
def get_response_time(url):
	base = re.sub('[./,:]', '-', url)
	#c = statsd.StatsClient(config['celery']['task_data']['statsd_host'], config['celery']['task_data']['statsd_port'], prefix=config['celery']['task_data']['statsd_prefix'])
	d = str(datetime.datetime.utcnow())
	nf = urllib.urlopen(url)
	rc = nf.getcode()
	start = time.time()
	page = nf.read()
	end = time.time()
	nf.close()	
	r = end - start
	#c.timing('base.response_time', round(r, 4))
	u = url.split("/")[2]
	tracert = runcom("/usr/bin/mtr -r %s" % u)
	data = AutoVivification()
	data['response_time'] = round(r, 4)
	data['traceroute'] = tracert
	data['url'] = url
	data['source'] = socket.getfqdn()
	data['timestamp'] = d
	data['response_code'] = rc
	#fname = "./results/%s.log" % base
        #file = open(fname, "a")
	#rstr = "%s: %s %s %s %s" % (d, data['url'], data['source'], data['response_time'], data['traceroute'])
        #file.write("%s\n" % str(data))
        #file.close()
	db = dbc()
	sql = "insert into results (response_time,source,traceroute,url,timestamp,response_code) values ('%s','%s','%s','%s','%s','%s')" % (data['response_time'],data['source'],data['traceroute'],data['url'],data['timestamp'],data['response_code'])
	db.insert(sql)
	return json.dumps(data)
