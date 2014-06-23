DistributedPOC
==============

rabbitmq + celery task management

This is a proof of concept for creating a pingdom like service

consumer.py - rabbitmq server that pushes work to celery

get_response.py - simple celery client

pingdom_homegrown.png	- POC diagram

queues.py - used by celery

start_worker.sh - start the celery workers

submit_test.py - inject a job message into rabbit

tasks.py - celery task definitions
