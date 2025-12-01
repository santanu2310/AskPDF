import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.exceptions import DatabaseError, NotFoundError
from .models import Conversation, Message

# Set up a logger for this module
logger = logging.getLogger(__name__)


# --- Conversation CRUD Functions ---


async def create_conversation(
    db: AsyncSession, user_id: str, title: str
) -> Conversation:
    """
    Creates a new, empty conversation for a specific user.

    Args:
        db: The AsyncSession instance for database interaction.
        user_id: The ID of the user creating the conversation.

    Returns:
        The newly created Conversation object.

    Raises:
        DatabaseError: If the database operation fails.
    """
    try:
        # Create a new conversation instance
        conversation = Conversation(user_id=user_id, title=title)
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        logger.info(
            f"Successfully created conversation {conversation.id} for user {user_id}."
        )
        return conversation
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Failed to create conversation for user {user_id}. Error: {e}")
        raise DatabaseError("Could not create a new conversation.")


async def get_conversation_by_id(
    db: AsyncSession, conversation_id: UUID, user_id: UUID
) -> Optional[Conversation]:
    """
    Retrieves a single conversation by its ID, without its messages or documents.

    Args:
        db: The AsyncSession instance.
        conversation_id: The ID of the conversation to retrieve.
        user_id: The ID of the user who owns the conversation.

    Returns:
        The Conversation object, or None if not found.

    Raises:
        DatabaseError: If the database query fails.
    """
    try:
        query = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    except SQLAlchemyError as e:
        logger.error(f"Failed to retrieve conversation {conversation_id}. Error: {e}")
        raise DatabaseError(
            f"Database error while fetching conversation '{conversation_id}'."
        )


async def get_conversation_with_messages(
    db: AsyncSession,
    conversation_id: UUID,
    user_id: UUID,
    last_updated: Optional[datetime] = None,
) -> Optional[Conversation]:
    """
    Retrieves a single conversation by its ID, including all its messages and doucments.

    Args:
        db: The AsyncSession instance.
        conversation_id: The ID of the conversation to retrieve.
        user_id: The ID of the user who owns the conversation.

    Returns:
        The Conversation object with its messages, or None if not found.

    Raises:
        DatabaseError: If the database query fails.
    """
    try:
        filter = [
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        ]
        if last_updated:
            filter.append(Conversation.updated_at > last_updated)

        query = (
            select(Conversation)
            .where(*filter)
            .options(
                selectinload(Conversation.messages),
                selectinload(Conversation.documents),
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    except SQLAlchemyError as e:
        logger.error(f"Failed to retrieve conversation {conversation_id}. Error: {e}")
        raise DatabaseError(
            f"Database error while fetching conversation '{conversation_id}'."
        )


async def get_conversations_by_user(
    db: AsyncSession, user_id: UUID
) -> List[Conversation]:
    """
    Retrieves all conversations for a given user, ordered by most recent.

    Args:
        db: The AsyncSession instance.
        user_id: The ID of the user whose conversations to retrieve.

    Returns:
        A list of Conversation objects.

    Raises:
        DatabaseError: If the database query fails.
    """
    try:
        # Assuming your BaseModel has a `created_at` timestamp
        query = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    except SQLAlchemyError as e:
        logger.error(f"Failed to retrieve conversations for user {user_id}. Error: {e}")
        raise DatabaseError(
            f"Database error while fetching conversations for user '{user_id}'."
        )


async def delete_conversation(
    db: AsyncSession, conversation_id: UUID, user_id: UUID
) -> Conversation:
    """
    Deletes a conversation and its associated messages from the database.

    Args:
        db: The AsyncSession instance.
        conversation_id: The ID of the conversation to delete.

    Returns:
        True if deletion was successful, False if the conversation was not found.

    Raises:
        DatabaseError: If the database operation fails.
    """
    try:
        conversation = await get_conversation_with_messages(
            db, conversation_id, user_id
        )
        logger.error(f"{conversation=}")
        if not conversation:
            logger.warning(
                f"Attempted to delete non-existent conversation with id {conversation_id}."
            )
            raise NotFoundError(
                message="Conversation with this given id doesnot exist."
            )

        await db.delete(conversation)
        await db.commit()
        logger.info(f"Successfully deleted conversation {conversation_id}.")
        return conversation

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Failed to delete conversation {conversation_id}. Error: {e}")
        raise DatabaseError(
            f"Database error while deleting conversation '{conversation_id}'."
        )


async def get_document_ids_by_conversation(
    db: AsyncSession, conversation_id: UUID, user_id: UUID
) -> List[UUID]:
    """
    Retrieves all document IDs associated with a given conversation.

    Args:
        db: The AsyncSession instance.
        conversation_id: The ID of the conversation.
        user_id: The ID of the user who owns the conversation.

    Returns:
        A list of document IDs.

    Raises:
        DatabaseError: If the database query fails.
    """
    try:
        conversation = await get_conversation_with_messages(
            db, conversation_id, user_id
        )
        if not conversation:
            logger.warning(
                f"Attempted to get documents from non-existent conversation with id {conversation_id}."
            )
            raise NotFoundError(message="no document found for this conversation")

        return [doc.id for doc in conversation.documents]

    except SQLAlchemyError as e:
        logger.error(
            f"Failed to retrieve document IDs for conversation {conversation_id}. Error: {e}"
        )
        raise DatabaseError(
            f"Database error while fetching document IDs for conversation '{conversation_id}'."
        )


async def update_conversation_title(
    db: AsyncSession, conversation_id: UUID, user_id: UUID, new_title: str
) -> Optional[Conversation]:
    """
    Updates the title of a specific conversation.

    Args:
        db: The AsyncSession instance.
        conversation_id: The ID of the conversation to update.
        user_id: The ID of the user who owns the conversation.
        new_title: The new title for the conversation.

    Returns:
        The updated Conversation object, or None if the conversation was not found.

    Raises:
        DatabaseError: If the database operation fails.
    """
    try:
        conversation = await get_conversation_by_id(db, conversation_id, user_id)
        if not conversation:
            logger.warning(
                f"Attempted to update non-existent conversation with id {conversation_id}."
            )
            return None

        conversation.title = new_title
        await db.commit()
        await db.refresh(conversation)
        logger.info(
            f"Successfully updated title for conversation {conversation_id} to '{new_title}'."
        )
        return conversation
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(
            f"Failed to update conversation {conversation_id} title. Error: {e}"
        )
        raise DatabaseError("Could not update conversation title.")


# --- Message CRUD Functions ---


async def create_message(
    db: AsyncSession,
    conversation_id: str,
    content: str,
    role: str,
    model: Optional[str] = None,
) -> Message:
    """
    Creates a new message and adds it to an existing conversation.

    Args:
        db: The AsyncSession instance.
        conversation_id: The ID of the conversation this message belongs to.
        content: The text content of the message.
        role: The role of the sender ('user' or 'assistant').
        model: (Optional) The model used to generate the message, if applicable.

    Returns:
        The newly created Message object.

    Raises:
        DatabaseError: If the database operation fails.
    """
    try:
        message = Message(
            conversation_id=conversation_id, content=content, role=role, model=model
        )
        db.add(message)
        await db.commit()
        await db.refresh(message)
        logger.info(
            f"Successfully created message {message.id} in conversation {conversation_id}."
        )
        return message

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(
            f"Failed to create message in conversation {conversation_id}. Error: {e}"
        )
        raise DatabaseError(
            f"Database error while creating message in conversation '{conversation_id}'."
        )
