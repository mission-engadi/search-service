"""Search Service

Core search functionality using PostgreSQL full-text search.
"""

import time
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, func, and_, or_, desc, asc, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.search_index import SearchIndex, DocumentType
from app.schemas.search import SearchRequest, SearchResponse, SearchResult
from app.services.search_analytics_service import SearchAnalyticsService


class SearchService:
    """Service for handling search operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.analytics_service = SearchAnalyticsService(db)
    
    async def search(
        self,
        request: SearchRequest,
        user_id: Optional[UUID] = None
    ) -> SearchResponse:
        """Universal search across all content types."""
        start_time = time.time()
        
        # Build the base query
        query = select(SearchIndex)
        
        # Apply search vector filter
        search_query = self._prepare_search_query(request.query, request.language or "english")
        query = query.where(
            SearchIndex.search_vector.op('@@')(func.to_tsquery(search_query))
        )
        
        # Apply filters
        query = self._apply_filters(query, request)
        
        # Count total results
        count_query = select(func.count()).select_from(query.subquery())
        total_count = (await self.db.execute(count_query)).scalar_one()
        
        # Apply sorting
        query = self._apply_sorting(query, request, search_query)
        
        # Apply pagination
        offset = (request.page - 1) * request.page_size
        query = query.offset(offset).limit(request.page_size)
        
        # Execute query
        result = await self.db.execute(query)
        search_indexes = result.scalars().all()
        
        # Convert to search results with highlighting
        results = [
            self._to_search_result(index, request.query, request.highlight)
            for index in search_indexes
        ]
        
        execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Track analytics
        await self.analytics_service.track_search(
            query_text=request.query,
            language=request.language,
            filters=self._get_filters_dict(request),
            results_count=total_count,
            user_id=user_id,
            execution_time=execution_time
        )
        
        total_pages = (total_count + request.page_size - 1) // request.page_size
        
        return SearchResponse(
            query=request.query,
            results=results,
            total_count=total_count,
            page=request.page,
            page_size=request.page_size,
            total_pages=total_pages,
            execution_time=execution_time
        )
    
    async def search_by_type(
        self,
        document_type: DocumentType,
        request: SearchRequest,
        user_id: Optional[UUID] = None
    ) -> SearchResponse:
        """Search within specific document type."""
        # Override document_types filter
        request.document_types = [document_type]
        return await self.search(request, user_id)
    
    def _prepare_search_query(self, query: str, language: str = "english") -> str:
        """Prepare search query for PostgreSQL tsquery."""
        # Map language codes to PostgreSQL text search configurations
        lang_map = {
            "en": "english",
            "es": "spanish",
            "fr": "french",
            "pt": "portuguese"
        }
        
        # Clean and prepare query
        terms = query.strip().split()
        # Add prefix matching for each term
        tsquery_terms = [f"{term}:*" for term in terms if term]
        return " & ".join(tsquery_terms) if tsquery_terms else "*"
    
    def _apply_filters(
        self,
        query,
        request: SearchRequest
    ):
        """Apply filters to search query."""
        filters = []
        
        # Document type filter
        if request.document_types:
            filters.append(SearchIndex.document_type.in_(request.document_types))
        
        # Language filter
        if request.language:
            filters.append(SearchIndex.language == request.language)
        
        # Author filter
        if request.author_id:
            filters.append(SearchIndex.author_id == request.author_id)
        
        # Status filter
        if request.status:
            filters.append(SearchIndex.status == request.status)
        
        # Date range filters
        if request.date_from:
            try:
                date_from = datetime.fromisoformat(request.date_from)
                filters.append(SearchIndex.published_at >= date_from)
            except ValueError:
                pass
        
        if request.date_to:
            try:
                date_to = datetime.fromisoformat(request.date_to)
                filters.append(SearchIndex.published_at <= date_to)
            except ValueError:
                pass
        
        # Metadata filters
        if request.metadata_filters:
            for key, value in request.metadata_filters.items():
                filters.append(
                    SearchIndex.metadata[key].astext == str(value)
                )
        
        if filters:
            query = query.where(and_(*filters))
        
        return query
    
    def _apply_sorting(
        self,
        query,
        request: SearchRequest,
        search_query: str
    ):
        """Apply sorting to search query."""
        if request.sort_by == "relevance":
            # Sort by relevance score
            rank = func.ts_rank(
                SearchIndex.search_vector,
                func.to_tsquery(search_query)
            )
            if request.sort_order == "desc":
                query = query.order_by(desc(rank))
            else:
                query = query.order_by(asc(rank))
        elif request.sort_by == "date":
            if request.sort_order == "desc":
                query = query.order_by(desc(SearchIndex.published_at))
            else:
                query = query.order_by(asc(SearchIndex.published_at))
        elif request.sort_by == "title":
            if request.sort_order == "desc":
                query = query.order_by(desc(SearchIndex.title))
            else:
                query = query.order_by(asc(SearchIndex.title))
        else:
            # Default to indexed_at desc
            query = query.order_by(desc(SearchIndex.indexed_at))
        
        return query
    
    def _to_search_result(
        self,
        index: SearchIndex,
        query: str,
        highlight: bool = True
    ) -> SearchResult:
        """Convert SearchIndex to SearchResult with highlighting."""
        # Create content snippet (first 200 chars)
        content_snippet = index.content[:200] + "..." if len(index.content) > 200 else index.content
        
        result = SearchResult(
            id=index.id,
            document_id=index.document_id,
            document_type=index.document_type,
            title=index.title,
            content_snippet=content_snippet,
            language=index.language,
            metadata=index.metadata or {},
            author_name=index.author_name,
            published_at=index.published_at,
        )
        
        # Add highlighting if requested
        if highlight:
            result.highlighted_title = self._highlight_text(index.title, query)
            result.highlighted_content = self._highlight_text(content_snippet, query)
        
        return result
    
    def _highlight_text(self, text: str, query: str) -> str:
        """Highlight search terms in text."""
        terms = query.lower().split()
        highlighted = text
        
        for term in terms:
            if term:
                # Simple case-insensitive highlighting
                import re
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                highlighted = pattern.sub(f"<mark>{term}</mark>", highlighted)
        
        return highlighted
    
    def _get_filters_dict(self, request: SearchRequest) -> Dict[str, Any]:
        """Convert request filters to dict for analytics."""
        filters = {}
        
        if request.document_types:
            filters["document_types"] = [dt.value for dt in request.document_types]
        if request.language:
            filters["language"] = request.language
        if request.author_id:
            filters["author_id"] = str(request.author_id)
        if request.status:
            filters["status"] = request.status
        if request.date_from:
            filters["date_from"] = request.date_from
        if request.date_to:
            filters["date_to"] = request.date_to
        if request.metadata_filters:
            filters["metadata"] = request.metadata_filters
        
        return filters
