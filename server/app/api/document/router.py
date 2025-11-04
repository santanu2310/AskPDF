import logging
from typing import Optional, Annotated
from fastapi import (
    APIRouter,
    Depends,
    Response,
    Body,
)

from app.core.db import AsyncSession, get_db
from app.core.dependency import (
    get_optional_user_from_access_token,
    get_id_from_access_token,
)
from app.core.schemas import UserAuthOut
from app.core.memory_db import SQLiteKVStore, get_memory_db
from .services import create_upload_session
from .schemas import UploadRequest


router = APIRouter()

logger = logging.getLogger(__name__)


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


@router.get("/status/{doc_id}")
async def get_file_status(
    doc_id: str,
    user: UserAuthOut = Depends(get_id_from_access_token),
    memory_db: SQLiteKVStore = Depends(get_memory_db),
):
    status = memory_db.get(doc_id)

    if not status:
        return {"id": doc_id, "status": "processing", "desc": "Going Multidimential"}

    return status
