import asyncio
import logging
import numpy
from fastapi import Request
from sentence_transformers import SentenceTransformer
from app.core.exceptions import MessageProcessingError

logger = logging.getLogger(__name__)


class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    async def embed(self, texts: list[str]) -> numpy.ndarray:
        """
        Convert a list of text chunks into embeddings.
        """
        try:
            embeddings: numpy.ndarray = await asyncio.to_thread(
                self.model.encode, texts, show_progress_bar=True, convert_to_numpy=True
            )
            return embeddings

        except Exception as e:
            logger.error(f"Failed to embed text: {str(e)}")
            raise MessageProcessingError(message="Failed to embed text")


# FastAPI dependency that provides access to the pre-loaded embedder model.
# This avoids re-loading the heavy model on every single request.
def get_embedder(request: Request):
    return request.state.embedder
