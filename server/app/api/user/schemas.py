from pydantic import BaseModel


class TokenExchangeRequest(BaseModel):
    code: str
    state: str
