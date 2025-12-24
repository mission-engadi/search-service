"""SearchIndex Model

Main table for storing searchable content from all services.
Uses PostgreSQL tsvector for full-text search.
"""

from datetime import datetime
from enum import Enum as PyEnum
import uuid

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    Enum,
    Index,
    func,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, TSVECTOR

from app.db.base_class import Base


class DocumentType(str, PyEnum):
    """Types of documents that can be indexed."""
    ARTICLE = "article"
    STORY = "story"
    PARTNER = "partner"
    PROJECT = "project"
    SOCIAL_POST = "social_post"
    NOTIFICATION = "notification"
    CAMPAIGN = "campaign"


class SearchIndex(Base):
    """Model for storing searchable content with full-text search support."""
    
    __tablename__ = "search_indexes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    document_type = Column(Enum(DocumentType), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    language = Column(String(10), default="en", index=True)  # en, es, fr, pt
    metadata = Column(JSONB, default=dict)  # Additional searchable fields
    search_vector = Column(TSVECTOR)  # PostgreSQL full-text search vector
    
    # Additional fields for filtering and sorting
    author_id = Column(UUID(as_uuid=True), nullable=True)
    author_name = Column(String(200), nullable=True)
    status = Column(String(50), nullable=True)
    published_at = Column(DateTime, nullable=True)
    
    # Timestamps
    indexed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        # GIN index for full-text search - most important index
        Index(
            "idx_search_vector",
            search_vector,
            postgresql_using="gin"
        ),
        # Composite indexes for common queries
        Index("idx_document_type_language", "document_type", "language"),
        Index("idx_published_at", "published_at"),
        Index("idx_author_id", "author_id"),
        # JSONB index for metadata queries
        Index(
            "idx_metadata",
            metadata,
            postgresql_using="gin"
        ),
    )
    
    def __repr__(self):
        return f"<SearchIndex {self.document_type}:{self.document_id}>"
