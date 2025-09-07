class DocumentProcessingError(Exception):
    """Base exception for our document processing pipeline."""

    def __init__(
        self, message="An error occurred during document processing.", detail=None
    ):
        self.message = message
        self.detail = detail
        super().__init__(self.message)

    def to_dict(self):
        return {"error": self.message, "detail": str(self.detail)}


class DocumentLoadError(DocumentProcessingError):
    """Raised when a document fails to load from S3."""

    pass


class EmbeddingError(DocumentProcessingError):
    """Raised when the embedding model fails."""

    pass


class VectorStoreError(DocumentProcessingError):
    """Raised when there's an issue with the vector database."""

    pass
