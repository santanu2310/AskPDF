import logging
from typing import Optional
from uuid import UUID
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from app.core.db import AsyncSession
from app.core.exceptions import DatabaseError, NotFoundError
from app.core.schemas import UserAuthOut
from .models import TempDocument, Document


logger = logging.getLogger(name=__name__)


async def createTempDocs(key: str, title: str, db: AsyncSession) -> TempDocument:
    """Create a temporary document entry in the database."""

    try:
        data = TempDocument(key=key, title=title)
        db.add(data)
        await db.commit()
        await db.refresh(data)

        return data

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Failed to create TempDocument with {key=}, {title=}. Error:{e}")
        raise DatabaseError(f"Database error while creating TempDocument '{title}'")


async def createDocs(
    key: str, user: UserAuthOut, title: str, db: AsyncSession
) -> Document:
    """Create a temporary document entry in the database."""

    try:
        data = Document(key=key, title=title, owner_id=user.user_id)
        db.add(data)
        await db.commit()

        return data

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(
            f"Failed to create TempDocument with {key=}, {user=}, {title=}. Error:{e}"
        )
        raise DatabaseError(f"Database error while creating TempDocument '{title}'")


async def get_document(
    db: AsyncSession, document_id: UUID, user: UserAuthOut
) -> Optional[Document]:
    """Retrieves a document by its ID."""
    try:
        query = select(Document).where(
            Document.id == document_id, Document.owner_id == user.user_id
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        logger.error(f"Failed to retrieve document {document_id}. Error: {e}")
        raise DatabaseError(f"Database error while fetching document '{document_id}'.")


async def associate_document_with_conversation(
    db: AsyncSession, document_id: UUID, conversation_id: UUID, user: UserAuthOut
) -> Optional[Document]:
    """Associates a document with a conversation."""
    try:
        document = await get_document(db=db, document_id=document_id, user=user)
        if not document:
            logger.warning(
                f"Attempted to associate non-existent document with id {document_id}."
            )
            return None

        document.conversation_id = conversation_id
        await db.commit()
        await db.refresh(document)
        logger.info(
            f"Successfully associated document {document_id} with conversation {conversation_id}."
        )
        return document
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(
            f"Failed to associate document {document_id} with conversation {conversation_id}. Error: {e}"
        )
        raise DatabaseError("Could not associate document with conversation.")


async def delete_document(
    document_id: UUID, user: UserAuthOut, db: AsyncSession
) -> Document:
    """Delete a document entry from the database."""

    try:
        document = await get_document(db=db, document_id=document_id, user=user)
        if not document:
            logger.warning(
                f"Attempted to associate non-existent document with id {document_id}."
            )
            raise NotFoundError(message=f"Document not found with id: {document_id}")

        await db.delete(document)
        await db.commit()

        return document

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Failed to delete Document with {document_id=}. Error:{e}")
        raise DatabaseError("Database error while deleting Document")
