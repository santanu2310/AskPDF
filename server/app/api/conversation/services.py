from datetime import datetime
import logging
from uuid import UUID
from app.core.db import AsyncSession
from app.core.schemas import UserAuthOut
from app.core.embedder import Embedder
from app.core.vector_store import VectorStore
from app.core.llm import LLMManager
from app.api.document.crud import associate_document_with_conversation

from .schemas import MessagePayload, MessageResponse, Message as Message_S
from .crud import (
    create_conversation,
    create_message,
    get_conversations_by_user,
    get_conversation_with_messages,
    get_document_ids_by_conversation,
)
from .rag import generate_augmented_response, generate_conversation_title
from .models import Conversation


logger = logging.getLogger(__name__)


async def handle_message(
    payload: MessagePayload,
    user: UserAuthOut,
    db: AsyncSession,
    embedder: Embedder,
    store: VectorStore,
    model_sm: LLMManager,
    model_lg: LLMManager,
) -> MessageResponse:
    created_at_time = None
    file_id = None
    logger.error(f"{payload=}")

    if payload.conv_id:
        conv_id = payload.conv_id
        logger.error(f"{conv_id=}")
        file_ids = await get_document_ids_by_conversation(
            db=db, conversation_id=conv_id, user_id=UUID(user.user_id)
        )
        logger.error(f"{file_ids=}")
        file_id = file_ids[0]
    else:
        if not payload.file_id:
            raise ValueError("file_id is required for a new conversation.")

        title = await generate_conversation_title(
            user_query=payload.message, llm=model_sm
        )
        logger.error(f"{title=}")

        conversation = await create_conversation(
            db=db, user_id=user.user_id, title=title
        )
        await associate_document_with_conversation(
            db=db,
            document_id=payload.file_id,
            conversation_id=conversation.id,
            user=user,
        )
        conv_id = conversation.id
        created_at_time = conversation.created_at

    user_message = await create_message(
        db=db, conversation_id=str(conv_id), content=payload.message, role="user"
    )

    agent_response = await generate_augmented_response(
        query=payload.message,
        embedder=embedder,
        store=store,
        llm=model_lg,
        doc_id=file_id,
        top_k=5,
    )

    assistant_message = await create_message(
        db=db,
        conversation_id=str(conv_id),
        content=agent_response.answer,
        role="assistant",
    )

    user_msg_res = Message_S(
        id=user_message.id,
        content=user_message.content,
        conversation_id=conv_id,
        role="user",
        time_stamp=user_message.created_at,
    )
    assis_msg_res = Message_S(
        id=assistant_message.id,
        content=assistant_message.content,
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
    db: AsyncSession, conversation_id: UUID, user: UserAuthOut, last_updated: datetime
) -> Conversation:
    db_conversation = await get_conversation_with_messages(
        db=db,
        conversation_id=conversation_id,
        user_id=UUID(user.user_id),
        last_updated=last_updated,
    )
    logger.info(f"{db_conversation=}")

    if not db_conversation:
        logger.warning(f"Conversation with id {conversation_id} not found.")
        raise ValueError(f"Conversation with id {conversation_id} does not exist.")

    return db_conversation
