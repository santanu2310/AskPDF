from typing import Optional
from pydantic import BaseModel


class UploadSession(BaseModel):
    temp_id: Optional[str]
    doc_id: Optional[str]
    url: str
    fields: dict
