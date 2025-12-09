from pydantic import BaseModel, EmailStr

from app.core.models import Base


class TokenExchangeRequest(BaseModel):
    code: str
    state: str


class OauthUserData(BaseModel):
    email: EmailStr
    full_name: str
    profile_pic_url: str
