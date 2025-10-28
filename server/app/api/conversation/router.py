from uuid import UUID
from typing import Annotated
from fastapi import APIRouter, Depends, Body
from app.core.embedder import Embedder, get_embedder
from app.core.db import get_db, AsyncSession
from app.core.schemas import UserAuthOut
from app.core.vector_store import get_vector_db, VectorStore
from app.core.dependency import (
    get_optional_user_from_access_token,
    get_id_from_access_token,
)
from .schemas import ConversationDetailOut, MessagePayload, Conversation
from .services import list_conversation, get_conversation, handle_message

router: APIRouter = APIRouter()


@router.post(path="/message")
async def query(
    payload: Annotated[MessagePayload, Body(...)],
    db: AsyncSession = Depends(get_db),
    vector_store: VectorStore = Depends(get_vector_db),
    embedder: Embedder = Depends(get_embedder),
    user: UserAuthOut = Depends(get_id_from_access_token),
):
    return await handle_message(
        payload=payload, user=user, db=db, embedder=embedder, store=vector_store
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
    user: UserAuthOut = Depends(get_optional_user_from_access_token),
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed information about a specific conversation, including its messages.
    """
    # Call the service function and return its result directly
    return await get_conversation(
        db=db, user=user, conversation_id=UUID(conversation_id)
    )
