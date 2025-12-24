# Search Service

**Port:** 8011  
**Version:** 1.0.0  
**Status:** Production Ready

## Overview

The Search Service provides powerful full-text search capabilities across all Mission Engadi content. It uses PostgreSQL full-text search with advanced features like autocomplete, faceted search, and multi-language support.

## Key Features

### 🔍 Universal Search
- Full-text search across all content types
- Advanced filtering and sorting
- Pagination and result highlighting
- Multi-language support (EN, FR, ES, PT, etc.)

### 📊 Faceted Search
- Dynamic filtering by document type, language, author, status
- Real-time facet counts
- Multi-facet combinations

### ⚡ Autocomplete
- Intelligent query suggestions
- Popular and recent searches
- Trigram similarity matching
- Usage tracking

### 📂 Content Indexing
- Single and bulk indexing
- Automatic reindexing
- Index job tracking
- Service integration (Content, Partners, Projects)

### 📊 Analytics
- Query performance tracking
- Popular search terms
- Zero-result query detection
- Search behavior insights

## Technology Stack

- **Framework:** FastAPI 0.104+
- **Database:** PostgreSQL 14+ with pg_trgm extension
- **Search:** PostgreSQL Full-Text Search (tsvector, GIN indexes)
- **Language:** Python 3.11+
- **ORM:** SQLAlchemy 2.0+
- **Migrations:** Alembic

## Quick Start

### Prerequisites

```bash
# PostgreSQL 14+
sudo apt install postgresql postgresql-contrib

# Python 3.11+
python --version
```

### Installation

```bash
# Clone repository
cd search_service

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup database
psql -U postgres -c "CREATE DATABASE search_service_db;"
psql -U postgres -d search_service_db -c "CREATE EXTENSION pg_trgm;"

# Run migrations
alembic upgrade head

# Start service
./start.sh
```

### Service Management

```bash
# Start service
./start.sh

# Stop service
./stop.sh

# Restart service
./restart.sh

# Check status
./status.sh
```

## API Endpoints

The service exposes **25 API endpoints** organized into 4 main categories:

### Search (6 endpoints)
- `POST /api/v1/search` - Universal search
- `POST /api/v1/search/articles` - Search articles
- `POST /api/v1/search/projects` - Search projects
- `POST /api/v1/search/people` - Search people
- `POST /api/v1/search/partners` - Search partners
- `POST /api/v1/search/advanced` - Advanced search

### Indexing (8 endpoints)
- `POST /api/v1/indexing/index` - Index single document
- `POST /api/v1/indexing/bulk` - Bulk index
- `PUT /api/v1/indexing/update/{doc_id}` - Update document
- `DELETE /api/v1/indexing/delete/{doc_id}` - Delete document
- `POST /api/v1/indexing/reindex/{service}` - Reindex service
- `GET /api/v1/indexing/stats` - Index statistics
- `GET /api/v1/indexing/jobs` - List index jobs
- `GET /api/v1/indexing/jobs/{job_id}` - Get job status

### Autocomplete (4 endpoints)
- `GET /api/v1/autocomplete/suggestions` - Get suggestions
- `GET /api/v1/autocomplete/popular` - Popular searches
- `GET /api/v1/autocomplete/recent` - Recent searches (auth)
- `POST /api/v1/autocomplete/suggestions` - Add suggestion

### Facets (4 endpoints)
- `GET /api/v1/facets` - Get all facets
- `GET /api/v1/facets/document-types` - Document type facets
- `GET /api/v1/facets/languages` - Language facets
- `GET /api/v1/facets/authors` - Author facets

### Analytics (3 endpoints)
- `GET /api/v1/analytics/popular-queries` - Popular queries
- `GET /api/v1/analytics/zero-results` - Zero-result queries
- `GET /api/v1/analytics/metrics` - Search metrics

**Full API Documentation:** [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)

## Architecture

### Database Models (4)

1. **SearchIndex** - Main search index with tsvector
2. **SearchQuery** - Query tracking for analytics
3. **SearchSuggestion** - Autocomplete suggestions
4. **IndexJob** - Indexing job tracking

### Service Layers (6)

1. **SearchService** - Core search logic
2. **IndexingService** - Document indexing
3. **AutoCompleteService** - Suggestions
4. **FacetService** - Faceted search
5. **SearchAnalyticsService** - Analytics
6. **ServiceIntegration** - External service integration

### PostgreSQL Full-Text Search

- **tsvector columns** with GIN indexes
- **Automatic triggers** for search_vector updates
- **Multi-language support** with text search configurations
- **Trigram similarity** for fuzzy matching

## Configuration

Key environment variables (`.env`):

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost/search_service_db

# Service URLs
CONTENT_SERVICE_URL=http://localhost:8007
PARTNERS_SERVICE_URL=http://localhost:8009
PROJECTS_SERVICE_URL=http://localhost:8010
SOCIAL_MEDIA_SERVICE_URL=http://localhost:8012

# Search Settings
DEFAULT_PAGE_SIZE=10
MAX_PAGE_SIZE=100
MAX_SEARCH_RESULTS=1000
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_search.py -v
```

**Test Coverage:** 70%+ (40+ test cases)

## Integration Guide

See [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) for:
- Service-to-service integration
- Authentication requirements
- Webhook setup for auto-indexing
- Client libraries

## Deployment

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for:
- Production deployment
- Docker setup
- Performance tuning
- Monitoring

## Performance

- **Search latency:** < 100ms (typical)
- **Indexing throughput:** 1000+ docs/sec (bulk)
- **Concurrent requests:** 100+
- **Database:** GIN indexes for optimal performance

## Monitoring

### Health Check

```bash
curl http://localhost:8011/health
```

### Metrics

- Search query performance
- Index size and growth
- Popular search terms
- Zero-result queries

## Troubleshooting

### Common Issues

**Search returns no results:**
- Check if content is indexed: `GET /api/v1/indexing/stats`
- Verify database connection
- Check search_vector updates

**Slow search performance:**
- Verify GIN indexes: `\di search_index_*` in psql
- Check query complexity
- Review database statistics: `ANALYZE search_index`

**Autocomplete not working:**
- Verify pg_trgm extension: `SELECT * FROM pg_extension WHERE extname = 'pg_trgm';`
- Check suggestions table

## Support

- **Documentation:** [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
- **Integration:** [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md)
- **Deployment:** [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

## License

Mission Engadi © 2024
