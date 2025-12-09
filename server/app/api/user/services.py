import logging
from datetime import timedelta
from urllib.parse import unquote

from fastapi import HTTPException, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.schemas import UserAuthOut

from .crud import get_or_create_user, get_user_by_id as _get_user_by_id, add_token_to_db
from .oauth import GoogleSdkLoginFlowService, GithubSdkLoginFlowService
from .security import create_access_token, create_refresh_token

logger = logging.getLogger(__name__)


def _get_google_sdk() -> GoogleSdkLoginFlowService:
    return GoogleSdkLoginFlowService()


def _get_github_sdk() -> GithubSdkLoginFlowService:
    return GithubSdkLoginFlowService()


def get_google_oauth_url():
    return _get_google_sdk().get_authorization_url()


def get_github_oauth_url():
    return _get_github_sdk().get_authorization_url()


async def login_user_google_oauth(
    state: str, code: str, db: AsyncSession, response: Response
):
    try:
        google_sdk = _get_google_sdk()
        google_token = google_sdk.get_token(code=code, state=state)

        user_info = google_sdk.get_user_info(google_token=google_token)

        user = await get_or_create_user(user_info, db)

        access_token = create_access_token(
            user_id=str(user.id),
            expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        refresh_token = create_refresh_token(
            user_id=str(user.id),
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


async def login_user_github_oauth(
    state: str, code: str, db: AsyncSession, response: Response
):
    try:
        github_sdk = _get_github_sdk()
        github_token = github_sdk.get_token(code=code, state=state)

        user_info = github_sdk.get_user_info(github_token=github_token)
        logger.error(f"{ user_info= }")

        user = await get_or_create_user(user_info, db)
        logger.info(f"{ user= }")

        access_token = create_access_token(
            user_id=str(user.id),
            expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        refresh_token = create_refresh_token(
            user_id=str(user.id),
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


async def get_user_by_id(user_id: str, db: AsyncSession):
    return await _get_user_by_id(user_id, db)


async def refresh_token_pair(
    user_data: UserAuthOut, db: AsyncSession, response: Response
):
    """refresh token pair and blacklist the old refresh_token"""
    access_token = create_access_token(
        user_id=user_data.user_id,
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    refresh_token = create_refresh_token(
        user_id=user_data.user_id,
        expires_delta=timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
    )

    # Blacklist the old refresh token
    await add_token_to_db(
        token=unquote(user_data.token),
        expires_at=user_data.expires_at,
        user_id=user_data.user_id,
        db=db,
    )

    # Set HTTP-only cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        # secure=True,
        samesite="lax",
        max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        # secure=True,
        samesite="lax",
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return {"message": "Tokens refreshed successfully"}


async def logout(user_data: UserAuthOut, db: AsyncSession):
    """blacklist the old refresh_token and delete the tokens from cookies"""

    await add_token_to_db(
        token=unquote(user_data.token),
        expires_at=user_data.expires_at,
        user_id=user_data.user_id,
        db=db,
    )

    response = JSONResponse(content={"message": "Logout successful"}, status_code=200)

    # Clear cookies
    response.delete_cookie(
        key="access_token",
        httponly=True,
        # secure=True,
        samesite="lax",
    )
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        # secure=True,
        samesite="lax",
    )

    return response
