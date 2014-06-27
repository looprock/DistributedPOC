#!/usr/bin/env python
import json
from kombu.mixins import ConsumerMixin
from kombu.log import get_logger
from kombu.utils import kwdict, reprcall
from kombu import Exchange, Queue
import datetime
import time
from tasks import get_response_time
import httplib
import socket
import sys
import os

time.sleep(11)

config_file = "/etc/pingnaut/config.json"
if os.path.isfile(config_file) == True:
    with open(config_file) as data_file:
        config = json.load(data_file)
else:
    sys.exit("ERROR: no config file %s found!" % config_file)

task_exchange = Exchange(config['consumer']['exchange'], type=config['consumer']['exchange_type'])
task_queues = [Queue(config['region'])]

logger = get_logger(__name__)


class Register():
	def __init__(self):
		self.service = "pingnaut-consumer-%s" % config['region']
		self.status_url = "http://%s:18002/status" % (socket.getfqdn())
		self.blob = blob = {"id": self.service, "url": self.status_url}
		self.data = json.dumps(self.blob)
		self.connection =  httplib.HTTPConnection('localhost:18001')
        	self.path = "/checks/%s" % (self.service)
	def add(self):
		if config['use_megaphone'] == "true":
			logger.info("Registering with megaphone")
			self.body_content = ''
        		self.connection.request('POST', '/checks', self.data)
        		result = self.connection.getresponse()
        		logger.info("megaphone add result: %s - %s" % (result.status, result.reason))
	def remove(self):
		if config['use_megaphone'] == "true":
			logger.info("un-registering with megaphone")
        		self.connection.request('DELETE', self.path)
        		result = self.connection.getresponse()
        		logger.info("megaphone remove result: %s - %s" % (result.status, result.reason))

class Worker(ConsumerMixin):

    def __init__(self, connection):
        self.connection = connection

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=task_queues,
                         accept=['json'],
                         callbacks=[self.process_task])]

    def process_task(self, body, message):
        try:
	    x = get_response_time.delay(body['url'])
	    logger.info("%s: %s, %s" % (datetime.datetime.today(),x.id,body))
        except Exception as exc:
            logger.error('task raised exception: %r', exc)
        message.ack()

if __name__ == '__main__':
    from kombu import Connection
    from kombu.pools import connections
    from kombu import pools
    from kombu.utils.debug import setup_logging

    pools.set_limit(500)

    # setup root logger
    setup_logging(loglevel='INFO', loggers=[''])
    megaphone = Register()
    connection = Connection(config['consumer']['connection'], heartbeat=int(config['consumer']['heartbeat']))
    connection.heartbeat_check(rate=1)
    #with Connection('amqp://guest:guest@localhost:5672//') as conn:
    with connections[connection].acquire(block=True, timeout=60) as conn:
        try:
	    megaphone.add()
            worker = Worker(conn)
            worker.run()
        except KeyboardInterrupt:
	    conn.release()
	    megaphone.remove()
            print('bye bye')
