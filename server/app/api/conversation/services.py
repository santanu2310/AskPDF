import logging
from uuid import UUID
from app.core.db import AsyncSession
from app.core.schemas import UserAuthOut
from app.core.embedder import Embedder
from app.core.vector_store import VectorStore

from .schemas import MessagePayload, MessageResponse, Message as Message_S
from .crud import (
    create_conversation,
    create_message,
    get_conversations_by_user,
    get_conversation_with_messages,
)
from .rag import RAGPipeline
from .models import Conversation


logger = logging.getLogger(__name__)


async def handle_message(
    payload: MessagePayload,
    user: UserAuthOut,
    db: AsyncSession,
    embedder: Embedder,
    store: VectorStore,
) -> MessageResponse:
    created_at_time = None
    file_id = None

    if payload.conv_id:
        conv_id = payload.conv_id
    else:
        if not payload.file_id:
            raise ValueError("file_id is required for a new conversation.")

        conversation = await create_conversation(db=db, user_id=user.user_id)
        conv_id = conversation.id
        created_at_time = conversation.created_at

        # TODO: Update the document-s with conversation id

    user_message = await create_message(
        db=db, conversation_id=str(conv_id), content=payload.message, role="user"
    )

    rag = RAGPipeline(embedder=embedder, store=store)
    agent_response = await rag.run(query=payload.message, top_k=5)

    assistant_message = await create_message(
        db=db,
        conversation_id=str(conv_id),
        content=agent_response.answer,
        role="assistant",
    )

    user_msg_res = Message_S(
        id=user_message.id,
        text=user_message.content,
        conversation_id=conv_id,
        role="user",
        time_stamp=user_message.created_at,
    )
    assis_msg_res = Message_S(
        id=assistant_message.id,
        text=assistant_message.content,
        conversation_id=conv_id,
        role="assistant",
        time_stamp=assistant_message.created_at,
    )

    message_response = MessageResponse(
        conversation_id=conv_id,
        user_message=user_msg_res,
        assistant_message=assis_msg_res,
        created_at=created_at_time,
        file_id=file_id,
    )

    return message_response


async def list_conversation(db: AsyncSession, user: UserAuthOut) -> list[Conversation]:
    conversations = await get_conversations_by_user(db=db, user_id=UUID(user.user_id))
    return conversations


async def get_conversation(
    db: AsyncSession, conversation_id: UUID, user: UserAuthOut
) -> Conversation:
    db_conversation = await get_conversation_with_messages(
        db=db, conversation_id=conversation_id, user_id=UUID(user.user_id)
    )

    if not db_conversation:
        logger.warning(f"Conversation with id {conversation_id} not found.")
        raise ValueError(f"Conversation with id {conversation_id} does not exist.")

    return db_conversation
