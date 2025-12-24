"""SearchQuery Model

Tracks search queries for analytics and improving search results.
"""

from datetime import datetime
import uuid

from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.db.base_class import Base


class SearchQuery(Base):
    """Model for tracking search queries and user behavior."""
    
    __tablename__ = "search_queries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_text = Column(String(500), nullable=False, index=True)
    language = Column(String(10), nullable=True)
    filters = Column(JSONB, default=dict)  # Applied filters
    results_count = Column(Integer, default=0)
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # If authenticated
    execution_time = Column(Float, nullable=True)  # Milliseconds
    clicked_result_id = Column(UUID(as_uuid=True), nullable=True)  # Which result was clicked
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index("idx_query_text_created", "query_text", "created_at"),
        Index("idx_user_created", "user_id", "created_at"),
        Index("idx_results_count", "results_count"),
    )
    
    def __repr__(self):
        return f"<SearchQuery '{self.query_text[:50]}'>"
