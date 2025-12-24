"""SearchSuggestion Schemas"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SearchSuggestionBase(BaseModel):
    """Base schema for SearchSuggestion."""
    suggestion_text: str = Field(..., max_length=200)
    language: str = Field(default="en", max_length=10)


class SearchSuggestionCreate(SearchSuggestionBase):
    """Schema for creating a SearchSuggestion."""
    pass


class SearchSuggestionResponse(SearchSuggestionBase):
    """Schema for SearchSuggestion response."""
    id: UUID
    usage_count: int
    last_used_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
