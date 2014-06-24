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
#import statsd
import MySQLdb

class dbc(object):
        def __init__(self):
                self.db_host = "localhost"
                self.db_username = "root"
                self.db_password = "root"
                self.db_name = "pingnaut"
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

app = Celery('tasks', backend='amqp', broker='amqp://guest:guest@localhost/celery-east')

@app.task
def get_response_time(url):
	base = re.sub('[./,:]', '-', url)
	#c = statsd.StatsClient('statsd-alpha.vast.com', 8125, prefix='pingnon')
	d = str(datetime.datetime.utcnow())
	nf = urllib.urlopen(url)
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
	fname = "./results/%s.log" % base
        file = open(fname, "a")
	rstr = "%s: %s %s %s %s" % (d, data['url'], data['source'], data['response_time'], data['traceroute'])
        file.write("%s\n" % str(data))
        file.close()
	db = dbc()
	sql = "insert into results (response_time,source,traceroute,url,timestamp) values ('%s','%s','%s','%s','%s')" % (data['response_time'],data['source'],data['traceroute'],data['url'],data['timestamp'])
	db.insert(sql)
	return json.dumps(data)
