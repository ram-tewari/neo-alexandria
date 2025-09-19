# Neo Alexandria 2.0 - Advanced Knowledge Management API

## Overview

Neo Alexandria 2.0 is a comprehensive knowledge management system that provides intelligent content processing, advanced search capabilities, and personalized recommendations through a RESTful API. The system combines traditional information retrieval with modern AI-powered features to deliver a complete solution for knowledge curation and discovery.

## Key Features

### Content Ingestion and Processing
- **Asynchronous URL Ingestion**: Submit web content for intelligent processing
- **AI-Powered Analysis**: Automatic summarization, tagging, and classification
- **Multi-Format Support**: HTML, PDF, and plain text content extraction
- **Quality Assessment**: Comprehensive content quality scoring and evaluation

### Advanced Search and Discovery
- **Hybrid Search**: Combines keyword and semantic search with configurable weighting
- **Vector Embeddings**: Semantic similarity search using state-of-the-art embedding models
- **Faceted Search**: Advanced filtering by classification, language, quality, and subjects
- **Full-Text Search**: SQLite FTS5 integration with graceful fallbacks

### Knowledge Graph and Relationships
- **Hybrid Graph Scoring**: Multi-signal relationship detection combining vector similarity, shared subjects, and classification matches
- **Mind-Map Visualization**: Resource-centric neighbor discovery for exploration
- **Global Overview**: System-wide relationship analysis and connection mapping

### Personalized Recommendations
- **Content-Based Filtering**: Learn user preferences from existing library content
- **Fresh Content Discovery**: Source and rank new content from external providers
- **Explainable Recommendations**: Provide reasoning for recommendation decisions

### Authority Control and Classification
- **Subject Normalization**: Intelligent tag standardization and canonical forms
- **Hierarchical Classification**: UDC-inspired classification system with automatic assignment
- **Usage Tracking**: Monitor and optimize metadata usage patterns

## API-First Architecture

Neo Alexandria 2.0 is built with an API-first approach, enabling seamless integration with external systems and applications. The RESTful API provides comprehensive endpoints for all system functionality, making it suitable for both internal knowledge management and external service integration.

## Quick Start

### Prerequisites

- Python 3.8 or higher
- SQLite (default) or PostgreSQL database
- 4GB RAM minimum (8GB recommended for AI features)

### Installation

1. **Clone the repository and navigate to the project directory**

2. **Create a virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r backend/requirements.txt
```

4. **Run database migrations**
```bash
cd backend
alembic upgrade head
```

5. **Start the API server**
```bash
uvicorn backend.app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

### First API Call

Test the API by ingesting your first resource:

```bash
curl -X POST http://127.0.0.1:8000/resources \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/article"}'
```

## API Documentation

### Base URL
```
http://127.0.0.1:8000
```

### Authentication
Currently, no authentication is required for development and testing. Future releases will include API key authentication and rate limiting.

### Core Endpoints

#### Content Management
- `POST /resources` - Ingest new content from URLs
- `GET /resources` - List resources with filtering and pagination
- `GET /resources/{id}` - Retrieve specific resource details
- `PUT /resources/{id}` - Update resource metadata
- `DELETE /resources/{id}` - Remove resources
- `GET /resources/{id}/status` - Check ingestion status

#### Search and Discovery
- `POST /search` - Advanced search with hybrid keyword/semantic capabilities
- `GET /recommendations` - Get personalized content recommendations

#### Knowledge Graph
- `GET /graph/resource/{id}/neighbors` - Find related resources for mind-map visualization
- `GET /graph/overview` - Get global relationship overview

#### Authority and Classification
- `GET /authority/subjects/suggest` - Get subject suggestions for autocomplete
- `GET /authority/classification/tree` - Retrieve hierarchical classification structure

#### Curation and Quality Control
- `GET /curation/review-queue` - Access low-quality items for review
- `POST /curation/batch-update` - Apply batch updates to multiple resources

## Data Models

### Resource Model
The core data model follows Dublin Core metadata standards with custom extensions:

```json
{
  "id": "uuid",
  "title": "string",
  "description": "string",
  "creator": "string",
  "publisher": "string",
  "source": "string",
  "language": "string",
  "type": "string",
  "subject": ["string"],
  "classification_code": "string",
  "quality_score": 0.85,
  "read_status": "unread",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Search Request Model
```json
{
  "text": "search query",
  "hybrid_weight": 0.5,
  "filters": {
    "classification_code": ["004"],
    "language": ["en"],
    "min_quality": 0.7,
    "subject_any": ["Machine Learning"]
  },
  "limit": 25,
  "offset": 0,
  "sort_by": "relevance",
  "sort_dir": "desc"
}
```

### Recommendation Response Model
```json
{
  "items": [
    {
      "url": "https://example.com/article",
      "title": "Article Title",
      "snippet": "Brief description...",
      "relevance_score": 0.85,
      "reasoning": ["Aligned with Machine Learning, Python"]
    }
  ]
}
```

## Configuration

### Environment Variables
```bash
# Database Configuration
DATABASE_URL=sqlite:///backend.db

# AI Model Configuration
EMBEDDING_MODEL_NAME=nomic-ai/nomic-embed-text-v1
SUMMARIZER_MODEL=facebook/bart-large-cnn
TAGGER_MODEL=facebook/bart-large-mnli

# Search Configuration
DEFAULT_HYBRID_SEARCH_WEIGHT=0.5
EMBEDDING_CACHE_SIZE=1000

# Recommendation Configuration
RECOMMENDATION_PROFILE_SIZE=50
RECOMMENDATION_KEYWORD_COUNT=5
RECOMMENDATION_CANDIDATES_PER_KEYWORD=10
SEARCH_PROVIDER=ddgs
SEARCH_TIMEOUT=10

# Graph Configuration
GRAPH_WEIGHT_VECTOR=0.6
GRAPH_WEIGHT_TAGS=0.3
GRAPH_WEIGHT_CLASSIFICATION=0.1
GRAPH_VECTOR_MIN_SIM_THRESHOLD=0.85
```

## Error Handling

The API uses standard HTTP status codes and returns structured error responses:

```json
{
  "detail": "Error description",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Common Status Codes
- `200 OK` - Successful request
- `202 Accepted` - Request accepted for processing
- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

## Rate Limits

Currently, no rate limits are enforced. Future releases will implement:
- 1000 requests per hour per API key
- 100 ingestion requests per hour per API key
- Burst allowance for short-term spikes

## Examples

### Basic Content Ingestion
```bash
# Submit URL for processing
curl -X POST http://127.0.0.1:8000/resources \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/machine-learning-guide"}'

# Check processing status
curl http://127.0.0.1:8000/resources/{resource_id}/status

# Retrieve processed resource
curl http://127.0.0.1:8000/resources/{resource_id}
```

### Advanced Search
```bash
# Hybrid search with semantic similarity
curl -X POST http://127.0.0.1:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "text": "artificial intelligence algorithms",
    "hybrid_weight": 0.7,
    "filters": {
      "min_quality": 0.8,
      "subject_any": ["Machine Learning", "AI"]
    },
    "limit": 10
  }'
```

### Knowledge Graph Exploration
```bash
# Find related resources for mind-map
curl "http://127.0.0.1:8000/graph/resource/{resource_id}/neighbors?limit=7"

# Get global relationship overview
curl "http://127.0.0.1:8000/graph/overview?limit=50&vector_threshold=0.85"
```

### Personalized Recommendations
```bash
# Get content recommendations
curl "http://127.0.0.1:8000/recommendations?limit=10"
```

## Testing

Run the comprehensive test suite:

```bash
# All tests
pytest backend/tests/ -v

# With coverage reporting
pytest backend/tests/ --cov=backend --cov-report=html

# Specific test categories
pytest backend/tests/ -m "recommendation"  # Recommendation system tests
pytest backend/tests/ -m "integration"     # Integration tests
```

## Development Phases

### Phase 0: Foundation
- Database schema and models
- Migration system
- Configuration management

### Phase 1: Content Ingestion
- URL processing and content extraction
- Basic metadata extraction
- Local content archiving

### Phase 2: CRUD Operations
- Resource management endpoints
- Curation workflows
- Batch operations

### Phase 3: Search and Discovery
- Full-text search with FTS5
- Faceted search capabilities
- Advanced filtering

### Phase 3.5: AI Integration
- Asynchronous processing
- AI-powered summarization and tagging
- Quality assessment algorithms

### Phase 4: Vector Search
- Semantic embeddings
- Hybrid search fusion
- Vector similarity search

### Phase 5: Knowledge Graph
- Relationship detection
- Graph-based exploration
- Mind-map visualization

### Phase 5.5: Recommendations
- Personalized content recommendations
- External content sourcing
- Explainable recommendation reasoning

## Production Deployment

### System Requirements
- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: SSD recommended for database performance
- **Network**: Stable internet connection for content ingestion

### Database Considerations
- **SQLite**: Suitable for development and small deployments
- **PostgreSQL**: Recommended for production with high concurrency
- **Backup Strategy**: Regular database backups and migration testing

### Security Considerations
- API key authentication (future release)
- Rate limiting and abuse prevention
- Input validation and sanitization
- Secure content storage and access controls

## Support and Documentation

### Comprehensive Documentation
- **[API Reference](docs/API_DOCUMENTATION.md)** - Complete endpoint documentation
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)** - Architecture and development setup
- **[Examples](docs/EXAMPLES.md)** - Practical usage examples and tutorials
- **[Changelog](docs/CHANGELOG.md)** - Version history and release notes

### Community and Support
- GitHub Issues for bug reports and feature requests
- Documentation updates and improvements
- Community contributions and feedback

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing

We welcome contributions to Neo Alexandria 2.0. Please see our contributing guidelines in the documentation for details on:
- Code style and standards
- Testing requirements
- Documentation standards
- Pull request process

## Roadmap

### Upcoming Features
- API key authentication and rate limiting
- Advanced analytics and reporting
- Multi-user support and permissions
- Enhanced recommendation algorithms
- Real-time collaboration features
- Mobile API optimizations

### Long-term Vision
- Distributed knowledge graph federation
- Advanced AI model integration
- Enterprise-grade security and compliance
- Scalable cloud deployment options
- Integration with popular knowledge management tools