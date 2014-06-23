#!/usr/bin/env python
from kombu import Connection
import datetime
import sys
import json
import os

if sys.argv < 2:
	print "Usage: %s [url]" % sys.argv[0]
	sys.exit()

#message = '123484949:{ "block":[ "rewrite ^(/search/.*/mpg-[^/]*):[^/]*($|/.*) $1$2 permanent;", "# Block Wiju.com http://jira.vast.com/browse/OPS-98", "if ($http_referer ~* (www\\.wiju\\.com)) {", "        return 403;", "}", "if ($http_user_agent ~* (WijuBot)) {", "        return 403;", "}" ], "tests": { "0": { "url": "/", "type": "Disabled", "site": "global" } }, "logoverride": "None", "tmpl_version": 1, "cache": { "0": { "authfile": "Default", "path": "/(img|js|css|content)/", "proxy": "127.0.0.1:9019", "auth": "False", "logoverride": "False" } }, "enabled": { "status": "True", "exceptions": [] }, "name": "vastautos", "hostoverride": "None", "hostnames": [ "www.vast.com" ], "location": { "0": { "authfile": "Default", "path": "/", "proxy": "127.0.0.1:9019", "auth": "False", "logoverride": "False" } }, "maintenance": "False", "type": "mixdown", "overwrite": "True", "vanity": "False" }'

#message = '{ "test_type": "standard", "url": "http://gmail.com"}'
message = '{ "test_type": "standard", "url": "%s"}' % sys.argv[1]


with Connection('amqp://guest:guest@localhost:5672//') as conn:
    #simple_queue = conn.SimpleQueue('simple_queue')
    simple_queue = conn.SimpleQueue('hipri')
    #message = 'hello world, sent at %s' % datetime.datetime.today()
    #message = '%s: %s' % (datetime.datetime.today(), sys.argv[1])
    simple_queue.put(json.loads(message),  priority='high')
    print('Sent: %s' % message)
    simple_queue.close()
