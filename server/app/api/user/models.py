from app.core.models import BaseModel
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    profile_pic_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
