web: uvicorn main:app --host 0.0.0.0 --port 8000
worker: python -m celery -A tasks.celery_config worker --loglevel=info
