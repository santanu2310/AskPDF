from datetime import datetime
from pydantic import BaseModel


class UserAuthOut(BaseModel):
    user_id: str
    token: str | None = None
    expires_at: datetime | None = None
