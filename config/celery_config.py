"""
Celery configuration for background task processing.

This enables asynchronous task execution for:
- Bulk message sending
- Notification processing
- Long-running operations (exports, reports)
- Scheduled tasks (reminders, cleanups)

Uses Redis as the message broker for reliability.
"""
from celery import Celery
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Determine Redis URL
redis_url = getattr(settings, 'redis_url', 'redis://localhost:6379/0')

# Create Celery app
celery_app = Celery(
    'edubot',
    broker=redis_url,
    backend=redis_url,
)

# Configuration
celery_app.conf.update(
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task timeouts (in seconds)
    task_soft_time_limit=600,  # 10 minutes
    task_time_limit=900,  # 15 minutes
    
    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    result_backend_transport_options={'master_name': 'mymaster'},
    
    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    
    # Task routing
    task_routes={
        'tasks.messaging.*': {'queue': 'messaging'},
        'tasks.notifications.*': {'queue': 'notifications'},
        'tasks.reports.*': {'queue': 'reports'},
    },
    
    # Task rate limiting
    task_rate_limit={
        'tasks.messaging.send_bulk_messages': '100/m',  # 100 messages per minute
    },
)

# Auto-discover tasks from all apps
celery_app.autodiscover_tasks(['tasks'])

logger.info(f"Celery configured with broker: {redis_url}")
logger.info("Task queues: messaging, notifications, reports, default")
