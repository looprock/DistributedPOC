#!/usr/bin/env python
import json
import sys
import os
import time
import shutil
import socket
from ConfigParser import SafeConfigParser
import logging
import re
import subprocess
import shlex
import urllib
import urllib2

logging.basicConfig()

config_file = "/etc/pingnaut/config.json"
if os.path.isfile(config_file) == True:
    with open(config_file) as data_file:
        config = json.load(data_file)
else:
    sys.exit("ERROR: no config file %s found!" % config_file)

path = "/vast/envs/alpha/test/pingnaut/%s" % config['region']

DEBUG = True
TIMEOUT = float(10)
min_consumers = 2
min_workers = 2

def bug(msg):
    if DEBUG:
        print "DEBUG: %s" % msg

bug("Watching: %s" % path)

def runcom(command_line):
        process = subprocess.Popen(shlex.split(command_line), stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        out, error = process.communicate()
        return out

class MyException(Exception):
    pass

# zookeeper reporting
# if we find ./zk.conf or /etc/zktools/zk.conf, we should try to report to
# zookeeper
enablezk = "false"
if os.path.exists('./zk.conf'):
    enablezk = "true"
    bug("using config ./zk.conf")
    parser = SafeConfigParser()
    parser.read('./zk.conf')
elif os.path.exists('/etc/zktools/zk.conf'):
    enablezk = "true"
    bug("Using config /etc/zktools/zk.conf")
    parser = SafeConfigParser()
    parser.read('/etc/zktools/zk.conf')

if enablezk == "true":
    from kazoo.client import KazooClient
    from kazoo.retry import KazooRetry
    from kazoo.exceptions import KazooException
    from kazoo.protocol.states import EventType
    env = parser.get('default', 'env').strip()
    use_exhibitor = parser.getboolean(env, 'use_exhibitor')
    zkservers = parser.get(env, 'servers').strip()
    if use_exhibitor:
        exhibitor = "http://%s/exhibitor/v1/cluster/list/" % (zkservers)
        try:
                if DEBUG:
                        print "Connecting to: %s" % exhibitor
                servers = ""
                zkdata = json.load(urllib2.urlopen(exhibitor, timeout = TIMEOUT))
                for z in zkdata['servers']:
                        servers += "%s:%s," % (z, zkdata['port'])
                servers = servers[:-1]
                if DEBUG:
                        print servers
        except:
                print "ERROR: unable to get server list from exhibitor! Aborting!"
                sys.exit(1)
    else:
        servers = "%s" % (zkservers)
    zkroot = parser.get(env, 'root').strip()
    host = socket.getfqdn()
    kr = KazooRetry(max_tries=3)
    zk = KazooClient(hosts=servers)

def watch_host(event):
    print event

def my_listener(state):
    if state == KazooState.LOST:
    # Register somewhere that the session was lost
        print "Lost"
    elif state == KazooState.SUSPENDED:
    # Handle being disconnected from Zookeeper
        print "Suspended"
    else:
    # Handle being connected/reconnected to Zookeeper
    # what are we supposed to do here?
    	print "Being Connected/Reconnected"



def my_listener(state):
    if state == KazooState.LOST:
    	# Register somewhere that the session was lost
        print "Lost"
    elif state == KazooState.SUSPENDED:
    	# Handle being disconnected from Zookeeper
        print "Suspended"
    else:
    	# Handle being connected/reconnected to Zookeeper
    	# what are we supposed to do here?
    	print "Being Connected/Reconnected"

zk.start()
#zk.add_listener(my_listener)

def reset_megaphone():
	if config['use_megaphone'] == 'true':
		urllib2.urlopen("http://localhost:18001", timeout = TIMEOUT)

@zk.DataWatch(path)
def restart(data, stat):
    	print("Data is %s" % data)
	file = open(config_file, "w")
	file.write("%s\n" % str(data))
	file.close()
	consumers_url = "http://oplog.vast.com/zknavalpha/json/|vast|envs|alpha|applications|pingnaut-consumer-%s|servers" % config['region']
	workers_url = "http://oplog.vast.com/zknavalpha/json/|vast|envs|alpha|applications|celery-worker-%s|servers" % config['region']
	consumers = len(json.load(urllib2.urlopen(consumers_url, timeout = TIMEOUT)))
	workers = len(json.load(urllib2.urlopen(workers_url, timeout = TIMEOUT)))
	if consumers < min_consumers or workers < min_workers:
		bug("not enough consumers or workers running, sleeping 10")
		time.sleep(10)
	else:	
		runcom("/usr/bin/supervisorctl stop consumer")
		reset_megaphone()
		runcom("/usr/bin/supervisorctl restart consumer_status")
		runcom("/usr/bin/supervisorctl stop worker")
		reset_megaphone()
		runcom("/usr/bin/supervisorctl restart worker_status")
		runcom("/usr/bin/supervisorctl start worker")
		reset_megaphone()
		runcom("/usr/bin/supervisorctl start consumer")
		reset_megaphone()
	

while True:
	time.sleep(5)
