#!/usr/bin/env python
import json
import pprint
pp = pprint.PrettyPrinter(indent=4)

from tasks import get_response_time
r = get_response_time.delay("http://gmail.com")
pp.pprint(json.loads(r.get()))
