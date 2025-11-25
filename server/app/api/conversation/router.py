from datetime import datetime
import logging
from uuid import UUID
from typing import Annotated
from fastapi import APIRouter, Depends, Body
from app.core.embedder import Embedder, get_embedder
from app.core.db import get_db, AsyncSession
from app.core.schemas import UserAuthOut
from app.core.vector_store import get_vector_db, VectorStore
from app.core.llm import LLMManager, get_llm_sm, get_llm_lg
from app.core.dependency import (
    get_optional_user_from_access_token,
    get_id_from_access_token,
)
from .schemas import (
    ConversationDetailOut,
    MessagePayload,
    Conversation,
    UpdateConversation,
)
from .services import (
    list_conversation,
    get_conversation,
    handle_message,
    change_conv_title,
)

router: APIRouter = APIRouter()

logger = logging.getLogger(__name__)


@router.post(path="/message")
async def query(
    payload: Annotated[MessagePayload, Body(...)],
    db: AsyncSession = Depends(get_db),
    vector_store: VectorStore = Depends(get_vector_db),
    embedder: Embedder = Depends(get_embedder),
    user: UserAuthOut = Depends(get_id_from_access_token),
    llm_lg: LLMManager = Depends(get_llm_lg),
    llm_sm: LLMManager = Depends(get_llm_sm),
):
    return await handle_message(
        payload=payload,
        user=user,
        db=db,
        embedder=embedder,
        store=vector_store,
        model_lg=llm_lg,
        model_sm=llm_sm,
    )


@router.get("/all", response_model=list[Conversation])
async def read_user_conversations(
    user: UserAuthOut = Depends(get_optional_user_from_access_token),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all conversations for the current user.
    """
    # Call the service function and return its result directly
    return await list_conversation(db=db, user=user)


@router.get("/{conversation_id}", response_model=ConversationDetailOut)
async def get_conversation_details(
    conversation_id: str,
    last_updated: datetime,
    user: UserAuthOut = Depends(get_optional_user_from_access_token),
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed information about a specific conversation, including its messages.
    """
    # Call the service function and return its result directly
    return await get_conversation(
        db=db,
        user=user,
        conversation_id=UUID(conversation_id),
        last_updated=last_updated,
    )


@router.put("/{conversation_id}")
async def update_conv_title(
    payload: Annotated[UpdateConversation, Body(...)],
    db: AsyncSession = Depends(get_db),
    user: UserAuthOut = Depends(get_id_from_access_token),
):
    logger.error(f"title update data: {payload}")
    return await change_conv_title(data=payload, db=db, user=user)
