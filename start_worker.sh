#!/bin/bash
# Celery worker startup script
export PYTHONUNBUFFERED=1
export PYTHONPATH=/app:$PYTHONPATH
cd /app
exec celery -A config.celery_config worker --loglevel=info
