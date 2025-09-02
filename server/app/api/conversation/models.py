from typing import Optional
import secrets
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Text
from app.core.models import BaseModel


class Document(BaseModel):
    __tablename__ = "documents"

    title: Mapped[str] = mapped_column(String(255), nullable=True)
    key: Mapped[str] = mapped_column(String(512), nullable=False)

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    conversation_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
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


class Conversation(BaseModel):
    __tablename__ = "conversations"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Relationships
    documents = relationship("Document", back_populates="conversation")
    messages = relationship("Message", back_populates="conversation")


class Message(BaseModel):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # "user" | "assistant"
    model: Mapped[str] = mapped_column(String(100), nullable=True)

    conversation = relationship("Conversation", back_populates="messages")
