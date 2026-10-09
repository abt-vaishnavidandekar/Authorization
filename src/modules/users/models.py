from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.configs.model import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    age: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    ph_no: Mapped[str] = mapped_column(
        String(15),
        nullable=False,
        unique=True
    )

    profile_image: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )