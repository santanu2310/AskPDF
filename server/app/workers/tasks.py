import logging
from aiobotocore.session import get_session

from app.core.config import settings
from app.core.memory_db import SQLiteKVStore
from .services import update_file_state

logger = logging.getLogger(__name__)


async def file_update_consumer():
    session = get_session()
    memory_db = SQLiteKVStore()
    logger.info("checking for message in queue")
    async with session.create_client(
        "sqs",
        region_name=settings.AWS_REGION,
        aws_secret_access_key=settings.AWS_SECRET_KEY,
        aws_access_key_id=settings.AWS_ACCESS_KEY,
    ) as client:
        while True:
            response = await client.receive_message(  # type: ignore
                QueueUrl=settings.SQS_QUEUE,
                MaxNumberOfMessages=1,  # Number of messages to retrieve
                WaitTimeSeconds=20,  # Long polling for up to 20 seconds
                VisibilityTimeout=30,  # Time message is invisible to other consumers
            )

            if "Messages" in response:
                for message in response["Messages"]:
                    logger.info(f"{message=}")
                    await update_file_state(
                        payload=message["Body"], memory_db=memory_db
                    )
                    # Delete the message after successful processing
                    await client.delete_message(  # type: ignore
                        QueueUrl=settings.SQS_QUEUE,
                        ReceiptHandle=message["ReceiptHandle"],
                    )
            else:
                logger.info("No messages in queue, waiting...")
