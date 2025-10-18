from celery import Celery
from kombu.utils.url import safequote
from app.config import get_settings

settings = get_settings()


# URL-encode ONLY for broker URL
aws_access_key_encoded = safequote(settings.AWS_ACCESS_KEY_ID)
aws_secret_key_encoded = safequote(settings.AWS_SECRET_ACCESS_KEY)

# Use encoded credentials in broker URL
broker_url = f"sqs://{aws_access_key_encoded}:{aws_secret_key_encoded}@"

celery_app = Celery("tasks", broker=broker_url, include=["app.tasks.process_pdf"])

celery_app.conf.task_default_queue = settings.CELERY_SQS_QUEUE_NAME
celery_app.conf.broker_transport_options = {
    "region": settings.AWS_REGION,
    "predefined_queues": {
        settings.CELERY_SQS_QUEUE_NAME: {
            "url": settings.CELERY_SQS_QUEUE,
            "access_key_id": settings.AWS_ACCESS_KEY_ID,
            "secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
        }
    },
}
