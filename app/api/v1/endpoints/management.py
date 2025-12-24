"""Management Endpoints

API endpoints for search index management.
"""

from typing import Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db, get_current_user
from app.models.index_job import IndexJob, JobStatus
from app.schemas.index_job import IndexJobResponse
from app.services.indexing_service import IndexingService

router = APIRouter()


@router.get("/management/status")
async def get_index_status(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get search index status and statistics.
    
    Requires authentication.
    
    Returns:
    - Total documents
    - Documents by type
    - Documents by language
    """
    service = IndexingService(db)
    return await service.get_index_stats()


@router.post("/management/optimize")
async def optimize_index(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, str]:
    """Optimize search index.
    
    Requires authentication.
    
    Runs PostgreSQL VACUUM and ANALYZE on search tables.
    """
    try:
        # Run VACUUM ANALYZE on search_indexes table
        await db.execute(
            "VACUUM ANALYZE search_indexes;"
        )
        await db.commit()
        
        return {
            "success": True,
            "message": "Index optimization completed successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to optimize index: {str(e)}"
        )


@router.delete("/management/clear")
async def clear_index(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Clear all documents from the search index.
    
    Requires authentication.
    
    WARNING: This operation cannot be undone.
    """
    service = IndexingService(db)
    
    try:
        count = await service.clear_index()
        return {
            "success": True,
            "message": f"Cleared {count} documents from index",
            "documents_deleted": count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear index: {str(e)}"
        )


@router.get("/management/jobs", response_model=List[IndexJobResponse])
async def list_index_jobs(
    status: JobStatus = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> List[IndexJobResponse]:
    """List indexing jobs.
    
    Requires authentication.
    
    Filter by status and limit results.
    """
    query = select(IndexJob)
    
    if status:
        query = query.where(IndexJob.status == status)
    
    query = query.order_by(IndexJob.created_at.desc()).limit(limit)
    
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    return [IndexJobResponse.from_orm(job) for job in jobs]
