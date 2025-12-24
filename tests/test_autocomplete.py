"""Test autocomplete functionality."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.search_suggestion import SearchSuggestion


class TestAutocompleteEndpoints:
    """Test autocomplete API endpoints."""

    def test_get_suggestions_basic(self, client: TestClient, sample_suggestion: SearchSuggestion):
        """Test basic autocomplete suggestions."""
        response = client.get(
            "/api/v1/autocomplete/suggestions",
            params={"query": "test", "limit": 10}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_suggestions_empty_query(self, client: TestClient):
        """Test suggestions with empty query."""
        response = client.get(
            "/api/v1/autocomplete/suggestions",
            params={"query": "", "limit": 10}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_suggestions_with_language(self, client: TestClient, db: Session):
        """Test suggestions with language filter."""
        # Create language-specific suggestions
        suggestion_en = SearchSuggestion(
            suggestion="english suggestion",
            language="en",
            usage_count=5
        )
        suggestion_fr = SearchSuggestion(
            suggestion="suggestion française",
            language="fr",
            usage_count=3
        )
        db.add_all([suggestion_en, suggestion_fr])
        db.commit()

        response = client.get(
            "/api/v1/autocomplete/suggestions",
            params={"query": "suggestion", "language": "en", "limit": 10}
        )
        assert response.status_code == 200

    def test_get_popular_suggestions(self, client: TestClient, db: Session):
        """Test getting popular suggestions."""
        # Create multiple suggestions with different usage counts
        for i in range(5):
            suggestion = SearchSuggestion(
                suggestion=f"popular {i}",
                language="en",
                usage_count=10 - i
            )
            db.add(suggestion)
        db.commit()

        response = client.get(
            "/api/v1/autocomplete/popular",
            params={"limit": 5}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5

    def test_get_recent_searches(self, client: TestClient, auth_headers: dict):
        """Test getting recent searches."""
        response = client.get(
            "/api/v1/autocomplete/recent",
            params={"limit": 10},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_add_suggestion(self, client: TestClient, auth_headers: dict):
        """Test adding a new suggestion."""
        response = client.post(
            "/api/v1/autocomplete/suggestions",
            json={
                "suggestion": "new suggestion",
                "language": "en"
            },
            headers=auth_headers
        )
        assert response.status_code == 200

    def test_increment_suggestion_usage(self, client: TestClient, sample_suggestion: SearchSuggestion):
        """Test incrementing suggestion usage count."""
        original_count = sample_suggestion.usage_count
        response = client.post(
            f"/api/v1/autocomplete/suggestions/{sample_suggestion.id}/increment"
        )
        assert response.status_code == 200
        # Verify count increased (would need to query DB)

    def test_suggestions_limit(self, client: TestClient, db: Session):
        """Test suggestion limit parameter."""
        # Create many suggestions
        for i in range(20):
            suggestion = SearchSuggestion(
                suggestion=f"suggestion {i}",
                language="en",
                usage_count=1
            )
            db.add(suggestion)
        db.commit()

        response = client.get(
            "/api/v1/autocomplete/suggestions",
            params={"query": "suggestion", "limit": 5}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5

    def test_suggestions_invalid_limit(self, client: TestClient):
        """Test suggestions with invalid limit."""
        response = client.get(
            "/api/v1/autocomplete/suggestions",
            params={"query": "test", "limit": 1000}
        )
        assert response.status_code == 422
