import requests
import logging
from app.core.embedder import Embedder
from app.core.vector_store import VectorStore
from app.core.config import settings
from app.core.exceptions import MessageProcessingError
from .schemas import RAGResponse

logger = logging.getLogger(__name__)


class RAGPipeline:
    def __init__(self, embedder: Embedder, store: VectorStore):
        self.embedder = embedder
        self.store = store

    async def run(self, query: str, top_k: int = 5) -> RAGResponse:
        try:
            query_embedding = await self.embedder.embed([query])
            results = self.store.query(query_embedding, top_k=top_k)

            if not results:
                return RAGResponse(answer="No relevant documents found.", citations=[])

            context = "\n\n".join([r["text"] for r in results])
            prompt = (
                f"Answer the legal question based on the context below:\n\n"
                f"Context:\n{context}\n\n"
                f"Question: {query}\n\n"
                f"Answer:"
            )

            response = self.call_llm(prompt)
            answar = {
                "answer": response["candidates"][0]["content"]["parts"][0]["text"],
                "citations": [
                    {"text": r["text"], "source": r["source"]} for r in results
                ],
            }
            return RAGResponse.model_validate(answar)

        except requests.exceptions.RequestException as e:
            logger.critical(f"Request to LLM failed: {e}")
            raise MessageProcessingError(
                message="Failed to contact the language model API."
            )
        except Exception as e:
            logger.critical(e)
            raise MessageProcessingError(
                message="An internal error occurred while processing your request."
            )

    def call_llm(self, prompt: str) -> dict:
        try:
            headers = {
                "Content-Type": "application/json",
                "X-goog-api-key": settings.API_KEY,
            }

            data = {"contents": [{"parts": [{"text": prompt}]}]}
            response = requests.post(settings.API_ENDPOINT, headers=headers, json=data)
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request to LLM failed: {e}")
            raise RuntimeError("Failed to reach the language model API.") from e

        except (KeyError, IndexError, ValueError) as e:
            logger.error(e)
            raise RuntimeError("Unexpected format in the LLM response.") from e

        except Exception as e:
            logger.exception(f"Unexpected error in LLM call: {e}")
            raise RuntimeError(
                "An unexpected error occurred while calling the LLM."
            ) from e
