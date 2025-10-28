from typing import Optional
from pydantic import BaseModel


class UploadRequest(BaseModel):
    file_name: str


class UploadSession(BaseModel):
    temp_id: Optional[str]
    doc_id: Optional[str]
    url: str
    fields: dict
