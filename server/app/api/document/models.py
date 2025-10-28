from typing import Optional
import secrets
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from app.core.models import BaseModel


class Document(BaseModel):
    __tablename__ = "documents"

    title: Mapped[str] = mapped_column(String(255), nullable=True)
    key: Mapped[str] = mapped_column(String(512), nullable=False)

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    conversation_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), nullable=True
    )

    # Relationships
    conversation = relationship("Conversation", back_populates="documents")


class TempDocument(BaseModel):
    __tablename__ = "temp_documents"

    key: Mapped[str] = mapped_column(String(512), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=True)
    temp_token: Mapped[str] = mapped_column(
        String(512), nullable=False, default=lambda: secrets.token_urlsafe()
    )
