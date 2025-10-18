import io
from typing import Any, Optional
from pypdf import PdfReader
import logging
from botocore.client import BaseClient
from app.exceptions import DocumentLoadError


CHUNK_SIZE = 300
OVERLAP = 50

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_data: bytes) -> str:
    try:
        pdf_file = io.BytesIO(file_data)
        doc = PdfReader(pdf_file)

        return "\n".join(page.extract_text() for page in doc.pages)

    except Exception as e:
        logger.warning(f"Invalid PDF: {e}")
        raise DocumentLoadError(
            "Failed to extract text from PDF.", detail=str(e)
        ) from e


# def extract_text_from_docx(file_data: bytes) -> str:
#     try:
#         docx_file = io.BytesIO(file_data)
#         doc = Document(docx_file)
#         return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
#
#     except Exception as e:
#         logger.warning(f"Could not parse DOCX file: {e}")
#         raise DocumentLoadError(
#             "Failed to extract text from DOCX.", detail=str(e)
#         ) from e
#


def chunk_text(text: str, doc_id: str) -> list[dict[str, Any]]:
    chunks = []
    start = 0
    chunk_id = 0
    try:
        while start < len(text):
            end = min(start + CHUNK_SIZE, len(text))
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(
                    {"text": chunk_text, "doc_id": doc_id, "chunk_id": chunk_id}
                )
                chunk_id += 1
            start += CHUNK_SIZE - OVERLAP
        return chunks

    except Exception as e:
        logger.error(f"Error while chunking text: {e}")
        raise DocumentLoadError(
            f"Failed to chunk document with id: {doc_id}", detail=str(e)
        ) from e


def load_documents(
    bucket: str, key: str, s3: BaseClient, doc_id: str
) -> list[dict[str, Any]]:
    """
    Load and chunk documents from a folder.
    Returns a list of dicts with: text, source, chunk_id
    """
    text: Optional[str] = None

    response = s3.get_object(Bucket=bucket, Key=key)
    file_data = response["Body"].read()
    content_type = response.get("ContentType")

    try:
        text = extract_text_from_pdf(file_data)
        # elif content_type == "docx":
        #     text = extract_text_from_docx(file_data)
        # else:
        #     raise DocumentLoadError(
        #         f"Unsupported content type: '{content_type}'", detail={"key": key}
        #     )

        if not text:
            raise DocumentLoadError(
                "Text extraction resulted in empty content.", detail={"key": key}
            )

        file_chunks = chunk_text(text, doc_id=doc_id)

        return file_chunks

    except Exception as e:
        logger.error(f"Failed to process file with key: {key} - {e}")
        raise DocumentLoadError(
            "An unexpected error occurred during document loading.", detail=str(e)
        ) from e
