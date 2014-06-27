#!/usr/bin/env python
from __future__ import with_statement 
from kombu import Connection, Producer
import datetime
import sys
import json
import os
from kombu.common import maybe_declare 
from kombu.pools import producers

if sys.argv < 2:
        print "Usage: %s [url]" % sys.argv[0]
        sys.exit()

#message = '123484949:{ "block":[ "rewrite ^(/search/.*/mpg-[^/]*):[^/]*($|/.*) $1$2 permanent;", "# Block Wiju.com http://jira.vast.com/browse/OPS-98", "if ($http_referer ~* (www\\.wiju\\.com)) {", "        return 403;", "}", "if ($http_user_agent ~* (WijuBot)) {", "        return 403;", "}" ], "tests": { "0": { "url": "/", "type": "Disabled", "site": "global" } }, "logoverride": "None", "tmpl_version": 1, "cache": { "0": { "authfile": "Default", "path": "/(img|js|css|content)/", "proxy": "127.0.0.1:9019", "auth": "False", "logoverride": "False" } }, "enabled": { "status": "True", "exceptions": [] }, "name": "vastautos", "hostoverride": "None", "hostnames": [ "www.vast.com" ], "location": { "0": { "authfile": "Default", "path": "/", "proxy": "127.0.0.1:9019", "auth": "False", "logoverride": "False" } }, "maintenance": "False", "type": "mixdown", "overwrite": "True", "vanity": "False" }'

#message = '{ "test_type": "standard", "url": "http://gmail.com"}'
message = '{ "test_type": "standard", "url": "%s"}' % sys.argv[1]


#with Connection('amqp://pingnaut:pingnaut@graylog.vast.com:5672/pingnaut') as conn:
#simple_queue = conn.SimpleQueue('checks')
#simple_queue.put(json.loads(message))
#print('Sent: %s' % message)
#simple_queue.close()
# http://oriolrius.cat/blog/2013/09/30/hello-world-using-kombu-library-and-python/
#with producers[conn].acquire(block=True) as producer:
#       maybe_declare(task_exchange, producer.channel)
#       producer.publish(message, exchange = 'checks', serializer="json")

connection = Connection('amqp://pingnaut:pingnaut@graylog.vast.com:5672/pingnaut')
#with Connection('amqp://guest:guest@localhost:5672//') as conn:
with producers[connection].acquire(block=True, timeout=60) as conn:
        conn.publish(json.loads(message), exchange = 'checks', serializer="json")
	print "wrote: %s" % message
