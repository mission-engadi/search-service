"""Indexing Service

Handles indexing operations for searchable content.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from app.models.search_index import SearchIndex, DocumentType
from app.models.index_job import IndexJob, JobType, JobStatus
from app.schemas.search import IndexDocumentRequest


class IndexingService:
    """Service for handling indexing operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def index_document(self, request: IndexDocumentRequest) -> SearchIndex:
        """Index a single document."""
        # Parse published_at if provided
        published_at = None
        if request.published_at:
            try:
                published_at = datetime.fromisoformat(request.published_at)
            except ValueError:
                pass
        
        # Check if document already exists
        existing_query = select(SearchIndex).where(
            SearchIndex.document_id == request.document_id
        )
        result = await self.db.execute(existing_query)
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update existing document
            existing.title = request.title
            existing.content = request.content
            existing.language = request.language
            existing.metadata = request.metadata
            existing.author_id = request.author_id
            existing.author_name = request.author_name
            existing.status = request.status
            existing.published_at = published_at
            existing.updated_at = datetime.utcnow()
            
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            # Create new index
            search_index = SearchIndex(
                id=uuid4(),
                document_id=request.document_id,
                document_type=request.document_type,
                title=request.title,
                content=request.content,
                language=request.language,
                metadata=request.metadata,
                author_id=request.author_id,
                author_name=request.author_name,
                status=request.status,
                published_at=published_at,
                indexed_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db.add(search_index)
            await self.db.commit()
            await self.db.refresh(search_index)
            return search_index
    
    async def bulk_index(
        self,
        documents: List[IndexDocumentRequest],
        source_service: Optional[str] = None
    ) -> IndexJob:
        """Bulk index multiple documents."""
        # Create index job
        job = IndexJob(
            id=uuid4(),
            job_type=JobType.BULK,
            status=JobStatus.RUNNING,
            source_service=source_service,
            started_at=datetime.utcnow()
        )
        self.db.add(job)
        await self.db.commit()
        
        processed = 0
        failed = 0
        
        for doc in documents:
            try:
                await self.index_document(doc)
                processed += 1
            except Exception as e:
                failed += 1
                # Log error but continue processing
                print(f"Failed to index document {doc.document_id}: {str(e)}")
        
        # Update job
        job.documents_processed = processed
        job.documents_failed = failed
        job.status = JobStatus.COMPLETED if failed == 0 else JobStatus.FAILED
        job.completed_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(job)
        
        return job
    
    async def update_index(self, document_id: UUID, request: IndexDocumentRequest) -> Optional[SearchIndex]:
        """Update an indexed document."""
        query = select(SearchIndex).where(SearchIndex.document_id == document_id)
        result = await self.db.execute(query)
        index = result.scalar_one_or_none()
        
        if not index:
            return None
        
        # Parse published_at if provided
        published_at = None
        if request.published_at:
            try:
                published_at = datetime.fromisoformat(request.published_at)
            except ValueError:
                pass
        
        # Update fields
        index.title = request.title
        index.content = request.content
        index.language = request.language
        index.metadata = request.metadata
        index.author_id = request.author_id
        index.author_name = request.author_name
        index.status = request.status
        index.published_at = published_at
        index.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(index)
        
        return index
    
    async def delete_from_index(self, document_id: UUID) -> bool:
        """Delete a document from the index."""
        query = delete(SearchIndex).where(SearchIndex.document_id == document_id)
        result = await self.db.execute(query)
        await self.db.commit()
        
        return result.rowcount > 0
    
    async def reindex_all(self, source_service: Optional[str] = None) -> IndexJob:
        """Re-index all documents (placeholder - would need to fetch from other services)."""
        job = IndexJob(
            id=uuid4(),
            job_type=JobType.FULL_REINDEX,
            status=JobStatus.PENDING,
            source_service=source_service
        )
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        
        # This would typically trigger a background task to fetch
        # all documents from other services and re-index them
        
        return job
    
    async def clear_index(self) -> int:
        """Clear all documents from the index."""
        query = delete(SearchIndex)
        result = await self.db.execute(query)
        await self.db.commit()
        
        return result.rowcount
    
    async def get_index_stats(self) -> dict:
        """Get statistics about the search index."""
        from sqlalchemy import func
        
        # Total documents
        total_query = select(func.count(SearchIndex.id))
        total = (await self.db.execute(total_query)).scalar_one()
        
        # Documents by type
        type_query = select(
            SearchIndex.document_type,
            func.count(SearchIndex.id)
        ).group_by(SearchIndex.document_type)
        type_result = await self.db.execute(type_query)
        by_type = {row[0].value: row[1] for row in type_result}
        
        # Documents by language
        lang_query = select(
            SearchIndex.language,
            func.count(SearchIndex.id)
        ).group_by(SearchIndex.language)
        lang_result = await self.db.execute(lang_query)
        by_language = {row[0]: row[1] for row in lang_result}
        
        return {
            "total_documents": total,
            "by_type": by_type,
            "by_language": by_language
        }
