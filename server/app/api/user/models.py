from datetime import datetime, timezone
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, validates
from sqlalchemy import ForeignKey
from app.core.models import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    profile_pic_url: Mapped[str | None] = mapped_column(String(500), nullable=True)


class RevokedRefToken(BaseModel):
    __tablename__ = "revoked_ref_tokens"
    token: Mapped[str] = mapped_column(String(300), nullable=False, unique=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    @validates("expires_at")
    def convert_to_naive_utc(self, key, value: datetime) -> datetime:
        if value.tzinfo is not None:
            # convert to UTC and strip tzinfo
            value = value.astimezone(timezone.utc).replace(tzinfo=None)
        return value
