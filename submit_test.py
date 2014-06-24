#!/usr/bin/env python
from __future__ import with_statement 
from kombu import Connection, Producer
import datetime
import sys
import json
import os
from queues import task_exchange 
from kombu.common import maybe_declare 
from kombu.pools import producers

if sys.argv < 2:
        print "Usage: %s [url]" % sys.argv[0]
        sys.exit()

message = '{ "test_type": "standard", "url": "%s"}' % sys.argv[1]

connection = Connection('amqp://guest:guest@localhost:5672/pingnaut')
with producers[connection].acquire(block=True, timeout=60) as conn:
        conn.publish(json.loads(message), exchange = 'checks', serializer="json")
	print "wrote: %s" % message
