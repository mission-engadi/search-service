"""IndexJob Model

Tracks indexing jobs and their status.
"""

from datetime import datetime
from enum import Enum as PyEnum
import uuid

from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    DateTime,
    Enum,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID

from app.db.base_class import Base


class JobType(str, PyEnum):
    """Types of indexing jobs."""
    FULL_REINDEX = "full_reindex"
    INCREMENTAL = "incremental"
    SINGLE_DOCUMENT = "single_document"
    BULK = "bulk"


class JobStatus(str, PyEnum):
    """Status of indexing jobs."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class IndexJob(Base):
    """Model for tracking indexing jobs."""
    
    __tablename__ = "index_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_type = Column(Enum(JobType), nullable=False)
    status = Column(Enum(JobStatus), nullable=False, default=JobStatus.PENDING, index=True)
    source_service = Column(String(100), nullable=True)  # Which service triggered indexing
    documents_processed = Column(Integer, default=0)
    documents_failed = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index("idx_job_status_created", "status", "created_at"),
        Index("idx_job_type_status", "job_type", "status"),
    )
    
    def __repr__(self):
        return f"<IndexJob {self.job_type}:{self.status}>"
