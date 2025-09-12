import urllib.parse
import boto3
import hmac
import hashlib
import json
import logging
from typing import Literal, Optional
from botocore.config import Config
from core.embedder import Embedder
from core.document_loader import load_documents
from core.config import get_settings
from core.vector_store import VectorStore
from core.exceptions import DocumentLoadError, VectorStoreError, EmbeddingError

print("Loading function")

logger = logging.getLogger(__name__)

settings = get_settings()

s3 = boto3.client(
    "s3",
    aws_access_key_id="",
    aws_secret_access_key="",
    region_name="ap-south-1",
    config=Config(signature_version="s3v4"),
)


def send_status_update(
    doc_id: str, status: Literal["success", "failed"], reason: Optional[str] = None
):
    body = json.dumps({"doc_id": doc_id, "status": status, "reason": reason})

    signature = hmac.new(
        settings.HOOK_SECRET.encode(), body.encode(), hashlib.sha256
    ).hexdigest()

    headers = {"X-Signature": signature, "Content-Type": "application/json"}
    print(f"{body=}")
    # requests.post(settings.HOOK_URL, data=body, headers=headers)


def lambda_handler(event, context):
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(
        event["Records"][0]["s3"]["object"]["key"], encoding="utf-8"
    )
    response_head = s3.head_object(Bucket=bucket, Key=key)

    metadata = response_head.get("Metadata", {})
    doc_id = metadata.get(
        "doc-id"
    )  # print("Received event: " + json.dumps(event, indent=2))
    try:
        # Get the object from the event and show its content type
        bucket = event["Records"][0]["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(
            event["Records"][0]["s3"]["object"]["key"], encoding="utf-8"
        )
        # response_head = s3.head_object(Bucket=bucket, Key=key)

        # metadata = response_head.get("Metadata", {})
        # doc_id = metadata.get("doc-id")
        # doc_id = "rest_string"

        chunks = load_documents(bucket=bucket, key=key, s3=s3, doc_id=doc_id)
        texts = [chunk["text"] for chunk in chunks]

        embedder = Embedder()
        embeddings = embedder.embed(texts)

        vector_store = VectorStore(
            collection_name="askpdf",
            host=settings.VDB_URI,
            port=settings.VDB_PORT,
            auth_credentials=settings.VDB_SECRET_KEY,
        )
        vector_store.add_embeddings(chunks, embeddings)

        send_status_update(doc_id, "success")

    except DocumentLoadError:
        send_status_update(doc_id, "failed", "Failed to load document for processing")

    except EmbeddingError:
        send_status_update(
            doc_id, "failed", "Failed to create embeddings of the document"
        )

    except VectorStoreError:
        send_status_update(
            doc_id, "failed", "Failed storing processed data in vector store"
        )

    # except Exception:
    #     send_status_update(doc_id, "failed", "Failed processing file")
