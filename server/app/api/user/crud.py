import logging

from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User

logger = logging.getLogger(name=__name__)


async def get_or_create_user(user_info: dict, db: AsyncSession) -> User:
    """Get existing user or create new user from Google user info"""
    email = user_info.get("email")
    logger.info(f"User email: {email}")
    if not email:
        raise HTTPException(status_code=400, detail="Email not provided by Google")

    # Check if user exists
    from sqlalchemy import select

    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        # Create new user
        user = User(
            email=email,
            full_name=user_info.get("given_name", ""),
            profile_pic_url=user_info.get("picture", ""),
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"Created new user: {email}")

    return user
