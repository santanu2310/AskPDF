import logging
from datetime import timedelta
from urllib.parse import unquote

from fastapi import HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings

from .crud import get_or_create_user
from .oauth import GoogleSdkLoginFlowService
from .security import create_access_token, create_refresh_token

GoogleSDK = GoogleSdkLoginFlowService()
logger = logging.getLogger(__name__)


def get_google_oauth_url():
    return GoogleSDK.get_authorization_url()


async def login_user_google_oauth(
    state: str, code: str, db: AsyncSession, response: Response
):
    try:
        # URL decode the code to handle potential encoding issues
        decoded_code = unquote(code)
        google_token = GoogleSDK.get_token(code=decoded_code, state=state)
        logger.error(f"Google token: {google_token}")
        user_info = GoogleSDK.get_user_info(google_token=google_token)
        logger.error(f"User info: {user_info}")

        user = await get_or_create_user(user_info, db)

        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        refresh_token = create_refresh_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        )

        # Set HTTP-only cookies
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )

        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "profile_pic_url": user.profile_pic_url,
        }

    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(status_code=400, detail="Login failed")
