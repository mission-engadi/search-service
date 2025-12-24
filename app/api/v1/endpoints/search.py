"""Search Endpoints

API endpoints for search operations.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user_optional
from app.models.search_index import DocumentType
from app.schemas.search import SearchRequest, SearchResponse
from app.services.search_service import SearchService

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def universal_search(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional)
) -> SearchResponse:
    """Universal search across all content types.
    
    - **query**: Search query (required)
    - **document_types**: Filter by document types (optional)
    - **language**: Language filter (optional)
    - **page**: Page number (default: 1)
    - **page_size**: Results per page (default: 20, max: 100)
    """
    service = SearchService(db)
    user_id = UUID(current_user["sub"]) if current_user else None
    return await service.search(request, user_id)


@router.post("/search/content", response_model=SearchResponse)
async def search_content(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional)
) -> SearchResponse:
    """Search content (articles, stories).
    
    Searches only within article and story document types.
    """
    service = SearchService(db)
    user_id = UUID(current_user["sub"]) if current_user else None
    
    # Filter to content types
    request.document_types = [DocumentType.ARTICLE, DocumentType.STORY]
    
    return await service.search(request, user_id)


@router.post("/search/partners", response_model=SearchResponse)
async def search_partners(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional)
) -> SearchResponse:
    """Search partners.
    
    Searches only within partner document type.
    """
    service = SearchService(db)
    user_id = UUID(current_user["sub"]) if current_user else None
    return await service.search_by_type(DocumentType.PARTNER, request, user_id)


@router.post("/search/projects", response_model=SearchResponse)
async def search_projects(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional)
) -> SearchResponse:
    """Search projects.
    
    Searches only within project document type.
    """
    service = SearchService(db)
    user_id = UUID(current_user["sub"]) if current_user else None
    return await service.search_by_type(DocumentType.PROJECT, request, user_id)


@router.post("/search/social", response_model=SearchResponse)
async def search_social(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional)
) -> SearchResponse:
    """Search social media posts.
    
    Searches only within social post document type.
    """
    service = SearchService(db)
    user_id = UUID(current_user["sub"]) if current_user else None
    return await service.search_by_type(DocumentType.SOCIAL_POST, request, user_id)


@router.post("/search/notifications", response_model=SearchResponse)
async def search_notifications(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user_optional)
) -> SearchResponse:
    """Search notifications.
    
    Searches only within notification document type.
    """
    service = SearchService(db)
    user_id = UUID(current_user["sub"]) if current_user else None
    return await service.search_by_type(DocumentType.NOTIFICATION, request, user_id)
