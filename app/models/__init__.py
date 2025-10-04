# app/models/__init__.py
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Import models so they’re registered when Base.metadata.create_all() is called
from .user import User, Role
