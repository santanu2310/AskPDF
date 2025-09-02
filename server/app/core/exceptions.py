class AppException(Exception):
    """Base class for custom app exceptions (optional, for grouping)."""

    pass


class TokenRevocationError(AppException):
    """Raised when a refresh token could not be revoked (DB failure)."""

    pass


class UserNotFoundError(AppException):
    """Raised when a user is not found in the database."""

    def __init__(self, message: str = "User not found"):
        super().__init__(message)


class DatabaseError(AppException):
    """Raised when database operation failed"""

    def __init__(self, message: str = "User not found"):
        super().__init__(message)


class InvalidOAuthCodeError(AppException):
    """Raised when an OAuth code is invalid or expired."""

    pass


class AuthenticationError(AppException):
    """Raised when authentication fails (invalid credentials, etc.)."""

    pass


class S3ServiceError(AppException):
    """Raised when S3 operations fail."""

    def __init__(self, message: str = "S3 operation failed"):
        super().__init__(message)
