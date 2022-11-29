#!/usr/bin/env bash

set -e

cd src

python utils/wait_for_es.py
python utils/wait_for_redis.py

gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000