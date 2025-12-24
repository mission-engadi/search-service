"""Autocomplete Endpoints

API endpoints for autocomplete and suggestions.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user, get_current_user_optional
from app.schemas.search import AutoCompleteRequest, AutoCompleteResponse
from app.services.autocomplete_service import AutoCompleteService

router = APIRouter()


@router.get("/autocomplete", response_model=AutoCompleteResponse)
async def get_autocomplete(
    query: str = Query(..., min_length=1, max_length=100),
    language: str = Query(None, max_length=10),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
) -> AutoCompleteResponse:
    """Get autocomplete suggestions.
    
    Returns suggestions based on:
    - Trigram similarity
    - Popular searches
    - Prefix matching
    """
    service = AutoCompleteService(db)
    suggestions = await service.get_suggestions(query, language, limit)
    
    return AutoCompleteResponse(
        query=query,
        suggestions=suggestions
    )


@router.get("/autocomplete/popular", response_model=AutoCompleteResponse)
async def get_popular_searches(
    language: str = Query(None, max_length=10),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
) -> AutoCompleteResponse:
    """Get popular search suggestions.
    
    Returns the most frequently searched terms.
    """
    service = AutoCompleteService(db)
    suggestions = await service.get_popular_searches(language, limit)
    
    return AutoCompleteResponse(
        query="",
        suggestions=suggestions
    )


@router.get("/autocomplete/recent", response_model=AutoCompleteResponse)
async def get_recent_searches(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> AutoCompleteResponse:
    """Get recent searches for the current user.
    
    Requires authentication.
    """
    service = AutoCompleteService(db)
    user_id = UUID(current_user["sub"])
    suggestions = await service.get_recent_searches(user_id, limit)
    
    return AutoCompleteResponse(
        query="",
        suggestions=suggestions
    )
