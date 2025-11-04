import logging
from typing import Optional
from uuid import UUID
from app.core.embedder import Embedder
from app.core.vector_store import VectorStore
from app.core.exceptions import MessageProcessingError
from app.core.llm import LLMManager
from .schemas import RAGResponse

logger = logging.getLogger(__name__)


async def generate_augmented_response(
    query: str,
    embedder: Embedder,
    store: VectorStore,
    llm: LLMManager,
    doc_id: Optional[UUID] = None,
    top_k: int = 5,
) -> RAGResponse:
    try:
        query_embedding = await embedder.embed([query])
        results = store.query(query_embedding, doc_id=str(doc_id), top_k=top_k)

        if not results or not results.get("documents"):
            return RAGResponse(answer="No relevant documents found.", citations=[])

        logger.error(f"{results=}")
        context = "\n\n".join(results["documents"][0])
        prompt = (
            f"Answer the question based on the context below:\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {query}\n\n"
            f"Answer:"
        )

        response = await llm.generate_content_async(prompt)
        logger.error(f"{response=}")
        answar = {
            "answer": response.candidates[0].content.parts[0].text,
            "citations": [
                {"text": doc, "source": meta.get("doc_id")}
                for doc, meta in zip(results["documents"][0], results["metadatas"][0])
            ],
        }
        logger.error(f"{answar=}")
        return RAGResponse.model_validate(answar)

    # except requests.exceptions.RequestException as e:
    #     logger.critical(f"Request to LLM failed: {e}")
    #     raise MessageProcessingError(
    #         message="Failed to contact the language model API."
    #     )
    except Exception as e:
        logger.critical(e)
        raise MessageProcessingError(
            message="An internal error occurred while processing your request."
        )


async def generate_conversation_title(user_query: str, llm: LLMManager) -> str:
    """
    Generates a concise title for a conversation based on the user's query.
    """
    try:
        prompt = (
            f"Create a very concise title (5 words or less) for a conversation "
            f"based on the following user query. The title should capture the "
            f"essence of the query without being a direct restatement.\n\n"
            f"User Query: {user_query}\n\n"
            f"Title:"
        )
        response = await llm.generate_content_async(prompt)
        logger.error(f"{response=}")
        title = response.candidates[0].content.parts[0].text.strip()
        return title
    except Exception as e:
        logger.error(f"Error generating conversation title: {e}")
        return "New Conversation"  # Fallback title


# class RAGPipeline:
#     def __init__(self, embedder: Embedder, store: VectorStore):
#         self.embedder = embedder
#         self.store = store
#         self.ai_client = genai.Client(
#             api_key=settings.API_KEY, project=settings.GOOGLE_PROJECT_ID
#         )
#
#     async def run(self, query: str, top_k: int = 5) -> RAGResponse:
#         try:
#             query_embedding = await self.embedder.embed([query])
#             results = self.store.query(query_embedding, top_k=top_k)
#
#             if not results:
#                 return RAGResponse(answer="No relevant documents found.", citations=[])
#
#             context = "\n\n".join([r["text"] for r in results])
#             prompt = (
#                 f"Answer the legal question based on the context below:\n\n"
#                 f"Context:\n{context}\n\n"
#                 f"Question: {query}\n\n"
#                 f"Answer:"
#             )
#
#             response = self.call_llm(prompt)
#             answar = {
#                 "answer": response["candidates"][0]["content"]["parts"][0]["text"],
#                 "citations": [
#                     {"text": r["text"], "source": r["source"]} for r in results
#                 ],
#             }
#             return RAGResponse.model_validate(answar)
#
#         except requests.exceptions.RequestException as e:
#             logger.critical(f"Request to LLM failed: {e}")
#             raise MessageProcessingError(
#                 message="Failed to contact the language model API."
#             )
#         except Exception as e:
#             logger.critical(e)
#             raise MessageProcessingError(
#                 message="An internal error occurred while processing your request."
#             )
#
#     def call_llm(self, prompt: str) -> dict:
#         try:
#             response = await self.ai_client.models.generate_content(
#                 model="gemini-2.5-flash", contents="How does AI work?"
#             )
#             headers = {
#                 "Content-Type": "application/json",
#                 "X-goog-api-key": settings.API_KEY,
#             }
#
#             data = {"contents": [{"parts": [{"text": prompt}]}]}
#             response = requests.post(settings.API_ENDPOINT, headers=headers, json=data)
#             return response.json()
#
#         except requests.exceptions.RequestException as e:
#             logger.error(f"HTTP request to LLM failed: {e}")
#             raise RuntimeError("Failed to reach the language model API.") from e
#
#         except (KeyError, IndexError, ValueError) as e:
#             logger.error(e)
#             raise RuntimeError("Unexpected format in the LLM response.") from e
#
#         except Exception as e:
#             logger.exception(f"Unexpected error in LLM call: {e}")
#             raise RuntimeError(
#                 "An unexpected error occurred while calling the LLM."
#             ) from e
