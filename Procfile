web: uvicorn main:app --host 0.0.0.0 --port 8000
worker: python -m celery.bin.celery -A config.celery_config worker --loglevel=info
