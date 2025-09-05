import logging
from sqlalchemy.exc import SQLAlchemyError
from app.core.db import AsyncSession
from app.core.exceptions import DatabaseError
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
