import logging
from datetime import datetime

from fastapi.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.user.schemas import OauthUserData
from app.core.exceptions import NotFoundError, TokenRevocationError, DatabaseError
from .models import User, RevokedRefToken

logger = logging.getLogger(name=__name__)


async def get_or_create_user(user_info: OauthUserData, db: AsyncSession) -> User:
    """Get existing user or create new user from Google user info"""

    try:
        # Check if user exists
        result = await db.execute(select(User).filter(User.email == user_info.email))
        user = result.scalar_one_or_none()

        # TODO: if user exists update the profile pic

        if not user:
            # Create new user
            user = User(
                email=user_info.email,
                full_name=user_info.full_name,
                profile_pic_url=user_info.profile_pic_url,
            )

            db.add(user)
            await db.commit()
            await db.refresh(user)

        return user
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error while creating user: {str(e)}")
        raise DatabaseError("Database error while creating user")


async def get_user_by_id(user_id: str, db: AsyncSession) -> User:
    """Get user by id"""
    try:
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise NotFoundError(f"User with id {user_id} not found")

        return user

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error while fetching user: {str(e)}")
        raise DatabaseError("Database error while fetching user")


async def add_token_to_db(
    token: str, expires_at: datetime, user_id: str, db: AsyncSession
) -> RevokedRefToken:
    """add the used refresh token to revoked_ref_token"""

    try:
        data = RevokedRefToken(token=token, expires_at=expires_at, user_id=user_id)
        db.add(data)
        await db.commit()

        return data

    except IntegrityError:
        await db.rollback()
        logger.warning(f"Token already revoked: {token[:10]}...")
        raise TokenRevocationError("Token has already been used")

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Failed to revoke token: {e}")
        raise DatabaseError("Database error while adding revoked token")
