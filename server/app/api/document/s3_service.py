# import uuid
import logging
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from app.core.exceptions import S3ServiceError
from app.core.config import settings
from .schemas import UploadSession


logger = logging.getLogger(__name__)


def create_presigned_upload_url(key: str, doc_id: str) -> UploadSession:
    conditions = [
        ["content-length-range", 0, 20971520],  # 20 MB limit
        {"x-amz-meta-doc-id": doc_id},
    ]

    # unique_id = str(uuid.uuid4()) + "-" + file_name.strip().replace(" ", "_").lower()
    # key = f"temp/{unique_id}" if temp else f"docs/{unique_id}"

    # Generate a presigned S3 POST URL
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY,
        region_name="ap-south-1",
        config=Config(signature_version="s3v4"),
    )

    try:
        response = s3_client.generate_presigned_post(
            settings.BUCKET_NAME,
            key,
            Fields={"x-amz-meta-doc-id": doc_id},
            Conditions=conditions,
            ExpiresIn=360,
        )

        return UploadSession(
            temp_id=None,
            doc_id=None,
            url=response["url"],
            fields=response["fields"],
        )

    except ClientError as e:
        logger.error(f"Failed to generate presigned URL: {e}")
        raise S3ServiceError("Failed to generate presigned URL")


async def create_presigned_download_url(key: str):
    # Generate a S3 Slient
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY,
        region_name="ap-south-1",
        config=Config(signature_version="s3v4"),
    )
    try:
        # Generate a presigned GET URL
        response = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.BUCKET_NAME, "Key": key},
            ExpiresIn=600,
        )

        return response

    except ClientError as e:
        logger.error(f"Failed to generate presigned URL: {e}")
        raise S3ServiceError("Failed to generate presigned URL")
