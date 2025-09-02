from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    TokenRevocationError,
    UserNotFoundError,
    InvalidOAuthCodeError,
    AuthenticationError,
    DatabaseError,
    S3ServiceError,
)


async def token_revocation_handler(request: Request, exc: TokenRevocationError):
    return JSONResponse(status_code=400, content={"detail": "Failed to revoke token"})


async def database_error_handler(request: Request, exc: DatabaseError):
    return JSONResponse(status_code=500, content={"detail": str(exc)})


async def user_not_found_handler(request: Request, exc: UserNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


async def invalid_oauth_handler(request: Request, exc: InvalidOAuthCodeError):
    return JSONResponse(
        status_code=400, content={"detail": "Invalid or expired OAuth code"}
    )


async def s3_service_error_handler(request: Request, exc: S3ServiceError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


async def authentication_error_handler(request: Request, exc: AuthenticationError):
    return JSONResponse(status_code=401, content={"detail": "Authentication failed"})


def add_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(TokenRevocationError, token_revocation_handler)
    app.add_exception_handler(UserNotFoundError, user_not_found_handler)
    app.add_exception_handler(InvalidOAuthCodeError, invalid_oauth_handler)
    app.add_exception_handler(AuthenticationError, authentication_error_handler)
    app.add_exception_handler(DatabaseError, database_error_handler)
    app.add_exception_handler(S3ServiceError, s3_service_error_handler)
