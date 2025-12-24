"""Autocomplete Service

Handles autocomplete and search suggestions.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import select, func, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.search_suggestion import SearchSuggestion
from app.models.search_query import SearchQuery


class AutoCompleteService:
    """Service for handling autocomplete and suggestions."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_suggestions(
        self,
        query: str,
        language: Optional[str] = None,
        limit: int = 10
    ) -> List[str]:
        """Get autocomplete suggestions using trigram similarity."""
        if not query or len(query) < 2:
            # For very short queries, return popular suggestions
            return await self.get_popular_searches(language, limit)
        
        # Use PostgreSQL similarity search
        stmt = select(SearchSuggestion.suggestion_text).where(
            SearchSuggestion.suggestion_text.op('%')(query)
        )
        
        if language:
            stmt = stmt.where(SearchSuggestion.language == language)
        
        # Order by similarity and usage count
        stmt = stmt.order_by(
            desc(func.similarity(SearchSuggestion.suggestion_text, query)),
            desc(SearchSuggestion.usage_count)
        ).limit(limit)
        
        result = await self.db.execute(stmt)
        suggestions = [row[0] for row in result]
        
        # If we don't have enough suggestions, try prefix matching
        if len(suggestions) < limit:
            prefix_stmt = select(SearchSuggestion.suggestion_text).where(
                SearchSuggestion.suggestion_text.ilike(f"{query}%")
            )
            
            if language:
                prefix_stmt = prefix_stmt.where(SearchSuggestion.language == language)
            
            prefix_stmt = prefix_stmt.order_by(
                desc(SearchSuggestion.usage_count)
            ).limit(limit - len(suggestions))
            
            prefix_result = await self.db.execute(prefix_stmt)
            prefix_suggestions = [row[0] for row in prefix_result]
            
            # Add unique suggestions
            for suggestion in prefix_suggestions:
                if suggestion not in suggestions:
                    suggestions.append(suggestion)
        
        return suggestions[:limit]
    
    async def get_popular_searches(
        self,
        language: Optional[str] = None,
        limit: int = 10
    ) -> List[str]:
        """Get popular search suggestions."""
        stmt = select(SearchSuggestion.suggestion_text)
        
        if language:
            stmt = stmt.where(SearchSuggestion.language == language)
        
        stmt = stmt.order_by(
            desc(SearchSuggestion.usage_count),
            desc(SearchSuggestion.last_used_at)
        ).limit(limit)
        
        result = await self.db.execute(stmt)
        return [row[0] for row in result]
    
    async def get_recent_searches(
        self,
        user_id: UUID,
        limit: int = 10
    ) -> List[str]:
        """Get recent searches for a user."""
        stmt = select(SearchQuery.query_text).where(
            SearchQuery.user_id == user_id
        ).order_by(
            desc(SearchQuery.created_at)
        ).distinct().limit(limit)
        
        result = await self.db.execute(stmt)
        return [row[0] for row in result]
    
    async def track_suggestion(self, suggestion_text: str, language: str = "en") -> None:
        """Track a suggestion usage."""
        # Check if suggestion exists
        stmt = select(SearchSuggestion).where(
            SearchSuggestion.suggestion_text == suggestion_text
        )
        result = await self.db.execute(stmt)
        suggestion = result.scalar_one_or_none()
        
        if suggestion:
            # Update existing suggestion
            suggestion.usage_count += 1
            suggestion.last_used_at = datetime.utcnow()
            suggestion.updated_at = datetime.utcnow()
        else:
            # Create new suggestion
            suggestion = SearchSuggestion(
                id=uuid4(),
                suggestion_text=suggestion_text,
                language=language,
                usage_count=1,
                last_used_at=datetime.utcnow()
            )
            self.db.add(suggestion)
        
        await self.db.commit()
    
    async def cleanup_suggestions(self, min_usage: int = 1) -> int:
        """Clean up suggestions with low usage."""
        from sqlalchemy import delete
        
        stmt = delete(SearchSuggestion).where(
            SearchSuggestion.usage_count < min_usage
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount
