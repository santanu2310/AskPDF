import uuid
from typing import Optional
from app.core.db import AsyncSession
from app.core.schemas import UserAuthOut

from .s3_service import create_presigned_upload_url
from .crud import createDocs, createTempDocs
from .schemas import UploadSession


async def create_upload_session(
    title: str, db: AsyncSession, user: Optional[UserAuthOut]
) -> tuple[UploadSession, Optional[str]]:
    """Register a new upload session and persist document info."""

    temp = False if user else True
    temp_session_token: Optional[str] = None

    unique_id = str(uuid.uuid4()) + "-" + title.strip().replace(" ", "_").lower()
    key = f"temp/{unique_id}" if temp else f"docs/{unique_id}"

    if user:
        docs = await createDocs(key=key, user=user, title=title, db=db)
        # upload_session.doc_id = str(docs.id)
    else:
        docs = await createTempDocs(key=key, title=title, db=db)

        # upload_session.temp_id = str(docs.id)
        temp_session_token = docs.temp_token

    upload_session = create_presigned_upload_url(key=key, doc_id=str(docs.id))
    if user:
        upload_session.doc_id = str(docs.id)
    else:
        upload_session.temp_id = str(docs.id)
    return upload_session, temp_session_token
