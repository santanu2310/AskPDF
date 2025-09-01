import jwt
import logging
from typing import Annotated
from fastapi import HTTPException, status, Cookie
from app.core.config import settings
from app.core.schemas import UserAuthOut

logger = logging.getLogger(__name__)


def decode_token(
    token: str,
    secret_key: str,
    algorithm: str = settings.JWT_ALGORITHM,
    with_token: bool = False,
) -> UserAuthOut:
    try:
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=[algorithm],
        )

        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        return (
            UserAuthOut(user_id=user_id)
            if not with_token
            else UserAuthOut(
                user_id=user_id, token=token, expires_at=payload.get("exp")
            )
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


async def get_id_from_access_token(
    refresh_token: Annotated[str, Cookie(alias="access_token")],
) -> UserAuthOut:
    return decode_token(refresh_token, settings.JWT_ACCESS_SECRET_KEY)


async def get_id_from_refresh_token(
    refresh_token: Annotated[str, Cookie(alias="refresh_token")],
) -> UserAuthOut:
    return decode_token(refresh_token, settings.JWT_REFRESH_SECRET_KEY, with_token=True)
