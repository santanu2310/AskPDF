from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Text
from app.core.models import BaseModel


class Conversation(BaseModel):
    __tablename__ = "conversations"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)

    # Relationships
    documents = relationship("Document", back_populates="conversation")
    messages = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )


class Message(BaseModel):
    __tablename__ = "messages"

    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # "user" | "assistant"
    model: Mapped[str] = mapped_column(String(100), nullable=True)

    conversation = relationship("Conversation", back_populates="messages")
