from typing import Any
from chromadb.api.types import QueryResult
from fastapi import Request
import numpy as np
from chromadb import HttpClient
from chromadb.config import Settings
from chromadb.errors import ChromaError
import logging
from .exceptions import VectorStoreError

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

        except ChromaError as e:
            logger.exception(f"Failed to initialize VectorStore with ChromaDB: {e}")
            raise VectorStoreError("Vector store initialization failed.") from e
        except Exception as e:
            logger.exception(f"Failed to initialize VectorStore: {e}")
            raise VectorStoreError("Vector store initialization failed.") from e

    def add_embeddings(self, chunks: list[dict[str, Any]], embeddings: np.ndarray):
        """
        Store embedded chunks into the Chroma collection.
        """
        try:
            self.collection.add(
                embeddings=embeddings,
                documents=[chunk["text"] for chunk in chunks],
                metadatas=[
                    {"source": chunk["source"], "chunk_id": chunk["chunk_id"]}
                    for chunk in chunks
                ],
                ids=[f"{chunk['source']}_{chunk['chunk_id']}" for chunk in chunks],
            )

        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Failed to prepare or add embeddings: {e}")
            raise RuntimeError("Invalid input format while adding embeddings.") from e

        except Exception as e:
            logger.exception(f"Unexpected error in add_embeddings: {e}")
            raise RuntimeError("An error occurred while storing embeddings.") from e

    def query(
        self, embedding: np.ndarray, top_k: int = 5, doc_id: str | None = None
    ) -> QueryResult:
        if not self.collection:
            raise VectorStoreError("VectorStore is not initialized.")

        try:
            where_clause = {}

            if doc_id:
                where_clause["doc_id"] = doc_id

            results = self.collection.query(
                query_embeddings=embedding,
                n_results=top_k,
                where=where_clause
                if where_clause
                else None,  # Pass the where_clause here
            )

            logger.error(f"{results=}")

            return results

        except (KeyError, IndexError, ValueError) as e:
            logger.error(f"Failed to parse query results: {e}")

            raise RuntimeError(
                "Failed to parse query results from vector store."
            ) from e

        except Exception as e:
            logger.exception(f"Error querying vector store: {e}")

            raise RuntimeError("An error occurred during vector store query.") from e


def get_vector_db(request: Request):
    return request.state.vector_store
