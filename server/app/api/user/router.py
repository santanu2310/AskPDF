import logging

from fastapi import Depends, Response
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.schemas import UserAuthOut
from app.core.dependency import get_id_from_access_token, get_id_from_refresh_token

from .schemas import TokenExchangeRequest
from .services import (
    get_google_oauth_url,
    login_user_google_oauth,
    get_user_by_id,
    refresh_token_pair as _refresh_token_pair,
    logout as _logout,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(path="/authorize/{provider}")
async def get_auth_url():
    url = get_google_oauth_url()[0]
    return {"url": url}


@router.post(path="/exchange")
async def exchange_tokens(
    payload: TokenExchangeRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    return await login_user_google_oauth(payload.state, payload.code, db, response)


@router.get(path="/me")
async def user_info(
    user: UserAuthOut = Depends(get_id_from_access_token),
    db: AsyncSession = Depends(get_db),
):
    logger.error(f"User: {user}")
    return await get_user_by_id(user.user_id, db)


@router.post(path="/refresh")
async def refresh_token_pair(
    response: Response,
    user: UserAuthOut = Depends(get_id_from_refresh_token),
    db: AsyncSession = Depends(get_db),
):
    return await _refresh_token_pair(user_data=user, db=db, response=response)


@router.get(path="/logout")
async def logout(
    user: UserAuthOut = Depends(get_id_from_access_token),
    db: AsyncSession = Depends(get_db),
):
    return _logout(user_data=user, db=db)
