import logging

from fastapi import Depends, Response
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db

from .schemas import TokenExchangeRequest
from .services import get_google_oauth_url, login_user_google_oauth

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(path="/oauth")
async def get_auth_url():
    return get_google_oauth_url()


@router.post(path="/exchange")
async def exchange_tokens(
    payload: TokenExchangeRequest, response: Response, db: AsyncSession = Depends(get_db)
):
    return await login_user_google_oauth(payload.state, payload.code, db, response)
