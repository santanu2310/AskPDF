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
from app.core.memory_db import SQLiteKVStore, get_memory_db
from .services import create_upload_session, update_file_state
from .schemas import UploadRequest


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


@router.post("/webhook")
async def webhook(
    request: Request,
    x_signature: Annotated[str | None, Header()] = None,
    memory_db: SQLiteKVStore = Depends(get_memory_db),
):
    body = await request.body()
    # signature = request.headers.get("X-Signature")

    expected = hmac.new(
        settings.WEBHOOK_SECRET.encode(), body, hashlib.sha256
    ).hexdigest()

    if not x_signature:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Missing x_signature"
        )

    if not hmac.compare_digest(x_signature, expected):
        raise HTTPException(status_code=401, detail="Invalid signature")

    data = await request.json()
    await update_file_state(body=data, memory_db=memory_db)

    return {"status": "ok"}
