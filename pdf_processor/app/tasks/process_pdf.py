import boto3
import logging
from typing import Literal, Optional
from botocore.config import Config
from app.models.embedder import Embedder
from app.document_processing.document_loader import load_documents
from app.queue.sqs import publish_status_to_sqs
from app.config import get_settings
from app.store.vector_store import VectorStore
from app.exceptions import DocumentLoadError, VectorStoreError, EmbeddingError
from app.celery_app import celery_app

print("Loading function")

logger = logging.getLogger(__name__)

settings = get_settings()

s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
    config=Config(signature_version="s3v4"),
)


def send_status_update(
    doc_id: str, status: Literal["success", "failed"], reason: Optional[str] = None
):
    body = {"doc_id": doc_id, "status": status, "reason": reason}
    publish_status_to_sqs(queue_name=settings.SQS_QUEUE_NAME, message_body=body)


@celery_app.task
def process_pdf(doc_id, key):
    try:
        chunks = load_documents(
            bucket=settings.BUCKET_NAME, key=key, s3=s3, doc_id=doc_id
        )
        texts = [chunk["text"] for chunk in chunks]

        embedder = Embedder()
        embeddings = embedder.embed(texts)

        vector_store = VectorStore(
            collection_name=settings.COLLECTION_NAME,
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

    except Exception as e:
        logger.error(e)
        send_status_update(doc_id, "failed", "Failed processing file")
