"""Indexing Endpoints

API endpoints for indexing operations.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.schemas.search import (
    IndexDocumentRequest,
    IndexResponse,
    BulkIndexRequest,
    BulkIndexResponse
)
from app.schemas.search_index import SearchIndexResponse
from app.services.indexing_service import IndexingService

router = APIRouter()


@router.post("/index/document", response_model=IndexResponse)
async def index_document(
    request: IndexDocumentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> IndexResponse:
    """Index a single document.
    
    Requires authentication.
    Creates or updates a document in the search index.
    """
    service = IndexingService(db)
    
    try:
        index = await service.index_document(request)
        return IndexResponse(
            success=True,
            message="Document indexed successfully",
            indexed_id=index.id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to index document: {str(e)}"
        )


@router.post("/index/bulk", response_model=BulkIndexResponse)
async def bulk_index(
    request: BulkIndexRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> BulkIndexResponse:
    """Bulk index multiple documents.
    
    Requires authentication.
    Creates an index job and processes all documents.
    """
    service = IndexingService(db)
    
    try:
        job = await service.bulk_index(request.documents, request.source_service)
        return BulkIndexResponse(
            success=True,
            message="Bulk indexing completed",
            job_id=job.id,
            documents_queued=len(request.documents)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk index: {str(e)}"
        )


@router.put("/index/{document_id}", response_model=IndexResponse)
async def update_indexed_document(
    document_id: UUID,
    request: IndexDocumentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> IndexResponse:
    """Update an indexed document.
    
    Requires authentication.
    """
    service = IndexingService(db)
    
    index = await service.update_index(document_id, request)
    
    if not index:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found in index"
        )
    
    return IndexResponse(
        success=True,
        message="Document updated successfully",
        indexed_id=index.id
    )


@router.delete("/index/{document_id}", response_model=IndexResponse)
async def delete_from_index(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> IndexResponse:
    """Delete a document from the index.
    
    Requires authentication.
    """
    service = IndexingService(db)
    
    deleted = await service.delete_from_index(document_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found in index"
        )
    
    return IndexResponse(
        success=True,
        message="Document deleted from index"
    )


@router.post("/index/reindex", response_model=IndexResponse)
async def reindex_all(
    source_service: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> IndexResponse:
    """Re-index all documents from all services.
    
    Requires authentication.
    Creates a reindex job and fetches all documents from other services.
    """
    service = IndexingService(db)
    
    try:
        job = await service.reindex_all(source_service)
        return IndexResponse(
            success=True,
            message="Re-indexing job created",
            job_id=job.id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create reindex job: {str(e)}"
        )
