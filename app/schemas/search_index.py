"""SearchIndex Schemas"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.search_index import DocumentType


class SearchIndexBase(BaseModel):
    """Base schema for SearchIndex."""
    document_id: UUID
    document_type: DocumentType
    title: str = Field(..., max_length=500)
    content: str
    language: str = Field(default="en", max_length=10)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    author_id: Optional[UUID] = None
    author_name: Optional[str] = Field(None, max_length=200)
    status: Optional[str] = Field(None, max_length=50)
    published_at: Optional[datetime] = None


class SearchIndexCreate(SearchIndexBase):
    """Schema for creating a SearchIndex."""
    pass


class SearchIndexUpdate(BaseModel):
    """Schema for updating a SearchIndex."""
    title: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    language: Optional[str] = Field(None, max_length=10)
    metadata: Optional[Dict[str, Any]] = None
    author_id: Optional[UUID] = None
    author_name: Optional[str] = Field(None, max_length=200)
    status: Optional[str] = Field(None, max_length=50)
    published_at: Optional[datetime] = None


class SearchIndexResponse(SearchIndexBase):
    """Schema for SearchIndex response."""
    id: UUID
    indexed_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SearchResult(BaseModel):
    """Individual search result with highlighting."""
    id: UUID
    document_id: UUID
    document_type: DocumentType
    title: str
    content_snippet: str
    highlighted_title: Optional[str] = None
    highlighted_content: Optional[str] = None
    language: str
    metadata: Dict[str, Any]
    author_name: Optional[str] = None
    published_at: Optional[datetime] = None
    relevance_score: Optional[float] = None
    
    class Config:
        from_attributes = True
