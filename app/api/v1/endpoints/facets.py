"""Facets Endpoints

API endpoints for faceted search.
"""

from typing import List, Dict, Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user_optional
from app.schemas.search import FacetRequest, FacetResponse, FacetOption
from app.services.facet_service import FacetService

router = APIRouter()


@router.post("/facets", response_model=FacetResponse)
async def get_facets(
    request: FacetRequest,
    db: AsyncSession = Depends(get_db)
) -> FacetResponse:
    """Get facets for a search query.
    
    Returns available filters with counts for:
    - Document types
    - Languages
    - Authors
    - Status
    """
    service = FacetService(db)
    return await service.get_facets(request)


@router.get("/facets/options", response_model=List[FacetOption])
async def get_filter_options(
    field: str = Query(..., description="Field to get options for"),
    db: AsyncSession = Depends(get_db)
) -> List[FacetOption]:
    """Get all available options for a filter field.
    
    Supported fields:
    - document_type
    - language
    - author_name
    - status
    """
    service = FacetService(db)
    return await service.get_filter_options(field)


@router.post("/facets/count")
async def count_facet_results(
    query: str = Query(..., min_length=1),
    facet_field: str = Query(...),
    facet_value: str = Query(...),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Count results for a specific facet value.
    
    Returns the number of search results that match
    the query and the specific facet value.
    """
    service = FacetService(db)
    count = await service.count_results(query, facet_field, facet_value)
    
    return {
        "query": query,
        "facet_field": facet_field,
        "facet_value": facet_value,
        "count": count
    }
