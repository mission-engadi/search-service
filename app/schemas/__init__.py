"""Pydantic schemas."""

from app.schemas.search_index import (
    SearchIndexBase,
    SearchIndexCreate,
    SearchIndexUpdate,
    SearchIndexResponse,
    SearchResult,
)
from app.schemas.search_query import (
    SearchQueryBase,
    SearchQueryCreate,
    SearchQueryResponse,
)
from app.schemas.search_suggestion import (
    SearchSuggestionBase,
    SearchSuggestionCreate,
    SearchSuggestionResponse,
)
from app.schemas.index_job import (
    IndexJobBase,
    IndexJobCreate,
    IndexJobUpdate,
    IndexJobResponse,
)
from app.schemas.search import (
    SearchRequest,
    SearchResponse,
    AutoCompleteRequest,
    AutoCompleteResponse,
    FacetRequest,
    FacetOption,
    FacetResponse,
    IndexDocumentRequest,
    BulkIndexRequest,
    IndexResponse,
    BulkIndexResponse,
)

__all__ = [
    # SearchIndex schemas
    "SearchIndexBase",
    "SearchIndexCreate",
    "SearchIndexUpdate",
    "SearchIndexResponse",
    "SearchResult",
    # SearchQuery schemas
    "SearchQueryBase",
    "SearchQueryCreate",
    "SearchQueryResponse",
    # SearchSuggestion schemas
    "SearchSuggestionBase",
    "SearchSuggestionCreate",
    "SearchSuggestionResponse",
    # IndexJob schemas
    "IndexJobBase",
    "IndexJobCreate",
    "IndexJobUpdate",
    "IndexJobResponse",
    # Search request/response schemas
    "SearchRequest",
    "SearchResponse",
    "AutoCompleteRequest",
    "AutoCompleteResponse",
    "FacetRequest",
    "FacetOption",
    "FacetResponse",
    "IndexDocumentRequest",
    "BulkIndexRequest",
    "IndexResponse",
    "BulkIndexResponse",
]
