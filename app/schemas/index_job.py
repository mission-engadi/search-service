"""IndexJob Schemas"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.index_job import JobType, JobStatus


class IndexJobBase(BaseModel):
    """Base schema for IndexJob."""
    job_type: JobType
    source_service: Optional[str] = Field(None, max_length=100)


class IndexJobCreate(IndexJobBase):
    """Schema for creating an IndexJob."""
    pass


class IndexJobUpdate(BaseModel):
    """Schema for updating an IndexJob."""
    status: Optional[JobStatus] = None
    documents_processed: Optional[int] = None
    documents_failed: Optional[int] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class IndexJobResponse(IndexJobBase):
    """Schema for IndexJob response."""
    id: UUID
    status: JobStatus
    documents_processed: int
    documents_failed: int
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
