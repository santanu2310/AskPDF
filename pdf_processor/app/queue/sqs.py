import json
import logging
from kombu import Connection
from kombu.utils.url import safequote
from app.config import get_settings

logger = logging.getLogger(__name__)


def publish_status_to_sqs(queue_name: str, message_body: dict):
    """
    Publishes a raw JSON message to a specific Amazon SQS queue.

    This function connects to your SQS broker and sends a message
    without using the Celery task protocol.

    Args:
        queue_name (str): The name of the SQS queue (e.g., 'askpdf').
        message_body (dict): The Python dictionary to be sent as the message body.
    """
    settings = get_settings()

    # URL-encode ONLY for broker URL
    aws_access_key_encoded = safequote(settings.AWS_ACCESS_KEY_ID)
    aws_secret_key_encoded = safequote(settings.AWS_SECRET_ACCESS_KEY)

    # Use encoded credentials in broker URL
    broker_url = f"sqs://{aws_access_key_encoded}:{aws_secret_key_encoded}@"
    # Kombu needs the region to connect to SQS correctly.
    # We get this from your settings file.
    transport_options = {
        "region": settings.AWS_REGION,
        "predefined_queues": {settings.SQS_QUEUE_NAME: {"url": settings.SQS_QUEUE}},
    }

    # Establish connection with the broker, including the region info.
    with Connection(broker_url, transport_options=transport_options) as connection:
        # SimpleQueue is a high-level interface perfect for this use case.
        # Just provide the name of the queue from your SQS URL.
        queue = connection.SimpleQueue(queue_name)

        try:
            # The .put() method sends the message.
            # We explicitly use the json serializer for clarity.
            queue.put(message_body, serializer="json")

            logger.info(f"Successfully published message to SQS queue '{queue_name}'")
            logger.info(f"Message Body: {json.dumps(message_body)}")

        except Exception as e:
            # It's good practice to log any potential errors.
            logger.error(f"Failed to publish message to SQS queue '{queue_name}'.")
            logger.error(f"Exception: {e}")

        finally:
            # Cleanly close the queue resource.
            queue.close()

