"""Test indexing functionality."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.search_index import SearchIndex
from app.models.index_job import IndexJob


class TestIndexingEndpoints:
    """Test indexing API endpoints."""

    def test_index_document(self, client: TestClient, auth_headers: dict):
        """Test indexing a single document."""
        response = client.post(
            "/api/v1/indexing/index",
            json={
                "document_id": 1,
                "document_type": "article",
                "title": "Test Article",
                "content": "Test content",
                "language": "en"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["document_id"] == 1

    def test_bulk_index(self, client: TestClient, auth_headers: dict):
        """Test bulk indexing."""
        response = client.post(
            "/api/v1/indexing/bulk",
            json={
                "documents": [
                    {
                        "document_id": 1,
                        "document_type": "article",
                        "title": "Article 1",
                        "content": "Content 1",
                        "language": "en"
                    },
                    {
                        "document_id": 2,
                        "document_type": "article",
                        "title": "Article 2",
                        "content": "Content 2",
                        "language": "en"
                    }
                ]
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["indexed"] == 2

    def test_update_document(self, client: TestClient, db: Session, auth_headers: dict):
        """Test updating an indexed document."""
        # Create initial document
        doc = SearchIndex(
            document_id=1,
            document_type="article",
            title="Original Title",
            content="Original content",
            language="en"
        )
        db.add(doc)
        db.commit()

        # Update document
        response = client.put(
            "/api/v1/indexing/update/1",
            json={
                "title": "Updated Title",
                "content": "Updated content"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"

    def test_delete_document(self, client: TestClient, sample_search_index: SearchIndex, auth_headers: dict):
        """Test deleting an indexed document."""
        doc_id = sample_search_index.document_id
        response = client.delete(
            f"/api/v1/indexing/delete/{doc_id}",
            headers=auth_headers
        )
        assert response.status_code == 200

    def test_reindex_service(self, client: TestClient, auth_headers: dict):
        """Test reindexing a service."""
        response = client.post(
            "/api/v1/indexing/reindex/content",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data

    def test_get_index_stats(self, client: TestClient, sample_search_index: SearchIndex):
        """Test getting index statistics."""
        response = client.get("/api/v1/indexing/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_documents" in data

    def test_get_job_status(self, client: TestClient, sample_index_job: IndexJob):
        """Test getting job status."""
        job_id = sample_index_job.id
        response = client.get(f"/api/v1/indexing/jobs/{job_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == job_id

    def test_list_jobs(self, client: TestClient, sample_index_job: IndexJob):
        """Test listing index jobs."""
        response = client.get("/api/v1/indexing/jobs")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

    def test_index_document_duplicate(self, client: TestClient, sample_search_index: SearchIndex, auth_headers: dict):
        """Test indexing duplicate document."""
        response = client.post(
            "/api/v1/indexing/index",
            json={
                "document_id": sample_search_index.document_id,
                "document_type": sample_search_index.document_type,
                "title": "Updated Title",
                "content": "Updated content",
                "language": "en"
            },
            headers=auth_headers
        )
        # Should update existing document
        assert response.status_code == 200

    def test_index_missing_fields(self, client: TestClient, auth_headers: dict):
        """Test indexing with missing required fields."""
        response = client.post(
            "/api/v1/indexing/index",
            json={
                "document_id": 1,
                "document_type": "article"
                # Missing title and content
            },
            headers=auth_headers
        )
        assert response.status_code == 422
