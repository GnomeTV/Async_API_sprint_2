#!/usr/bin/env bash

set -e
export PATH="/opt/tests:$PATH"
python3 functional/utils/wait_for_es.py
python3 functional/utils/wait_for_redis.py
pytest functional/src