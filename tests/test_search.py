"""Test search functionality."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.search_index import SearchIndex


class TestSearchEndpoints:
    """Test search API endpoints."""

    def test_search_basic(self, client: TestClient, sample_search_index: SearchIndex):
        """Test basic search functionality."""
        response = client.post(
            "/api/v1/search",
            json={
                "query": "sample",
                "page": 1,
                "page_size": 10
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total" in data
        assert "page" in data

    def test_search_with_filters(self, client: TestClient, sample_search_index: SearchIndex):
        """Test search with filters."""
        response = client.post(
            "/api/v1/search",
            json={
                "query": "sample",
                "filters": {
                    "document_type": "article",
                    "language": "en"
                },
                "page": 1,
                "page_size": 10
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data

    def test_search_empty_query(self, client: TestClient):
        """Test search with empty query."""
        response = client.post(
            "/api/v1/search",
            json={
                "query": "",
                "page": 1,
                "page_size": 10
            }
        )
        assert response.status_code == 200

    def test_search_pagination(self, client: TestClient, db: Session):
        """Test search pagination."""
        # Create multiple entries
        for i in range(15):
            entry = SearchIndex(
                document_id=i,
                document_type="article",
                title=f"Article {i}",
                content=f"Content {i} with search term",
                language="en"
            )
            db.add(entry)
        db.commit()

        response = client.post(
            "/api/v1/search",
            json={
                "query": "search",
                "page": 1,
                "page_size": 10
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) <= 10

    def test_search_sorting(self, client: TestClient, sample_search_index: SearchIndex):
        """Test search with sorting."""
        response = client.post(
            "/api/v1/search",
            json={
                "query": "sample",
                "sort_by": "created_at",
                "sort_order": "desc",
                "page": 1,
                "page_size": 10
            }
        )
        assert response.status_code == 200

    def test_search_by_content_type(self, client: TestClient, sample_search_index: SearchIndex):
        """Test search by content type."""
        response = client.post(
            "/api/v1/search/articles",
            json={
                "query": "sample",
                "page": 1,
                "page_size": 10
            }
        )
        assert response.status_code == 200

    def test_search_projects(self, client: TestClient, db: Session):
        """Test project search."""
        project = SearchIndex(
            document_id=1,
            document_type="project",
            title="Test Project",
            content="Project description",
            language="en"
        )
        db.add(project)
        db.commit()

        response = client.post(
            "/api/v1/search/projects",
            json={
                "query": "project",
                "page": 1,
                "page_size": 10
            }
        )
        assert response.status_code == 200

    def test_search_people(self, client: TestClient, db: Session):
        """Test people search."""
        person = SearchIndex(
            document_id=1,
            document_type="person",
            title="John Doe",
            content="Bio of John Doe",
            language="en"
        )
        db.add(person)
        db.commit()

        response = client.post(
            "/api/v1/search/people",
            json={
                "query": "john",
                "page": 1,
                "page_size": 10
            }
        )
        assert response.status_code == 200

    def test_search_invalid_page(self, client: TestClient):
        """Test search with invalid page number."""
        response = client.post(
            "/api/v1/search",
            json={
                "query": "test",
                "page": -1,
                "page_size": 10
            }
        )
        assert response.status_code == 422

    def test_search_invalid_page_size(self, client: TestClient):
        """Test search with invalid page size."""
        response = client.post(
            "/api/v1/search",
            json={
                "query": "test",
                "page": 1,
                "page_size": 1000
            }
        )
        assert response.status_code == 422
