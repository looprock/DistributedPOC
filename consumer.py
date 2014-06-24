#!/usr/bin/env python
import json
from kombu.mixins import ConsumerMixin
from kombu.log import get_logger
from kombu.utils import kwdict, reprcall
import datetime
import json
from tasks import get_response_time

from queues import task_queues

logger = get_logger(__name__)


class Worker(ConsumerMixin):

    def __init__(self, connection):
        self.connection = connection

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=task_queues,
                         #accept=['pickle', 'json'],
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
    connection = Connection('amqp://localhost:5672/pingnaut', heartbeat=5)
    connection.heartbeat_check(rate=1)
    with connections[connection].acquire(block=True, timeout=60) as conn:
        try:
            worker = Worker(conn)
            worker.run()
        except KeyboardInterrupt:
	    conn.release()
            print('bye bye')
