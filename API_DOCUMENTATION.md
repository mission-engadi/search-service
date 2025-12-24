# Search Service - API Documentation

**Base URL:** `http://localhost:8011/api/v1`  
**Version:** 1.0.0

## Table of Contents

1. [Search Endpoints](#search-endpoints)
2. [Indexing Endpoints](#indexing-endpoints)
3. [Autocomplete Endpoints](#autocomplete-endpoints)
4. [Facet Endpoints](#facet-endpoints)
5. [Analytics Endpoints](#analytics-endpoints)
6. [Common Models](#common-models)

---

## Search Endpoints

### 1. Universal Search

**Endpoint:** `POST /api/v1/search`  
**Description:** Search across all content types  
**Authentication:** Optional

**Request Body:**
```json
{
  "query": "mission africa",
  "filters": {
    "document_type": "article",
    "language": "en",
    "author": "John Doe",
    "status": "published"
  },
  "sort_by": "relevance",
  "sort_order": "desc",
  "page": 1,
  "page_size": 10
}
```

**Response:**
```json
{
  "results": [
    {
      "id": 1,
      "document_id": 123,
      "document_type": "article",
      "title": "Mission Work in Africa",
      "content_preview": "...mission <mark>africa</mark>...",
      "language": "en",
      "author": "John Doe",
      "created_at": "2024-12-01T10:00:00Z",
      "relevance_score": 0.95
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 10,
  "total_pages": 5
}
```

### 2. Search Articles

**Endpoint:** `POST /api/v1/search/articles`  
**Description:** Search specifically for articles  
**Authentication:** Optional

**Request Body:**
```json
{
  "query": "evangelism",
  "page": 1,
  "page_size": 10
}
```

### 3. Search Projects

**Endpoint:** `POST /api/v1/search/projects`  
**Description:** Search for projects  
**Authentication:** Optional

### 4. Search People

**Endpoint:** `POST /api/v1/search/people`  
**Description:** Search for people/missionaries  
**Authentication:** Optional

### 5. Search Partners

**Endpoint:** `POST /api/v1/search/partners`  
**Description:** Search for partner organizations  
**Authentication:** Optional

### 6. Advanced Search

**Endpoint:** `POST /api/v1/search/advanced`  
**Description:** Advanced search with complex filters  
**Authentication:** Optional

**Request Body:**
```json
{
  "query": "missions",
  "filters": {
    "document_types": ["article", "project"],
    "languages": ["en", "fr"],
    "date_range": {
      "start": "2024-01-01",
      "end": "2024-12-31"
    },
    "tags": ["evangelism", "training"]
  },
  "boost": {
    "title": 2.0,
    "content": 1.0
  }
}
```

---

## Indexing Endpoints

### 7. Index Single Document

**Endpoint:** `POST /api/v1/indexing/index`  
**Description:** Index a single document  
**Authentication:** Required

**Request Body:**
```json
{
  "document_id": 123,
  "document_type": "article",
  "title": "Understanding Missions",
  "content": "Full article content...",
  "language": "en",
  "author": "Jane Smith",
  "status": "published",
  "metadata": {
    "tags": ["missions", "training"],
    "category": "Education"
  }
}
```

**Response:**
```json
{
  "id": 1,
  "document_id": 123,
  "document_type": "article",
  "title": "Understanding Missions",
  "indexed_at": "2024-12-25T10:00:00Z"
}
```

### 8. Bulk Index

**Endpoint:** `POST /api/v1/indexing/bulk`  
**Description:** Index multiple documents at once  
**Authentication:** Required

**Request Body:**
```json
{
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
      "language": "fr"
    }
  ]
}
```

**Response:**
```json
{
  "job_id": 42,
  "indexed": 2,
  "failed": 0,
  "errors": []
}
```

### 9. Update Document

**Endpoint:** `PUT /api/v1/indexing/update/{document_id}`  
**Description:** Update an indexed document  
**Authentication:** Required

**Request Body:**
```json
{
  "title": "Updated Title",
  "content": "Updated content",
  "status": "published"
}
```

### 10. Delete Document

**Endpoint:** `DELETE /api/v1/indexing/delete/{document_id}`  
**Description:** Remove document from index  
**Authentication:** Required

**Response:**
```json
{
  "message": "Document deleted successfully",
  "document_id": 123
}
```

### 11. Reindex Service

**Endpoint:** `POST /api/v1/indexing/reindex/{service}`  
**Description:** Trigger reindexing from external service  
**Authentication:** Required  
**Services:** `content`, `partners`, `projects`, `social_media`

**Response:**
```json
{
  "job_id": 42,
  "service": "content",
  "status": "started",
  "estimated_documents": 1000
}
```

### 12. Get Index Statistics

**Endpoint:** `GET /api/v1/indexing/stats`  
**Description:** Get indexing statistics

**Response:**
```json
{
  "total_documents": 5420,
  "by_type": {
    "article": 3200,
    "project": 1500,
    "person": 500,
    "partner": 220
  },
  "by_language": {
    "en": 3000,
    "fr": 1500,
    "es": 920
  },
  "last_indexed": "2024-12-25T09:30:00Z",
  "index_size": "2.3 GB"
}
```

### 13. List Index Jobs

**Endpoint:** `GET /api/v1/indexing/jobs`  
**Description:** List all index jobs

**Query Parameters:**
- `status` (optional): Filter by status
- `limit` (optional): Limit results (default: 50)

**Response:**
```json
[
  {
    "id": 42,
    "job_type": "full_reindex",
    "status": "completed",
    "total_documents": 1000,
    "processed_documents": 1000,
    "failed_documents": 0,
    "started_at": "2024-12-25T08:00:00Z",
    "completed_at": "2024-12-25T08:15:00Z"
  }
]
```

### 14. Get Job Status

**Endpoint:** `GET /api/v1/indexing/jobs/{job_id}`  
**Description:** Get detailed job status

**Response:**
```json
{
  "id": 42,
  "job_type": "full_reindex",
  "status": "in_progress",
  "total_documents": 1000,
  "processed_documents": 650,
  "failed_documents": 2,
  "progress_percentage": 65.0,
  "errors": [
    {"document_id": 123, "error": "Invalid format"}
  ],
  "started_at": "2024-12-25T08:00:00Z",
  "estimated_completion": "2024-12-25T08:20:00Z"
}
```

---

## Autocomplete Endpoints

### 15. Get Suggestions

**Endpoint:** `GET /api/v1/autocomplete/suggestions`  
**Description:** Get autocomplete suggestions

**Query Parameters:**
- `query` (required): Search query prefix
- `language` (optional): Filter by language
- `limit` (optional): Max suggestions (default: 10)

**Response:**
```json
[
  {
    "suggestion": "missions in africa",
    "usage_count": 45,
    "language": "en"
  },
  {
    "suggestion": "missionary training",
    "usage_count": 32,
    "language": "en"
  }
]
```

### 16. Get Popular Searches

**Endpoint:** `GET /api/v1/autocomplete/popular`  
**Description:** Get most popular searches

**Query Parameters:**
- `language` (optional): Filter by language
- `limit` (optional): Max results (default: 10)

**Response:**
```json
[
  {
    "query": "missions",
    "count": 1250,
    "language": "en"
  },
  {
    "query": "evangelism",
    "count": 980,
    "language": "en"
  }
]
```

### 17. Get Recent Searches

**Endpoint:** `GET /api/v1/autocomplete/recent`  
**Description:** Get user's recent searches  
**Authentication:** Required

**Query Parameters:**
- `limit` (optional): Max results (default: 10)

**Response:**
```json
[
  {
    "query": "bible translation",
    "searched_at": "2024-12-25T09:45:00Z"
  },
  {
    "query": "church planting",
    "searched_at": "2024-12-25T09:30:00Z"
  }
]
```

### 18. Add Suggestion

**Endpoint:** `POST /api/v1/autocomplete/suggestions`  
**Description:** Add a new suggestion  
**Authentication:** Required

**Request Body:**
```json
{
  "suggestion": "new search term",
  "language": "en"
}
```

---

## Facet Endpoints

### 19. Get All Facets

**Endpoint:** `GET /api/v1/facets`  
**Description:** Get all available facets with counts

**Query Parameters:**
- `query` (optional): Filter facets by search query
- Various filter parameters

**Response:**
```json
{
  "document_types": [
    {"type": "article", "count": 3200},
    {"type": "project", "count": 1500},
    {"type": "person", "count": 500}
  ],
  "languages": [
    {"language": "en", "count": 3000},
    {"language": "fr", "count": 1500},
    {"language": "es", "count": 920}
  ],
  "authors": [
    {"author": "John Doe", "count": 245},
    {"author": "Jane Smith", "count": 189}
  ],
  "statuses": [
    {"status": "published", "count": 4800},
    {"status": "draft", "count": 620}
  ]
}
```

### 20. Get Document Type Facets

**Endpoint:** `GET /api/v1/facets/document-types`  
**Description:** Get document type facets

**Response:**
```json
[
  {"type": "article", "count": 3200},
  {"type": "project", "count": 1500},
  {"type": "person", "count": 500},
  {"type": "partner", "count": 220}
]
```

### 21. Get Language Facets

**Endpoint:** `GET /api/v1/facets/languages`  
**Description:** Get language facets

**Response:**
```json
[
  {"language": "en", "name": "English", "count": 3000},
  {"language": "fr", "name": "French", "count": 1500},
  {"language": "es", "name": "Spanish", "count": 920}
]
```

### 22. Get Author Facets

**Endpoint:** `GET /api/v1/facets/authors`  
**Description:** Get author facets

**Response:**
```json
[
  {"author": "John Doe", "count": 245},
  {"author": "Jane Smith", "count": 189},
  {"author": "Bob Johnson", "count": 156}
]
```

---

## Analytics Endpoints

### 23. Get Popular Queries

**Endpoint:** `GET /api/v1/analytics/popular-queries`  
**Description:** Get most popular search queries

**Query Parameters:**
- `days` (optional): Time period (default: 30)
- `limit` (optional): Max results (default: 20)

**Response:**
```json
[
  {
    "query": "missions",
    "count": 1250,
    "avg_results": 42,
    "avg_response_time": 0.085
  },
  {
    "query": "evangelism",
    "count": 980,
    "avg_results": 35,
    "avg_response_time": 0.092
  }
]
```

### 24. Get Zero-Result Queries

**Endpoint:** `GET /api/v1/analytics/zero-results`  
**Description:** Get queries that returned no results

**Query Parameters:**
- `days` (optional): Time period (default: 30)
- `limit` (optional): Max results (default: 20)

**Response:**
```json
[
  {
    "query": "obscure search term",
    "count": 15,
    "last_searched": "2024-12-25T09:00:00Z"
  }
]
```

### 25. Get Search Metrics

**Endpoint:** `GET /api/v1/analytics/metrics`  
**Description:** Get overall search metrics

**Query Parameters:**
- `days` (optional): Time period (default: 30)

**Response:**
```json
{
  "total_searches": 15420,
  "unique_queries": 3250,
  "avg_response_time": 0.089,
  "zero_result_rate": 0.08,
  "top_languages": [
    {"language": "en", "count": 10000},
    {"language": "fr", "count": 3500}
  ],
  "peak_hours": [
    {"hour": 14, "count": 1250},
    {"hour": 10, "count": 1100}
  ]
}
```

---

## Common Models

### SearchRequest

```json
{
  "query": "string (required)",
  "filters": {
    "document_type": "string",
    "language": "string",
    "author": "string",
    "status": "string"
  },
  "sort_by": "relevance|created_at|updated_at",
  "sort_order": "asc|desc",
  "page": 1,
  "page_size": 10
}
```

### SearchResult

```json
{
  "id": "integer",
  "document_id": "integer",
  "document_type": "string",
  "title": "string",
  "content_preview": "string",
  "language": "string",
  "author": "string",
  "created_at": "datetime",
  "relevance_score": "float"
}
```

### IndexDocument

```json
{
  "document_id": "integer (required)",
  "document_type": "string (required)",
  "title": "string (required)",
  "content": "string (required)",
  "language": "string (required)",
  "author": "string",
  "status": "string",
  "metadata": {}
}
```

---

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Invalid search parameters"
}
```

### 401 Unauthorized

```json
{
  "detail": "Authentication required"
}
```

### 404 Not Found

```json
{
  "detail": "Document not found"
}
```

### 422 Validation Error

```json
{
  "detail": [
    {
      "loc": ["body", "query"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

- **Search endpoints:** 100 requests/minute
- **Indexing endpoints:** 50 requests/minute
- **Autocomplete:** 200 requests/minute

## Interactive Documentation

- **Swagger UI:** http://localhost:8011/docs
- **ReDoc:** http://localhost:8011/redoc
