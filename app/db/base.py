"""Database base classes and common models."""

from sqlalchemy.orm import DeclarativeBase

# Import all models here for Alembic to detect them
from app.db.base_class import Base  # noqa: F401
