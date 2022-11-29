#!/usr/bin/env bash

set -e

python functional/utils/wait_for_es.py
python functional/utils/wait_for_redis.py
pytest functional/src
