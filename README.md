DistributedPOC
==============
rabbitmq + celery task management

This is a proof of concept for creating a pingdom like service

# Requirements:

rabbitmq

mysql

## Python modules required:
Celery

mysql

statsd (though currently disabled)

kombu (included in celery, or separate for the consumer)

bottle required for megaphone checks and fe.py

kazoo required for watcher.py

# Setup:

Create a virtual host 'pingnaut'

Create a fanout exchange 'checks' for the consumers to connect to

Create a queue for each region bound to fanout queue (i.e. east, west, which will map to 'region' in config.json)

Create vhost for each celery region (or run per-region rabbitmq instances)

Configure config.json and put it under /etc/pingnaut

We're currently running a consumer on each worker node because why not, but you only need one.

We run the workers and consumer under supervisord. Find example configs under the supervisor directory

# Files

addsite - command line for adding a new site to be checked

config.json - put this under /etc/pingnaut and config it

consumer.py - rabbitmq server that pushes work to celery

fe.py - a VERY basic bottle db viewer displaying the last 15 entries, for demo of functionality

megaphone - rest endpoints for megaphone integration

pingnaut.sql - sql script for creating the database fed by the workers

publisher.py - this will trigger checks of all sites in the database

sites.sql - sql script for creating the checks database

start_worker.sh - start the celery workers (if you're not running under supervisor or some other init setup)

submit_test.py - inject a message into rabbit for testing

supervisor - we use supervisor for init, here are our configs

tasks.py - celery task definitions

views - template for fe.py

watcher.py - this is a tiny app that watches zookeeper for a config update, then writes that to config.json and restarts consumers and workers.
