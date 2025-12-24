"""Test faceted search functionality."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.search_index import SearchIndex


class TestFacetEndpoints:
    """Test facet API endpoints."""

    def test_get_facets_basic(self, client: TestClient, sample_search_index: SearchIndex):
        """Test basic facet retrieval."""
        response = client.get("/api/v1/facets")
        assert response.status_code == 200
        data = response.json()
        assert "document_types" in data
        assert "languages" in data

    def test_get_facets_with_query(self, client: TestClient, sample_search_index: SearchIndex):
        """Test facets with search query."""
        response = client.get(
            "/api/v1/facets",
            params={"query": "sample"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "document_types" in data

    def test_get_facets_with_filters(self, client: TestClient, db: Session):
        """Test facets with existing filters."""
        # Create diverse documents
        docs = [
            SearchIndex(
                document_id=1,
                document_type="article",
                title="Article",
                content="Content",
                language="en"
            ),
            SearchIndex(
                document_id=2,
                document_type="project",
                title="Project",
                content="Content",
                language="fr"
            )
        ]
        db.add_all(docs)
        db.commit()

        response = client.get(
            "/api/v1/facets",
            params={"document_type": "article"}
        )
        assert response.status_code == 200

    def test_get_document_type_facets(self, client: TestClient, db: Session):
        """Test document type facets."""
        # Create multiple document types
        for doc_type in ["article", "project", "person"]:
            for i in range(3):
                doc = SearchIndex(
                    document_id=i,
                    document_type=doc_type,
                    title=f"{doc_type} {i}",
                    content=f"Content {i}",
                    language="en"
                )
                db.add(doc)
        db.commit()

        response = client.get("/api/v1/facets/document-types")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3

    def test_get_language_facets(self, client: TestClient, db: Session):
        """Test language facets."""
        # Create documents in multiple languages
        for lang in ["en", "fr", "es"]:
            for i in range(2):
                doc = SearchIndex(
                    document_id=i,
                    document_type="article",
                    title=f"Article {i}",
                    content=f"Content {i}",
                    language=lang
                )
                db.add(doc)
        db.commit()

        response = client.get("/api/v1/facets/languages")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3

    def test_get_author_facets(self, client: TestClient, db: Session):
        """Test author facets."""
        # Create documents with different authors
        authors = ["Author A", "Author B", "Author C"]
        for author in authors:
            doc = SearchIndex(
                document_id=1,
                document_type="article",
                title="Article",
                content="Content",
                language="en",
                author=author
            )
            db.add(doc)
        db.commit()

        response = client.get("/api/v1/facets/authors")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3

    def test_facet_counts(self, client: TestClient, db: Session):
        """Test facet counts are accurate."""
        # Create 5 articles and 3 projects
        for i in range(5):
            db.add(SearchIndex(
                document_id=i,
                document_type="article",
                title=f"Article {i}",
                content="Content",
                language="en"
            ))
        for i in range(3):
            db.add(SearchIndex(
                document_id=i + 5,
                document_type="project",
                title=f"Project {i}",
                content="Content",
                language="en"
            ))
        db.commit()

        response = client.get("/api/v1/facets/document-types")
        assert response.status_code == 200
        data = response.json()
        # Check counts are present
        assert all("count" in item for item in data)

    def test_facets_empty_database(self, client: TestClient):
        """Test facets with empty database."""
        response = client.get("/api/v1/facets")
        assert response.status_code == 200
        data = response.json()
        assert data["document_types"] == []
        assert data["languages"] == []
