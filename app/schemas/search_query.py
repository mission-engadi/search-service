"""SearchQuery Schemas"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


class SearchQueryBase(BaseModel):
    """Base schema for SearchQuery."""
    query_text: str = Field(..., max_length=500)
    language: Optional[str] = None
    filters: Dict[str, Any] = Field(default_factory=dict)
    results_count: int = 0


class SearchQueryCreate(SearchQueryBase):
    """Schema for creating a SearchQuery."""
    user_id: Optional[UUID] = None
    execution_time: Optional[float] = None


class SearchQueryResponse(SearchQueryBase):
    """Schema for SearchQuery response."""
    id: UUID
    user_id: Optional[UUID] = None
    execution_time: Optional[float] = None
    clicked_result_id: Optional[UUID] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
