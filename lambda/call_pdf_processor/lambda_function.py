import os
import uuid
import base64
import json
import urllib.parse
import boto3

# The name of the task as defined in your Celery worker code.
# Example: 'my_tasks.process_s3_object'
CELERY_TASK_NAME = os.environ.get("CELERY_TASK_NAME")
FUNCTION_NAME = os.environ.get("FUNCTION_NAME")
QUEUE_URL = os.environ.get("QUEUE_URL")
QUEUE_NAME = os.environ.get("QUEUE_NAME")

s3 = boto3.client("s3")
sqs = boto3.client("sqs")


def create_celery_message(
    task_name,
    queue_name=QUEUE_NAME,
    *args,
    **kwargs,
):
    """
    Constructs a Celery-compatible message dictionary and JSON string.
    """
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}

    task_id = str(uuid.uuid4())
    reply_to_id = str(uuid.uuid4())
    delivery_tag_id = str(uuid.uuid4())

    # The structure is a tuple/list: [args, kwargs, options]
    inner_body_payload = [
        args,
        kwargs,
        {"callbacks": None, "errbacks": None, "chain": None, "chord": None},
    ]

    encoded_inner_body = base64.b64encode(
        json.dumps(inner_body_payload).encode("utf-8")
    ).decode("utf-8")

    message = {
        "body": encoded_inner_body,
        "content-encoding": "utf-8",
        "content-type": "application/json",
        "headers": {
            "lang": "py",
            "task": task_name,
            "id": task_id,
            "shadow": None,
            "eta": None,
            "expires": None,
            "group": None,
            "group_index": None,
            "retries": 0,
            "timelimit": [None, None],
            "root_id": task_id,  # Same as task_id for a simple task
            "parent_id": None,  # No parent for a direct-published task
            "argsrepr": str(tuple(args)),
            "kwargsrepr": str(kwargs),
            "origin": FUNCTION_NAME,
            "ignore_result": False,
        },
        "properties": {
            "correlation_id": task_id,  # Same as task_id
            "reply_to": reply_to_id,
            "delivery_mode": 2,
            "delivery_info": {"exchange": "", "routing_key": queue_name},
            "priority": 0,
            "body_encoding": "base64",
            "delivery_tag": delivery_tag_id,
        },
    }

    return message


def lambda_handler(event, context):
    """
    This function is triggered by an S3 event. It extracts the object key
    and a 'doc-id' from the object's metadata, then dispatches a Celery task
    using IAM authentication.
    """
    try:
        bucket = event["Records"][0]["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(
            event["Records"][0]["s3"]["object"]["key"], encoding="utf-8"
        )
        print(f"Processing object: s3://{bucket}/{key}")

        response_head = s3.head_object(Bucket=bucket, Key=key)
        metadata = response_head.get("Metadata", {})
        doc_id = metadata.get("doc-id")

        if not doc_id:
            print(f"Error: 'doc-id' not found in metadata for object {key}. Aborting.")
            # Return a success status to S3 to prevent retries for this known issue.
            return {
                "statusCode": 200,
                "body": json.dumps("Missing doc-id in metadata."),
            }

        message = create_celery_message(
            task_name=CELERY_TASK_NAME, doc_id=doc_id, key=key
        )
        encoded_message = base64.b64encode(json.dumps(message).encode("utf-8")).decode(
            "utf-8"
        )

        print(
            f"Sending task to Celery. Task: {CELERY_TASK_NAME}, Key: {key}, Doc ID: {doc_id}"
        )

        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=encoded_message,
        )

        print("Task sent successfully.")
        return {
            "statusCode": 200,
            "body": json.dumps(f"Successfully dispatched task for doc_id: {doc_id}"),
        }

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        # Return an error to signal that the invocation failed.
        # S3 may retry invoking the function based on your configuration.
        return {"statusCode": 500, "body": json.dumps("An internal error occurred.")}
