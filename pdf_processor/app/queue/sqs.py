import json
import logging
import boto3
from app.config import get_settings

logger = logging.getLogger(__name__)


def publish_status_to_sqs(message_body: dict):
    """
    Publishes a raw JSON message to a specific Amazon SQS queue.

    This function connects to your SQS broker and sends a message
    without using the Celery task protocol.

    Args:
        queue_name (str): The name of the SQS queue (e.g., 'askpdf').
        message_body (dict): The Python dictionary to be sent as the message body.
    """
    settings = get_settings()

    try:
        sqs = boto3.client(
            "sqs",
            region_name=settings.AWS_REGION,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        )

        sqs.send_message(
            QueueUrl=settings.SQS_QUEUE, MessageBody=json.dumps(message_body)
        )

        logger.info(f"Successfully published message to SQS queue {settings.SQS_QUEUE}")
        logger.info(f"Message Body: {json.dumps(message_body)}")

    except Exception as e:
        # It's good practice to log any potential errors.
        logger.error(f"Failed to publish message to SQS queue '{settings.SQS_QUEUE}'.")
        logger.error(f"Exception: {e}")
