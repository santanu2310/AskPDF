import logging
import numpy as np
from sentence_transformers import SentenceTransformer
from app.exceptions import EmbeddingError

logger = logging.getLogger(__name__)


class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        try:
            self.model = SentenceTransformer(model_name)
        except Exception as e:
            logger.exception(f"Failed to load SentenceTransformer model: {model_name}")
            raise EmbeddingError(
                "Failed to initialize the embedding model.", detail=str(e)
            ) from e

    def embed(self, texts: list[str]) -> np.ndarray:
        """
        Convert a list of text chunks into embeddings.
        """
        try:
            return self.model.encode(
                texts, show_progress_bar=True, convert_to_numpy=True
            )
        except Exception as e:
            logger.exception("An error occurred while generating embeddings.")
            raise EmbeddingError(
                "Failed to generate embeddings for the provided text.", detail=str(e)
            ) from e
