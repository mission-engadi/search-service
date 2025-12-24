"""Test configuration and fixtures."""
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.search_index import SearchIndex
from app.models.search_query import SearchQuery
from app.models.search_suggestion import SearchSuggestion
from app.models.index_job import IndexJob

# Test database URL
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database override."""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_search_index(db: Session) -> SearchIndex:
    """Create sample search index entry."""
    index_entry = SearchIndex(
        document_id=1,
        document_type="article",
        title="Sample Article",
        content="This is sample content for testing search functionality.",
        language="en",
        author="Test Author",
        status="published",
        metadata={"tags": ["test", "sample"]}
    )
    db.add(index_entry)
    db.commit()
    db.refresh(index_entry)
    return index_entry


@pytest.fixture
def sample_search_query(db: Session) -> SearchQuery:
    """Create sample search query."""
    query = SearchQuery(
        query_text="test query",
        filters={"document_type": "article"},
        results_count=5,
        response_time=0.123,
        user_id=1
    )
    db.add(query)
    db.commit()
    db.refresh(query)
    return query


@pytest.fixture
def sample_suggestion(db: Session) -> SearchSuggestion:
    """Create sample search suggestion."""
    suggestion = SearchSuggestion(
        suggestion="test suggestion",
        language="en",
        usage_count=10
    )
    db.add(suggestion)
    db.commit()
    db.refresh(suggestion)
    return suggestion


@pytest.fixture
def sample_index_job(db: Session) -> IndexJob:
    """Create sample index job."""
    job = IndexJob(
        job_type="full_reindex",
        status="completed",
        total_documents=100,
        processed_documents=100,
        failed_documents=0
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@pytest.fixture
def auth_headers() -> dict:
    """Mock authentication headers."""
    return {
        "Authorization": "Bearer mock_token",
        "X-User-ID": "1"
    }
