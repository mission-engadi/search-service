"""Facet Service

Handles faceted search and filtering.
"""

from typing import Dict, List, Any, Optional
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.search_index import SearchIndex, DocumentType
from app.schemas.search import FacetRequest, FacetResponse, FacetOption


class FacetService:
    """Service for handling faceted search."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_facets(
        self,
        request: FacetRequest
    ) -> FacetResponse:
        """Get facets for a search query."""
        # Base query with search
        base_query = select(SearchIndex)
        
        # Apply search vector filter
        search_query = self._prepare_search_query(request.query)
        base_query = base_query.where(
            SearchIndex.search_vector.op('@@')(func.to_tsquery(search_query))
        )
        
        # Apply existing filters
        if request.filters:
            base_query = self._apply_filters(base_query, request.filters)
        
        # Get total count
        count_query = select(func.count()).select_from(base_query.subquery())
        total_results = (await self.db.execute(count_query)).scalar_one()
        
        # Generate facets for each field
        facets = {}
        
        for field in request.facet_fields:
            if field == "document_type":
                facets["document_type"] = await self._get_document_type_facets(base_query)
            elif field == "language":
                facets["language"] = await self._get_language_facets(base_query)
            elif field == "author_name":
                facets["author_name"] = await self._get_author_facets(base_query)
            elif field == "status":
                facets["status"] = await self._get_status_facets(base_query)
        
        return FacetResponse(
            query=request.query,
            facets=facets,
            total_results=total_results
        )
    
    async def get_filter_options(self, field: str) -> List[FacetOption]:
        """Get all available options for a filter field."""
        if field == "document_type":
            return await self._get_document_type_facets(select(SearchIndex))
        elif field == "language":
            return await self._get_language_facets(select(SearchIndex))
        elif field == "author_name":
            return await self._get_author_facets(select(SearchIndex))
        elif field == "status":
            return await self._get_status_facets(select(SearchIndex))
        else:
            return []
    
    async def count_results(
        self,
        query: str,
        facet_field: str,
        facet_value: Any
    ) -> int:
        """Count results for a specific facet value."""
        base_query = select(func.count(SearchIndex.id))
        
        # Apply search
        search_query = self._prepare_search_query(query)
        base_query = base_query.where(
            SearchIndex.search_vector.op('@@')(func.to_tsquery(search_query))
        )
        
        # Apply facet filter
        if facet_field == "document_type":
            base_query = base_query.where(SearchIndex.document_type == facet_value)
        elif facet_field == "language":
            base_query = base_query.where(SearchIndex.language == facet_value)
        elif facet_field == "author_name":
            base_query = base_query.where(SearchIndex.author_name == facet_value)
        elif facet_field == "status":
            base_query = base_query.where(SearchIndex.status == facet_value)
        
        result = await self.db.execute(base_query)
        return result.scalar_one()
    
    async def _get_document_type_facets(self, base_query) -> List[FacetOption]:
        """Get document type facets."""
        stmt = select(
            SearchIndex.document_type,
            func.count(SearchIndex.id).label('count')
        ).select_from(base_query.subquery()).group_by(SearchIndex.document_type)
        
        result = await self.db.execute(stmt)
        
        facets = []
        for row in result:
            facets.append(FacetOption(
                value=row[0].value,
                count=row[1],
                label=row[0].value.replace('_', ' ').title()
            ))
        
        return sorted(facets, key=lambda x: x.count, reverse=True)
    
    async def _get_language_facets(self, base_query) -> List[FacetOption]:
        """Get language facets."""
        stmt = select(
            SearchIndex.language,
            func.count(SearchIndex.id).label('count')
        ).select_from(base_query.subquery()).group_by(SearchIndex.language)
        
        result = await self.db.execute(stmt)
        
        # Map language codes to labels
        lang_labels = {
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            "pt": "Portuguese"
        }
        
        facets = []
        for row in result:
            facets.append(FacetOption(
                value=row[0],
                count=row[1],
                label=lang_labels.get(row[0], row[0].upper())
            ))
        
        return sorted(facets, key=lambda x: x.count, reverse=True)
    
    async def _get_author_facets(self, base_query) -> List[FacetOption]:
        """Get author facets."""
        stmt = select(
            SearchIndex.author_name,
            func.count(SearchIndex.id).label('count')
        ).select_from(base_query.subquery()).where(
            SearchIndex.author_name.isnot(None)
        ).group_by(SearchIndex.author_name)
        
        result = await self.db.execute(stmt)
        
        facets = []
        for row in result:
            if row[0]:  # Skip null authors
                facets.append(FacetOption(
                    value=row[0],
                    count=row[1],
                    label=row[0]
                ))
        
        return sorted(facets, key=lambda x: x.count, reverse=True)[:20]  # Top 20 authors
    
    async def _get_status_facets(self, base_query) -> List[FacetOption]:
        """Get status facets."""
        stmt = select(
            SearchIndex.status,
            func.count(SearchIndex.id).label('count')
        ).select_from(base_query.subquery()).where(
            SearchIndex.status.isnot(None)
        ).group_by(SearchIndex.status)
        
        result = await self.db.execute(stmt)
        
        facets = []
        for row in result:
            if row[0]:  # Skip null status
                facets.append(FacetOption(
                    value=row[0],
                    count=row[1],
                    label=row[0].replace('_', ' ').title()
                ))
        
        return sorted(facets, key=lambda x: x.count, reverse=True)
    
    def _prepare_search_query(self, query: str) -> str:
        """Prepare search query for PostgreSQL tsquery."""
        terms = query.strip().split()
        tsquery_terms = [f"{term}:*" for term in terms if term]
        return " & ".join(tsquery_terms) if tsquery_terms else "*"
    
    def _apply_filters(self, query, filters: Dict[str, Any]):
        """Apply filters to query."""
        filter_conditions = []
        
        if "document_type" in filters:
            filter_conditions.append(SearchIndex.document_type == filters["document_type"])
        
        if "language" in filters:
            filter_conditions.append(SearchIndex.language == filters["language"])
        
        if "author_id" in filters:
            filter_conditions.append(SearchIndex.author_id == filters["author_id"])
        
        if "status" in filters:
            filter_conditions.append(SearchIndex.status == filters["status"])
        
        if filter_conditions:
            query = query.where(and_(*filter_conditions))
        
        return query
