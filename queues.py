#!/usr/bin/env python
from kombu import Exchange, Queue

task_exchange = Exchange('checks', type='fanout')
task_queues = [Queue('east')]
