from typing import List, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey
from . import Base

class Role(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    users: Mapped[List["User"]] = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    role_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("roles.id"), nullable=True)

    role: Mapped["Role"] = relationship("Role", back_populates="users")
