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

app = Celery('tasks', backend='amqp', broker='amqp://guest@localhost//')

@app.task
def add(x, y):
    return x + y

@app.task(ignore_result=True)
def print_hello():
    print 'hello there'

@app.task
def gen_prime(x):
    multiples = []
    results = []
    for i in xrange(2, x+1):
        if i not in multiples:
            results.append(i)
            for j in xrange(i*i, x+1, i):
                multiples.append(j)
    return results

@app.task
def get_response_time(url):
	d = str(datetime.datetime.utcnow())
	nf = urllib.urlopen(url)
	start = time.time()
	page = nf.read()
	end = time.time()
	nf.close()	
	u = url.split("/")[2]
	tracert = runcom("sudo /usr/local/sbin/mtr -r %s" % u)
	r = end - start
	data = AutoVivification()
	data['response_time'] = round(r, 4)
	data['traceroute'] = tracert
	data['url'] = url
	data['source'] = socket.getfqdn()
	data['timestamp'] = d
	return json.dumps(data)
