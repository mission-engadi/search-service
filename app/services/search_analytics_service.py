"""Search Analytics Service

Tracks and analyzes search queries and user behavior.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from uuid import UUID, uuid4

from sqlalchemy import select, func, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.search_query import SearchQuery
from app.models.search_suggestion import SearchSuggestion


class SearchAnalyticsService:
    """Service for tracking and analyzing search behavior."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def track_search(
        self,
        query_text: str,
        language: Optional[str],
        filters: Dict[str, Any],
        results_count: int,
        user_id: Optional[UUID],
        execution_time: float
    ) -> SearchQuery:
        """Track a search query."""
        search_query = SearchQuery(
            id=uuid4(),
            query_text=query_text,
            language=language,
            filters=filters,
            results_count=results_count,
            user_id=user_id,
            execution_time=execution_time
        )
        
        self.db.add(search_query)
        await self.db.commit()
        await self.db.refresh(search_query)
        
        # Also update suggestions
        await self._update_suggestion(query_text, language or "en")
        
        return search_query
    
    async def track_click(
        self,
        query_id: UUID,
        clicked_result_id: UUID
    ) -> bool:
        """Track when a user clicks on a search result."""
        stmt = select(SearchQuery).where(SearchQuery.id == query_id)
        result = await self.db.execute(stmt)
        query = result.scalar_one_or_none()
        
        if query:
            query.clicked_result_id = clicked_result_id
            await self.db.commit()
            return True
        
        return False
    
    async def get_popular_queries(
        self,
        limit: int = 20,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get most popular search queries."""
        since = datetime.utcnow() - timedelta(days=days)
        
        stmt = select(
            SearchQuery.query_text,
            func.count(SearchQuery.id).label('count'),
            func.avg(SearchQuery.results_count).label('avg_results')
        ).where(
            SearchQuery.created_at >= since
        ).group_by(
            SearchQuery.query_text
        ).order_by(
            desc('count')
        ).limit(limit)
        
        result = await self.db.execute(stmt)
        
        return [
            {
                "query": row[0],
                "count": row[1],
                "avg_results": int(row[2]) if row[2] else 0
            }
            for row in result
        ]
    
    async def get_zero_result_queries(
        self,
        limit: int = 20,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get queries that returned no results."""
        since = datetime.utcnow() - timedelta(days=days)
        
        stmt = select(
            SearchQuery.query_text,
            func.count(SearchQuery.id).label('count')
        ).where(
            and_(
                SearchQuery.created_at >= since,
                SearchQuery.results_count == 0
            )
        ).group_by(
            SearchQuery.query_text
        ).order_by(
            desc('count')
        ).limit(limit)
        
        result = await self.db.execute(stmt)
        
        return [
            {"query": row[0], "count": row[1]}
            for row in result
        ]
    
    async def get_search_stats(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get overall search statistics."""
        since = datetime.utcnow() - timedelta(days=days)
        
        # Total searches
        total_stmt = select(func.count(SearchQuery.id)).where(
            SearchQuery.created_at >= since
        )
        total_searches = (await self.db.execute(total_stmt)).scalar_one()
        
        # Unique queries
        unique_stmt = select(func.count(func.distinct(SearchQuery.query_text))).where(
            SearchQuery.created_at >= since
        )
        unique_queries = (await self.db.execute(unique_stmt)).scalar_one()
        
        # Average results
        avg_stmt = select(func.avg(SearchQuery.results_count)).where(
            SearchQuery.created_at >= since
        )
        avg_results = (await self.db.execute(avg_stmt)).scalar_one() or 0
        
        # Average execution time
        avg_time_stmt = select(func.avg(SearchQuery.execution_time)).where(
            and_(
                SearchQuery.created_at >= since,
                SearchQuery.execution_time.isnot(None)
            )
        )
        avg_execution_time = (await self.db.execute(avg_time_stmt)).scalar_one() or 0
        
        # Zero result rate
        zero_stmt = select(func.count(SearchQuery.id)).where(
            and_(
                SearchQuery.created_at >= since,
                SearchQuery.results_count == 0
            )
        )
        zero_results = (await self.db.execute(zero_stmt)).scalar_one()
        zero_result_rate = (zero_results / total_searches * 100) if total_searches > 0 else 0
        
        return {
            "total_searches": total_searches,
            "unique_queries": unique_queries,
            "avg_results": float(avg_results),
            "avg_execution_time_ms": float(avg_execution_time),
            "zero_result_rate": float(zero_result_rate),
            "period_days": days
        }
    
    async def get_performance_metrics(
        self,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """Get performance metrics over time."""
        since = datetime.utcnow() - timedelta(days=days)
        
        stmt = select(
            func.date_trunc('day', SearchQuery.created_at).label('date'),
            func.count(SearchQuery.id).label('count'),
            func.avg(SearchQuery.execution_time).label('avg_time'),
            func.avg(SearchQuery.results_count).label('avg_results')
        ).where(
            SearchQuery.created_at >= since
        ).group_by(
            'date'
        ).order_by(
            'date'
        )
        
        result = await self.db.execute(stmt)
        
        return [
            {
                "date": row[0].strftime('%Y-%m-%d') if row[0] else None,
                "count": row[1],
                "avg_execution_time_ms": float(row[2]) if row[2] else 0,
                "avg_results": float(row[3]) if row[3] else 0
            }
            for row in result
        ]
    
    async def get_user_search_history(
        self,
        user_id: UUID,
        limit: int = 50
    ) -> List[SearchQuery]:
        """Get search history for a specific user."""
        stmt = select(SearchQuery).where(
            SearchQuery.user_id == user_id
        ).order_by(
            desc(SearchQuery.created_at)
        ).limit(limit)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def _update_suggestion(
        self,
        query_text: str,
        language: str
    ) -> None:
        """Update or create a search suggestion."""
        # Only track queries that are long enough and don't contain special characters
        if len(query_text) < 3 or not query_text.replace(' ', '').isalnum():
            return
        
        stmt = select(SearchSuggestion).where(
            SearchSuggestion.suggestion_text == query_text
        )
        result = await self.db.execute(stmt)
        suggestion = result.scalar_one_or_none()
        
        if suggestion:
            suggestion.usage_count += 1
            suggestion.last_used_at = datetime.utcnow()
            suggestion.updated_at = datetime.utcnow()
        else:
            suggestion = SearchSuggestion(
                id=uuid4(),
                suggestion_text=query_text,
                language=language,
                usage_count=1,
                last_used_at=datetime.utcnow()
            )
            self.db.add(suggestion)
        
        await self.db.commit()
