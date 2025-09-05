import hmac
import hashlib
from typing import Optional, Annotated
from fastapi import (
    APIRouter,
    Depends,
    Response,
    Body,
    Request,
    HTTPException,
    status,
    Header,
)

from app.core.db import AsyncSession, get_db
from app.core.dependency import get_optional_user_from_access_token
from app.core.schemas import UserAuthOut
from app.core.config import settings
from .services import create_upload_session
from .schemas import UploadRequest, WebhookPayload


router = APIRouter()


@router.post("/upload")
async def doc_upload_session(
    response: Response,
    data: Annotated[UploadRequest, Body(...)],
    user: Optional[UserAuthOut] = Depends(get_optional_user_from_access_token),
    db: AsyncSession = Depends(get_db),
):
    upload_session, session_token = await create_upload_session(
        user=user, db=db, title=data.file_name
    )
    if session_token:
        response.set_cookie(
            key="temp_session",
            value=session_token,
            httponly=True,
            expires="Session",
            samesite="lax",
        )

    return upload_session
