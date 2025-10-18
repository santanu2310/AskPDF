from typing import Any
import numpy as np
from chromadb import HttpClient
from chromadb.config import Settings
import logging
from app.exceptions import VectorStoreError

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(
        self,
        collection_name: str,
        host: str,
        port: int,
        auth_credentials: str,
        token_header: str = "Authorization",
    ):
        try:
            self.client = HttpClient(
                host=host,
                port=port,
                settings=Settings(
                    chroma_client_auth_provider="chromadb.auth.token_authn.TokenAuthClientProvider",
                    chroma_client_auth_credentials=auth_credentials,
                    chroma_auth_token_transport_header=token_header,
                ),
            )

            self.collection = self.client.get_or_create_collection(name=collection_name)

        except Exception as e:
            logger.exception(f"Failed to initialize VectorStore: {e}")
            raise VectorStoreError(
                "Vector store initialization failed.", detail=str(e)
            ) from e

    def add_embeddings(self, chunks: list[dict[str, Any]], embeddings: np.ndarray):
        """
        Store embedded chunks into the Chroma collection.
        """
        try:
            self.collection.add(
                embeddings=embeddings,
                documents=[chunk["text"] for chunk in chunks],
                metadatas=[
                    {"doc_id": chunk["doc_id"], "chunk_id": chunk["chunk_id"]}
                    for chunk in chunks
                ],
                ids=[f"{chunk['doc_id']}_{chunk['chunk_id']}" for chunk in chunks],
            )

        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Failed to prepare or add embeddings: {e}")
            raise VectorStoreError(
                "Invalid input format for chunks or embeddings.", detail=str(e)
            ) from e
            # raise RuntimeError("Invalid input format while adding embeddings.") from e

        except Exception as e:
            logger.exception(f"Unexpected error in add_embeddings: {e}")
            raise VectorStoreError(
                "An unexpected error occurred while storing embeddings.", detail=str(e)
            ) from e
