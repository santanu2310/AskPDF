import logging
from typing import Optional
from uuid import UUID
from app.core.embedder import Embedder
from app.core.vector_store import VectorStore
from app.core.exceptions import LLMRequestFailedError, MessageProcessingError
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

        if not results or not results["documents"] or not results["metadatas"]:
            return RAGResponse(answer="No relevant documents found.", citations=[])

        logger.error(f"{results=}")
        context = "\n\n".join(results["documents"][0])
        prompt = (
            f"Answer the question based on the context below:\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {query}\n\n"
            f"Answer:"
        )

        response = await llm.generate_content(prompt)
        if (
            not response.candidates
            or not response.candidates[0].content
            or not response.candidates[0].content.parts
        ):
            raise LLMRequestFailedError(message="failed to generate response")

        logger.error(f"{response=}")
        answar = {
            "answer": response.candidates[0].content.parts[0].text,
            "citations": [
                {"text": doc, "source": meta.get("doc_id")}
                for doc, meta in zip(results["documents"][0], results["metadatas"][0])
            ],
        }
        return RAGResponse.model_validate(answar)

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
        response = await llm.generate_content(prompt)
        logger.error(f"{response=}")
        title = response.candidates[0].content.parts[0].text.strip()  # type: ignore
        return title
    except Exception as e:
        logger.error(f"Error generating conversation title: {e}")
        return "New Conversation"  # Fallback title
