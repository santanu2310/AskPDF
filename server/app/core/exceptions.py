class AppException(Exception):
    """Base class for custom app exceptions (optional, for grouping)."""

    pass


class WebhookBaseException(Exception):
    """Base class for exceptions in this app."""

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.detail)


class TokenRevocationError(AppException):
    """Raised when a refresh token could not be revoked (DB failure)."""

    pass


class NotFoundError(AppException):
    """Raised when a user is not found in the database."""

    def __init__(self, message: str = "Not found"):
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


class MessageProcessingError(AppException):
    """Raised when user message fail."""

    def __init__(self, message: str = "Failed to process message"):
        super().__init__(message)


class InvalidPayloadException(WebhookBaseException):
    """
    Raised when the webhook payload validation fails.
    Defaults to a 400 Bad Request status code.
    """

    def __init__(self, detail: str = "Invalid webhook payload."):
        super().__init__(status_code=400, detail=detail)


class FileStateUpdateException(WebhookBaseException):
    """
    Raised when there's an internal error updating the file state.
    Defaults to a 500 Internal Server Error status code.
    """

    def __init__(self, detail: str = "Failed to update file state."):
        super().__init__(status_code=500, detail=detail)


class VectorStoreError(AppException):
    """Raised when there's an issue with the vector database."""

    def __init__(self, message: str = "Failed to update file state."):
        super().__init__(message)


class LLMRequestFailedError(AppException):
    """Raised when an LLM request fails."""

    def __init__(self, message: str = "LLM is busy or unavailable"):
        super().__init__(message)
