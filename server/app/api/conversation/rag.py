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
    chat_history: list[object],
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

        context = "\n\n".join(results["documents"][0])
        prompt = (
            f"You are the 'Magical PDF Wizard', an insightful and empathetic AI thought partner. Your goal is to help users uncover knowledge hidden within their documents.\n\n### YOUR KNOWLEDGE BASE:\nThe following snippets are retrieved from the user's uploaded documents. Use ONLY this information to answer if possible:{context}\n\n### RULES OF MAGIC:\n1. Empathy First: Acknowledge the user's intent and maintain a warm, helpful, and slightly whimsical tone.\n2. Accuracy: If the answer is not contained within the provided Context above, state clearly that your 'crystal ball is foggy' regarding that specific detail, but offer a general helpful tip if relevant.\n3. Formatting: Use Markdown (bolding, bullet points) to make answers easy to read. \n4. Citations: If you find an answer, mention which part of the document it came from (e.g., 'According to the section on [Topic]...').\n\n"
            f"Chat History:\n{chat_history}\n\n"
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
        title = response.candidates[0].content.parts[0].text.strip()  # type: ignore
        return title
    except Exception as e:
        logger.error(f"Error generating conversation title: {e}")
        return "New Conversation"  # Fallback title
