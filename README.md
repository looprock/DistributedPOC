DistributedPOC
==============
rabbitmq + celery task management

This is a proof of concept for creating a pingdom like service

Requirements:

rabbitmq

mysql

Python modules required:
Celery

mysql

kombu (included in celery, or separate for the consumer)

Setup:

Create a fanout exchange (pingnaut) for the consumers to connect to

Create a queue for each region bound to fanout queue

Create vhost for each celery region (or run per-region rabbitmq instances)

Configure: tasks.py, queues.py, consumer.py for each region/worker

We're currently running a consumer on each worker node because why not, but you only need one.

We run the workers and consumer under supervisord. Find example configs under the supervisor directory

consumer.py - rabbitmq server that pushes work to celery

pingnaut.sql - sql script for creating the database fed by the workers

queues.py - used by celery

start_worker.sh - start the celery workers (if you're not running under supervisor or some other init setup)

submit_test.py - inject a message into rabbit for testing

tasks.py - celery task definitions
