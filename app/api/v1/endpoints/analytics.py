"""Analytics Endpoints

API endpoints for search analytics and insights.
"""

from typing import List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.services.search_analytics_service import SearchAnalyticsService

router = APIRouter()


@router.get("/analytics/queries")
async def get_search_statistics(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get search query statistics.
    
    Requires authentication.
    
    Returns:
    - Total searches
    - Unique queries
    - Average results
    - Average execution time
    - Zero result rate
    """
    service = SearchAnalyticsService(db)
    return await service.get_search_stats(days)


@router.get("/analytics/popular")
async def get_popular_queries(
    limit: int = Query(20, ge=1, le=100),
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get most popular search queries.
    
    Requires authentication.
    
    Returns list of queries with:
    - Query text
    - Search count
    - Average results
    """
    service = SearchAnalyticsService(db)
    return await service.get_popular_queries(limit, days)


@router.get("/analytics/zero-results")
async def get_zero_result_queries(
    limit: int = Query(20, ge=1, le=100),
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get queries that returned zero results.
    
    Requires authentication.
    
    Useful for identifying gaps in content or improving search.
    """
    service = SearchAnalyticsService(db)
    return await service.get_zero_result_queries(limit, days)


@router.get("/analytics/performance")
async def get_performance_metrics(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get search performance metrics over time.
    
    Requires authentication.
    
    Returns daily metrics:
    - Date
    - Search count
    - Average execution time
    - Average results
    """
    service = SearchAnalyticsService(db)
    return await service.get_performance_metrics(days)
