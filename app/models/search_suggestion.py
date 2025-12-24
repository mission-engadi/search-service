"""SearchSuggestion Model

Stores popular search suggestions for autocomplete.
"""

from datetime import datetime
import uuid

from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID

from app.db.base_class import Base


class SearchSuggestion(Base):
    """Model for storing search suggestions and autocomplete data."""
    
    __tablename__ = "search_suggestions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    suggestion_text = Column(String(200), nullable=False, unique=True, index=True)
    language = Column(String(10), default="en", index=True)
    usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_suggestion_usage", "usage_count", "last_used_at"),
        Index("idx_suggestion_language", "language", "usage_count"),
    )
    
    def __repr__(self):
        return f"<SearchSuggestion '{self.suggestion_text}'>"
