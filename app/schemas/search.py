"""Search Request/Response Schemas"""

from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.search_index import DocumentType
from app.schemas.search_index import SearchResult


class SearchRequest(BaseModel):
    """Schema for search requests."""
    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    document_types: Optional[List[DocumentType]] = Field(
        None,
        description="Filter by document types"
    )
    language: Optional[str] = Field(None, max_length=10, description="Language filter")
    author_id: Optional[UUID] = Field(None, description="Filter by author")
    status: Optional[str] = Field(None, description="Filter by status")
    date_from: Optional[str] = Field(None, description="Filter by date from (ISO format)")
    date_to: Optional[str] = Field(None, description="Filter by date to (ISO format)")
    metadata_filters: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata filters"
    )
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Results per page")
    sort_by: Optional[str] = Field(default="relevance", description="Sort field (relevance, date, title)")
    sort_order: Optional[str] = Field(default="desc", description="Sort order (asc, desc)")
    highlight: bool = Field(default=True, description="Enable result highlighting")


class SearchResponse(BaseModel):
    """Schema for search responses."""
    query: str
    results: List[SearchResult]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    execution_time: float  # milliseconds
    facets: Optional[Dict[str, List[Dict[str, Any]]]] = None


class AutoCompleteRequest(BaseModel):
    """Schema for autocomplete requests."""
    query: str = Field(..., min_length=1, max_length=100)
    language: Optional[str] = Field(None, max_length=10)
    limit: int = Field(default=10, ge=1, le=50)


class AutoCompleteResponse(BaseModel):
    """Schema for autocomplete responses."""
    query: str
    suggestions: List[str]


class FacetRequest(BaseModel):
    """Schema for facet requests."""
    query: str = Field(..., min_length=1, max_length=500)
    facet_fields: List[str] = Field(
        default=["document_type", "language", "author_name", "status"],
        description="Fields to generate facets for"
    )
    filters: Optional[Dict[str, Any]] = None


class FacetOption(BaseModel):
    """Individual facet option with count."""
    value: str
    count: int
    label: Optional[str] = None


class FacetResponse(BaseModel):
    """Schema for facet responses."""
    query: str
    facets: Dict[str, List[FacetOption]]
    total_results: int


class IndexDocumentRequest(BaseModel):
    """Schema for indexing a single document."""
    document_id: UUID
    document_type: DocumentType
    title: str = Field(..., max_length=500)
    content: str
    language: str = Field(default="en", max_length=10)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    author_id: Optional[UUID] = None
    author_name: Optional[str] = Field(None, max_length=200)
    status: Optional[str] = Field(None, max_length=50)
    published_at: Optional[str] = None  # ISO format


class BulkIndexRequest(BaseModel):
    """Schema for bulk indexing."""
    documents: List[IndexDocumentRequest]
    source_service: Optional[str] = Field(None, max_length=100)


class IndexResponse(BaseModel):
    """Schema for indexing responses."""
    success: bool
    message: str
    indexed_id: Optional[UUID] = None
    job_id: Optional[UUID] = None


class BulkIndexResponse(BaseModel):
    """Schema for bulk indexing responses."""
    success: bool
    message: str
    job_id: UUID
    documents_queued: int
