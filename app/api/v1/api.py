"""API router configuration.

This module aggregates all API routers for version 1.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    health,
    search,
    autocomplete,
    indexing,
    analytics,
    management,
    facets,
)

api_router = APIRouter()

# Health check
api_router.include_router(
    health.router,
    tags=["health"],
)

# Search endpoints (6 endpoints)
api_router.include_router(
    search.router,
    tags=["search"],
)

# Autocomplete endpoints (3 endpoints)
api_router.include_router(
    autocomplete.router,
    tags=["autocomplete"],
)

# Indexing endpoints (5 endpoints)
api_router.include_router(
    indexing.router,
    tags=["indexing"],
)

# Analytics endpoints (4 endpoints)
api_router.include_router(
    analytics.router,
    tags=["analytics"],
)

# Management endpoints (4 endpoints)
api_router.include_router(
    management.router,
    tags=["management"],
)

# Facets endpoints (3 endpoints)
api_router.include_router(
    facets.router,
    tags=["facets"],
)
