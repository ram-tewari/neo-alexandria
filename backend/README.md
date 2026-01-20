# Neo Alexandria 2.0 - Advanced Knowledge Management API

## Overview

Neo Alexandria 2.0 is a comprehensive knowledge management system that provides intelligent content processing, advanced search capabilities, and personalized recommendations through a RESTful API. The system combines traditional information retrieval with modern AI-powered features to deliver a complete solution for knowledge curation and discovery.

> **📚 Quick Navigation:**
> - [Product Vision & Goals](../.kiro/steering/product.md) - What we're building and why
> - [Tech Stack & Architecture](../.kiro/steering/tech.md) - How we're building it
> - [Repository Structure](../.kiro/steering/structure.md) - Where things are located
> - [API Documentation](docs/index.md) - Complete API reference
> - [Architecture Guide](docs/architecture/overview.md) - System architecture details
> - [Developer Setup](docs/guides/setup.md) - Getting started guide

## Key Features

### Authentication and Security (Phase 17)
- **JWT Authentication**: Secure token-based authentication with access and refresh tokens
- **OAuth2 Integration**: Social login via Google and GitHub
- **Tiered Rate Limiting**: Free (100/hr), Premium (1,000/hr), and Admin (10,000/hr) tiers
- **Token Revocation**: Redis-backed token blacklist for secure logout
- **Password Security**: Bcrypt password hashing with automatic salt generation
- **User Management**: User registration, authentication, and profile management

### Content Ingestion and Processing
- **Asynchronous URL Ingestion**: Submit web content for intelligent processing
- **AI-Powered Analysis**: Automatic summarization, tagging, and classification
- **Multi-Format Support**: HTML, PDF, and plain text content extraction
- **Quality Assessment**: Comprehensive content quality scoring and evaluation

### Advanced Search and Discovery
- **Hybrid Search**: Combines keyword and semantic search with configurable weighting
- **Vector Embeddings**: Semantic similarity search using state-of-the-art embedding models
- **Advanced RAG (Phase 17.5)**: Parent-child chunking, GraphRAG retrieval, and question-based search
- **Faceted Search**: Advanced filtering by classification, language, quality, and subjects
- **Full-Text Search**: SQLite FTS5 integration with graceful fallbacks

### Advanced RAG Architecture (Phase 17.5)
- **Parent-Child Chunking**: Split documents into searchable chunks while maintaining parent context
- **GraphRAG Retrieval**: Entity extraction, graph traversal, and chunk retrieval
- **Synthetic Questions**: Reverse HyDE retrieval using generated questions
- **Knowledge Graph**: Semantic triple storage with provenance tracking
- **Contradiction Discovery**: Identify conflicting information across resources
- **RAG Evaluation**: RAGAS metrics for faithfulness, relevance, and precision
- **Migration Tools**: Batch migration script for existing resources

### Code Intelligence Pipeline (Phase 18)
- **Repository Ingestion**: Scan local directories or clone Git repositories (HTTPS/SSH)
- **AST-Based Chunking**: Parse code into logical units (functions, classes, methods) using Tree-Sitter
- **Multi-Language Support**: Python, JavaScript, TypeScript, Rust, Go, and Java

## Quick Start with Docker

```bash
cd backend
cp .env.production .env
# Edit .env: Set JWT_SECRET_KEY and POSTGRES_PASSWORD
docker-compose up -d
```

**Build Times:**
- First build: 10-15 minutes (downloads ~1GB ML libraries)
- Subsequent starts: 10-30 seconds (cached)
- After code changes: 30-60 seconds

See [Quick Start Guide](QUICK_START.md) or [Deployment Guide](docs/guides/deployment.md) for details.
- **Static Analysis**: Extract imports, definitions, and function calls without code execution
- **Code Graph**: Build dependency graphs with IMPORTS, DEFINES, and CALLS relationships
- **Gitignore Support**: Automatically respect .gitignore patterns during ingestion
- **Binary Detection**: Exclude binary files from analysis
- **File Classification**: Automatic categorization (PRACTICE, THEORY, GOVERNANCE)
- **Performance**: <2s per file for AST parsing, <1s for static analysis (P95)

### Knowledge Graph and Relationships
- **Hybrid Graph Scoring**: Multi-signal relationship detection combining vector similarity, shared subjects, and classification matches
- **Mind-Map Visualization**: Resource-centric neighbor discovery for exploration
- **Global Overview**: System-wide relationship analysis and connection mapping

### Citation Network & Link Intelligence
- **Multi-Format Citation Extraction**: Automatically extract citations from HTML, PDF, and Markdown content
- **Internal Citation Resolution**: Link citations to existing resources in your library
- **PageRank Importance Scoring**: Compute citation importance using network analysis
- **Citation Graph Visualization**: Build and explore citation networks with configurable depth
- **Smart Citation Classification**: Automatically categorize citations as datasets, code, references, or general links

### Personalized Recommendations
- **Content-Based Filtering**: Learn user preferences from existing library content
- **Fresh Content Discovery**: Source and rank new content from external providers
- **Explainable Recommendations**: Provide reasoning for recommendation decisions

### Collection Management
- **Curated Collections**: Organize resources into named, thematic collections with descriptions
- **Hierarchical Organization**: Create nested collections for complex topic structures
- **Visibility Controls**: Set collections as private, shared, or public for flexible collaboration
- **Aggregate Embeddings**: Automatic semantic representation computed from member resources
- **Collection Recommendations**: Discover similar resources and collections based on semantic similarity
- **Batch Operations**: Add or remove up to 100 resources in a single request
- **Automatic Cleanup**: Collections update automatically when resources are deleted
- **Access Control**: Owner-based permissions with visibility-based read access

### Annotation & Active Reading System
- **Precise Text Highlighting**: Character-offset-based text selection with context preservation
- **Rich Note-Taking**: Add personal notes to highlights with automatic semantic embedding
- **Tag Organization**: Categorize annotations with custom tags and color-coding
- **Full-Text Search**: Search across all annotation notes and highlighted text (<100ms for 10K annotations)
- **Semantic Search**: Find conceptually related annotations using AI-powered similarity
- **Export Capabilities**: Export annotations to Markdown or JSON for external tools
- **Collection Integration**: Associate annotations with research collections
- **Privacy Controls**: Annotations are private by default with optional sharing

### Authority Control and Classification
- **Subject Normalization**: Intelligent tag standardization and canonical forms
- **Hierarchical Classification**: UDC-inspired classification system with automatic assignment
- **Usage Tracking**: Monitor and optimize metadata usage patterns

### ML-Powered Classification & Taxonomy
- **Transformer-Based Classification**: Fine-tuned BERT/DistilBERT models for accurate resource categorization
- **Hierarchical Taxonomy Management**: Create and manage multi-level category trees with parent-child relationships
- **Multi-Label Classification**: Resources can belong to multiple categories with confidence scores
- **Semi-Supervised Learning**: Train effective models with minimal labeled data (<500 examples)
- **Active Learning**: System identifies uncertain predictions for targeted human review
- **Confidence Scoring**: Every classification includes a confidence score (0.0-1.0) for transparency
- **Model Versioning**: Track and manage multiple model versions with rollback capability
- **GPU Acceleration**: Automatic GPU utilization with graceful CPU fallback
- **Continuous Improvement**: Models improve automatically through human feedback loops

## API-First Architecture

Neo Alexandria 2.0 is built with an API-first approach, enabling seamless integration with external systems and applications. The RESTful API provides comprehensive endpoints for all system functionality, making it suitable for both internal knowledge management and external service integration.

## Quick Start

### Prerequisites

- Python 3.8 or higher
- SQLite (default) or PostgreSQL database
- Docker Desktop (for PostgreSQL and Redis)
- 4GB RAM minimum (8GB recommended for AI features)

### Option 1: Docker Development Setup (Recommended)

Use Docker for backing services (PostgreSQL and Redis) while running the application locally:

1. **Start backing services**
```bash
cd backend
docker-compose -f docker-compose.dev.yml up -d
```

2. **Create virtual environment and install dependencies**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment**
```bash
# Create .env file with:
DATABASE_URL=postgresql+asyncpg://postgres:devpassword@localhost:5432/neo_alexandria_dev
REDIS_HOST=localhost
REDIS_PORT=6379
```

4. **Run database migrations**
```bash
alembic upgrade head
```

5. **Start the API server**
```bash
uvicorn app.main:app --reload
```

📖 **See [DOCKER_SETUP_GUIDE.md](DOCKER_SETUP_GUIDE.md) for detailed Docker setup instructions**

### Option 2: SQLite Setup (Simple)

Use SQLite for a zero-configuration setup:

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
- `GET /search/three-way-hybrid` - Three-way hybrid search with RRF and reranking
- `GET /search/compare-methods` - Compare different search methods side-by-side
- `POST /search/evaluate` - Evaluate search quality with IR metrics
- `POST /admin/sparse-embeddings/generate` - Batch generate sparse embeddings
- `GET /recommendations` - Get personalized content recommendations

#### Knowledge Graph
- `GET /graph/resource/{id}/neighbors` - Find related resources for mind-map visualization
- `GET /graph/overview` - Get global relationship overview

#### Citation Network
- `GET /citations/resources/{id}/citations` - Get citations for a resource (inbound/outbound)
- `GET /citations/graph/citations` - Get citation network for visualization
- `POST /citations/resources/{id}/citations/extract` - Trigger citation extraction
- `POST /citations/resolve` - Resolve internal citations
- `POST /citations/importance/compute` - Compute PageRank importance scores

#### Collection Management
- `POST /collections` - Create a new collection
- `GET /collections/{id}` - Retrieve collection details with member resources
- `PUT /collections/{id}` - Update collection metadata
- `DELETE /collections/{id}` - Delete collection and subcollections
- `GET /collections` - List collections with filtering and pagination
- `POST /collections/{id}/resources` - Add resources to collection
- `DELETE /collections/{id}/resources` - Remove resources from collection
- `GET /collections/{id}/recommendations` - Get similar resources and collections
- `GET /collections/{id}/embedding` - Retrieve collection aggregate embedding

#### Annotation Management
- `POST /resources/{resource_id}/annotations` - Create annotation on resource
- `GET /resources/{resource_id}/annotations` - List resource annotations
- `GET /annotations` - List user annotations with pagination
- `GET /annotations/{id}` - Retrieve specific annotation
- `PUT /annotations/{id}` - Update annotation note, tags, or color
- `DELETE /annotations/{id}` - Delete annotation
- `GET /annotations/search/fulltext` - Full-text search across annotations
- `GET /annotations/search/semantic` - Semantic search with similarity scores
- `GET /annotations/search/tags` - Tag-based annotation search
- `GET /annotations/export/markdown` - Export annotations to Markdown
- `GET /annotations/export/json` - Export annotations to JSON

#### Authority and Classification
- `GET /authority/subjects/suggest` - Get subject suggestions for autocomplete
- `GET /authority/classification/tree` - Retrieve hierarchical classification structure

#### Taxonomy Management (Phase 8.5)
- `POST /taxonomy/nodes` - Create new taxonomy node
- `PUT /taxonomy/nodes/{node_id}` - Update taxonomy node metadata
- `DELETE /taxonomy/nodes/{node_id}` - Delete taxonomy node (with cascade option)
- `POST /taxonomy/nodes/{node_id}/move` - Move node to different parent
- `GET /taxonomy/tree` - Retrieve hierarchical taxonomy tree
- `GET /taxonomy/nodes/{node_id}/ancestors` - Get ancestor nodes (breadcrumb trail)
- `GET /taxonomy/nodes/{node_id}/descendants` - Get all descendant nodes

#### ML Classification (Phase 8.5)
- `POST /taxonomy/classify/{resource_id}` - Classify resource using ML model
- `GET /taxonomy/active-learning/uncertain` - Get uncertain predictions for review
- `POST /taxonomy/active-learning/feedback` - Submit human classification feedback
- `POST /taxonomy/train` - Initiate model fine-tuning with training data

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

### Database Configuration

Neo Alexandria 2.0 supports both SQLite and PostgreSQL databases. Choose the appropriate database based on your deployment scenario:

#### SQLite (Development)
- **Use Case**: Local development, testing, small deployments
- **Advantages**: Zero configuration, file-based, portable
- **Limitations**: Limited concurrency, no advanced features
- **Configuration**:
  ```bash
  DATABASE_URL=sqlite:///./backend.db
  ```

#### PostgreSQL (Production)
- **Use Case**: Production deployments, high concurrency, large datasets
- **Advantages**: Advanced indexing, JSONB support, full-text search, high concurrency
- **Requirements**: PostgreSQL 15 or higher
- **Configuration**:
  ```bash
  DATABASE_URL=postgresql://user:password@host:5432/database
  ```

#### Database Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | `sqlite:///./backend.db` | Primary database connection string |
| `TEST_DATABASE_URL` | No | `sqlite:///:memory:` | Test database connection string (overrides default test database) |
| `ENV` | No | `dev` | Environment name (`dev`, `staging`, `prod`) |

#### Database URL Format

**SQLite:**
```bash
# File-based database
DATABASE_URL=sqlite:///./backend.db

# In-memory database (testing only)
DATABASE_URL=sqlite:///:memory:

# Absolute path
DATABASE_URL=sqlite:////absolute/path/to/database.db
```

**PostgreSQL:**
```bash
# Basic connection
DATABASE_URL=postgresql://username:password@hostname:5432/database_name

# With SSL (recommended for production)
DATABASE_URL=postgresql://username:password@hostname:5432/database_name?sslmode=require

# With connection pool parameters
DATABASE_URL=postgresql://username:password@hostname:5432/database_name?pool_size=20&max_overflow=40
```

#### Environment-Specific Configuration Files

Neo Alexandria provides example configuration files for different environments:

- **`.env.development`** - Local development with SQLite
- **`.env.staging`** - Staging environment with PostgreSQL
- **`.env.production`** - Production environment with PostgreSQL

Copy the appropriate file to `.env` and customize for your environment:

```bash
# For local development
cp .env.development .env

# For staging
cp .env.staging .env
# Edit .env and update database credentials

# For production
cp .env.production .env
# Edit .env and update database credentials
```

#### Testing with Different Databases

By default, tests use in-memory SQLite for speed. To test against PostgreSQL:

```bash
# Set TEST_DATABASE_URL in your .env file
TEST_DATABASE_URL=postgresql://user:password@localhost:5432/test_db

# Or set it inline when running tests
TEST_DATABASE_URL=postgresql://user:password@localhost:5432/test_db pytest backend/tests/
```

#### Database Migration

When switching from SQLite to PostgreSQL or vice versa:

1. **Run migrations** to ensure schema is up to date:
   ```bash
   cd backend
   alembic upgrade head
   ```

2. **Migrate data** (if switching databases):
   ```bash
   # SQLite to PostgreSQL (forward migration)
   python backend/scripts/migrate_sqlite_to_postgresql.py \
     --source sqlite:///./backend.db \
     --target postgresql://user:password@host:5432/database \
     --validate
   
   # PostgreSQL to SQLite (rollback/reverse migration)
   python backend/scripts/migrate_postgresql_to_sqlite.py \
     --source postgresql://user:password@host:5432/database \
     --target sqlite:///./backend.db \
     --validate
   ```

3. **Verify migration** by checking row counts and running tests

#### Rollback Procedures

If you need to rollback from PostgreSQL to SQLite:

1. **Stop the application**:
   ```bash
   # Docker Compose
   docker-compose down
   
   # Or kill the process
   pkill -f "uvicorn backend.app.main:app"
   ```

2. **Restore SQLite backup** (if available):
   ```bash
   cp backend.db.backup backend.db
   ```

3. **Or run reverse migration** (if no backup):
   ```bash
   python backend/scripts/migrate_postgresql_to_sqlite.py \
     --source postgresql://user:password@host:5432/database \
     --target sqlite:///./backend.db \
     --validate
   ```

4. **Update environment configuration**:
   ```bash
   # Update .env file
   DATABASE_URL=sqlite:///./backend.db
   ```

5. **Restart the application**:
   ```bash
   uvicorn backend.app.main:app --reload
   ```

**⚠️ Important Rollback Limitations:**
- JSONB columns are converted to JSON text (no binary optimization)
- PostgreSQL full-text search vectors are not migrated (FTS5 must be rebuilt)
- Some PostgreSQL-specific indexes cannot be recreated in SQLite
- Array types are converted to JSON arrays

For detailed rollback procedures and troubleshooting, see:
- **[PostgreSQL Migration Guide](backend/docs/POSTGRESQL_MIGRATION_GUIDE.md)** - Complete migration and rollback procedures
- **[SQLite Compatibility Maintenance](backend/docs/SQLITE_COMPATIBILITY_MAINTENANCE.md)** - Maintaining compatibility during transition

#### Connection Pool Configuration

PostgreSQL connection pooling is automatically configured with optimal defaults:

- **Pool Size**: 20 base connections
- **Max Overflow**: 40 additional connections for burst traffic
- **Pool Recycle**: 3600 seconds (1 hour)
- **Pool Pre-Ping**: Enabled (validates connections before use)

Monitor connection pool usage via the monitoring endpoint:
```bash
curl http://localhost:8000/monitoring/database
```

### Environment Variables
```bash
# Database Configuration
DATABASE_URL=sqlite:///backend.db
TEST_DATABASE_URL=sqlite:///:memory:

# Phase 17: Authentication and Security
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# OAuth2 Providers (Optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
GITHUB_REDIRECT_URI=http://localhost:8000/auth/github/callback

# Rate Limiting
REDIS_HOST=localhost
REDIS_PORT=6379
RATE_LIMIT_FREE_TIER=100
RATE_LIMIT_PREMIUM_TIER=1000
RATE_LIMIT_ADMIN_TIER=10000

# Testing Mode (Development only)
TEST_MODE=false

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

**Generate Secure JWT Secret:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
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
- `401 Unauthorized` - Missing or invalid authentication token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
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

### Collection Management
```bash
# Create a new collection
curl -X POST http://127.0.0.1:8000/collections \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Machine Learning Papers",
    "description": "Curated collection of ML research",
    "visibility": "public"
  }'

# Add resources to collection
curl -X POST http://127.0.0.1:8000/collections/{collection_id}/resources \
  -H "Content-Type: application/json" \
  -d '{
    "resource_ids": [
      "550e8400-e29b-41d4-a716-446655440000",
      "660e8400-e29b-41d4-a716-446655440001"
    ]
  }'

# Get collection with member resources
curl "http://127.0.0.1:8000/collections/{collection_id}"

# Get recommendations based on collection
curl "http://127.0.0.1:8000/collections/{collection_id}/recommendations?limit=10"

# Create nested collection
curl -X POST http://127.0.0.1:8000/collections \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Deep Learning Subset",
    "parent_id": "{parent_collection_id}",
    "visibility": "public"
  }'
```

### Annotation and Active Reading
```bash
# Create annotation on a resource
curl -X POST http://127.0.0.1:8000/resources/{resource_id}/annotations \
  -H "Content-Type: application/json" \
  -d '{
    "start_offset": 150,
    "end_offset": 200,
    "highlighted_text": "This is the key finding of the paper",
    "note": "Important result - contradicts previous assumptions",
    "tags": ["key-finding", "methodology"],
    "color": "#FFD700"
  }'

# Search annotations semantically
curl "http://127.0.0.1:8000/annotations/search/semantic?query=machine+learning+algorithms&limit=10"

# Export annotations to Markdown
curl "http://127.0.0.1:8000/annotations/export/markdown?resource_id={resource_id}"

# List all user annotations
curl "http://127.0.0.1:8000/annotations?limit=50&sort_by=recent"
```

### Three-Way Hybrid Search (Phase 8)
```bash
# Three-way hybrid search with reranking
curl -X GET "http://127.0.0.1:8000/search/three-way-hybrid?query=machine+learning&limit=20&enable_reranking=true&adaptive_weighting=true"

# Compare all search methods side-by-side
curl -X GET "http://127.0.0.1:8000/search/compare-methods?query=neural+networks&limit=10"

# Evaluate search quality with metrics
curl -X POST http://127.0.0.1:8000/search/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "deep learning",
    "relevance_judgments": {
      "resource_id_1": 3,
      "resource_id_2": 2,
      "resource_id_3": 1
    }
  }'

# Generate sparse embeddings for existing resources
curl -X POST http://127.0.0.1:8000/admin/sparse-embeddings/generate \
  -H "Content-Type: application/json" \
  -d '{"batch_size": 32}'

# Three-way search without reranking (faster)
curl -X GET "http://127.0.0.1:8000/search/three-way-hybrid?query=artificial+intelligence&limit=20&enable_reranking=false"

# Three-way search with custom weighting (disable adaptive)
curl -X GET "http://127.0.0.1:8000/search/three-way-hybrid?query=data+science&limit=20&adaptive_weighting=false"
```

### ML Classification & Taxonomy Management (Phase 8.5)
```bash
# Create a taxonomy node
curl -X POST http://127.0.0.1:8000/taxonomy/nodes \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Machine Learning",
    "description": "ML and deep learning topics",
    "keywords": ["neural networks", "deep learning"],
    "allow_resources": true
  }'

# Create a child node
curl -X POST http://127.0.0.1:8000/taxonomy/nodes \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Deep Learning",
    "parent_id": "{parent_node_id}",
    "description": "Neural networks with multiple layers"
  }'

# Get the full taxonomy tree
curl "http://127.0.0.1:8000/taxonomy/tree"

# Get a subtree starting from a specific node
curl "http://127.0.0.1:8000/taxonomy/tree?root_id={node_id}&max_depth=3"

# Get ancestors (breadcrumb trail)
curl "http://127.0.0.1:8000/taxonomy/nodes/{node_id}/ancestors"

# Get all descendants
curl "http://127.0.0.1:8000/taxonomy/nodes/{node_id}/descendants"

# Move a node to a different parent
curl -X POST http://127.0.0.1:8000/taxonomy/nodes/{node_id}/move \
  -H "Content-Type: application/json" \
  -d '{"new_parent_id": "{new_parent_id}"}'

# Classify a resource using ML
curl -X POST "http://127.0.0.1:8000/taxonomy/classify/{resource_id}"

# Get uncertain predictions for human review
curl "http://127.0.0.1:8000/taxonomy/active-learning/uncertain?limit=50"

# Submit human feedback on classification
curl -X POST http://127.0.0.1:8000/taxonomy/active-learning/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "resource_id": "{resource_id}",
    "correct_taxonomy_ids": ["{node_id_1}", "{node_id_2}"]
  }'

# Train/fine-tune the ML model
curl -X POST http://127.0.0.1:8000/taxonomy/train \
  -H "Content-Type: application/json" \
  -d '{
    "labeled_data": [
      {
        "text": "Introduction to neural networks and backpropagation",
        "taxonomy_ids": ["{ml_node_id}", "{dl_node_id}"]
      }
    ],
    "unlabeled_texts": [
      "Article about convolutional neural networks",
      "Tutorial on recurrent neural networks"
    ],
    "epochs": 3,
    "batch_size": 16
  }'
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

### Phase 6: Citation Network & Link Intelligence ✅
- Citation extraction from HTML, PDF, and Markdown
- Internal citation resolution (link resources together)
- PageRank-style importance scoring
- Citation graph visualization endpoints
- Integration with knowledge graph service

### Phase 6.5: Advanced Metadata Extraction & Scholarly Processing ✅
- Fine-tuned metadata extraction for academic papers (authors, DOI, affiliations, funding)
- Mathematical equation extraction with LaTeX format preservation
- Table extraction with structure preservation (camelot-py + tabula-py)
- Figure/image extraction with caption detection
- OCR processing for scanned PDFs with error correction
- Metadata validation and completeness scoring
- Scholarly metadata API endpoints for comprehensive access
- Integration with quality service for metadata quality scoring

### Phase 7: Collection Management ✅
- User-curated collections for organizing resources into thematic groups
- Hierarchical collection organization with parent/child relationships
- Flexible visibility controls (private, shared, public) for collaboration
- Aggregate embedding computation for collection-level semantic representation
- Intelligent recommendations based on collection similarity
- Resource membership management with batch operations
- Automatic collection updates when resources are deleted
- Integration with existing search and recommendation infrastructure

### Phase 7.5: Annotation & Active Reading System ✅
- Character-offset-based text highlighting with precise positioning
- Rich annotation notes with automatic semantic embedding generation
- Tag-based organization with color-coding for visual categorization
- Full-text search across notes and highlighted text (<100ms for 10K annotations)
- Semantic search using cosine similarity for conceptual discovery
- Markdown and JSON export for integration with external note-taking tools
- Collection integration for project-based annotation organization
- Privacy-first design with optional annotation sharing
- Performance: <50ms annotation creation, <500ms semantic search, <2s export for 1K annotations

### Phase 8: Three-Way Hybrid Search with Sparse Vectors & Reranking ✅
- Sparse vector embeddings using BGE-M3 model for learned keyword representations
- Three-way retrieval combining FTS5, dense vectors, and sparse vectors
- Reciprocal Rank Fusion (RRF) for score-agnostic result merging
- Query-adaptive weighting that automatically adjusts method importance
- ColBERT-style cross-encoder reranking for maximum precision
- Comprehensive search metrics (nDCG, Recall, Precision, MRR)
- Method comparison endpoints for debugging and optimization
- Batch sparse embedding generation with progress tracking
- Performance: <200ms three-way search, <1s reranking, 30%+ nDCG improvement

### Phase 8: Three-Way Hybrid Search with Sparse Vectors & Reranking ✅
- Sparse vector embeddings using BGE-M3 model for learned keyword representations
- Three-way retrieval combining FTS5, dense vectors, and sparse vectors
- Reciprocal Rank Fusion (RRF) for score-agnostic result merging
- Query-adaptive weighting that automatically adjusts method importance
- ColBERT-style cross-encoder reranking for maximum precision
- Comprehensive search metrics (nDCG, Recall, Precision, MRR)
- Method comparison endpoints for debugging and optimization
- Batch sparse embedding generation with progress tracking
- Performance: <200ms three-way search, <1s reranking, 30%+ nDCG improvement

### Phase 8.5: ML Classification & Hierarchical Taxonomy ✅
- Transformer-based classification using fine-tuned BERT/DistilBERT models
- Hierarchical taxonomy tree with unlimited depth and parent-child relationships
- Multi-label classification with confidence scores (0.0-1.0) for each category
- Semi-supervised learning to leverage unlabeled data with <500 labeled examples
- Active learning workflow to identify uncertain predictions for human review
- Materialized path pattern for efficient ancestor/descendant queries
- Model versioning and checkpoint management for rollback capability
- GPU acceleration support with automatic CPU fallback
- Automatic classification during resource ingestion pipeline
- Performance: <100ms inference, F1 score >0.85, 60%+ reduction in labeling effort

## Production Deployment

### System Requirements
- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB recommended for AI features
- **Storage**: SSD recommended for database performance (minimum 20GB free space)
- **Network**: Stable internet connection for content ingestion
- **Database**: PostgreSQL 15+ for production (SQLite for development)

### Database Selection Guide

#### SQLite (Development & Small Deployments)
**Use Cases:**
- Local development and testing
- Single-user deployments
- Prototyping and demos
- Small datasets (<10,000 resources)

**Advantages:**
- Zero configuration required
- File-based (portable)
- No separate database server needed
- Perfect for development

**Limitations:**
- Limited concurrent writes (single writer)
- No advanced indexing (GIN, JSONB)
- File locking can cause issues under load
- Not suitable for production with multiple users

#### PostgreSQL (Production & High Concurrency)
**Use Cases:**
- Production deployments
- Multi-user environments
- High concurrency requirements (100+ simultaneous users)
- Large datasets (>10,000 resources)
- Advanced search and analytics

**Advantages:**
- Excellent concurrent write performance
- Advanced indexing (GIN indexes for JSONB, full-text search)
- Native JSONB support for efficient JSON queries
- Connection pooling with health checks
- Production-grade reliability and ACID compliance
- Point-in-time recovery and replication support

**Requirements:**
- PostgreSQL 15 or higher
- Dedicated database server or managed service (AWS RDS, Google Cloud SQL, Azure Database)
- Regular backups and monitoring

### PostgreSQL Setup for Production

#### Option 1: Docker Compose (Recommended for Development/Staging)
```bash
# Start PostgreSQL with Docker
cd backend/docker
docker-compose up -d postgres

# Verify PostgreSQL is running
docker-compose ps

# Check logs
docker-compose logs postgres
```

#### Option 2: Managed Database Service (Recommended for Production)
**AWS RDS:**
```bash
# Create PostgreSQL RDS instance
aws rds create-db-instance \
  --db-instance-identifier neo-alexandria-prod \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --engine-version 15.4 \
  --master-username admin \
  --master-user-password <secure-password> \
  --allocated-storage 100 \
  --backup-retention-period 7 \
  --multi-az
```

**Google Cloud SQL:**
```bash
# Create PostgreSQL instance
gcloud sql instances create neo-alexandria-prod \
  --database-version=POSTGRES_15 \
  --tier=db-custom-2-7680 \
  --region=us-central1 \
  --backup \
  --backup-start-time=02:00
```

#### Option 3: Self-Hosted PostgreSQL
```bash
# Install PostgreSQL 15 (Ubuntu/Debian)
sudo apt update
sudo apt install postgresql-15 postgresql-contrib-15

# Create database and user
sudo -u postgres psql
CREATE DATABASE neo_alexandria;
CREATE USER neo_user WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE neo_alexandria TO neo_user;
\q
```

### Migration from SQLite to PostgreSQL

**Prerequisites:**
- Backup your SQLite database
- PostgreSQL 15+ installed and running
- Python environment with all dependencies

**Migration Steps:**
```bash
# 1. Backup SQLite database
cp backend.db backend.db.backup

# 2. Set up PostgreSQL connection
export DATABASE_URL="postgresql://user:password@host:5432/database"

# 3. Run schema migrations
cd backend
alembic upgrade head

# 4. Migrate data from SQLite to PostgreSQL
python scripts/migrate_sqlite_to_postgresql.py \
  --source sqlite:///./backend.db \
  --target postgresql://user:password@host:5432/database \
  --validate

# 5. Verify migration
# Check row counts match between source and target

# 6. Update environment configuration
# Edit .env file
DATABASE_URL=postgresql://user:password@host:5432/database

# 7. Restart application
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

**Migration Validation:**
```bash
# Compare row counts
python -c "
from sqlalchemy import create_engine, inspect
sqlite_engine = create_engine('sqlite:///./backend.db')
pg_engine = create_engine('postgresql://user:password@host:5432/database')

for table in inspect(sqlite_engine).get_table_names():
    sqlite_count = sqlite_engine.execute(f'SELECT COUNT(*) FROM {table}').scalar()
    pg_count = pg_engine.execute(f'SELECT COUNT(*) FROM {table}').scalar()
    print(f'{table}: SQLite={sqlite_count}, PostgreSQL={pg_count}')
"
```

### Database Backup Strategy

#### PostgreSQL Backups
```bash
# Full database backup
pg_dump -h localhost -U postgres -d neo_alexandria > backup_$(date +%Y%m%d).sql

# Compressed backup
pg_dump -h localhost -U postgres -d neo_alexandria | gzip > backup_$(date +%Y%m%d).sql.gz

# Custom format (supports parallel restore)
pg_dump -h localhost -U postgres -d neo_alexandria -Fc > backup_$(date +%Y%m%d).dump
```

**Automated Backup Script:**
```bash
# Use the provided backup script
chmod +x backend/scripts/backup_postgresql.sh
./backend/scripts/backup_postgresql.sh

# Schedule with cron (daily at 2 AM)
crontab -e
0 2 * * * /path/to/backend/scripts/backup_postgresql.sh
```

**Backup Retention Policy:**
- Daily backups: Keep for 7 days
- Weekly backups: Keep for 4 weeks
- Monthly backups: Keep for 12 months

#### SQLite Backups
```bash
# Simple file copy
cp backend.db backend.db.backup_$(date +%Y%m%d)

# Using SQLite backup command
sqlite3 backend.db ".backup 'backend.db.backup_$(date +%Y%m%d)'"
```

### Monitoring and Performance

#### Connection Pool Monitoring
```bash
# Check connection pool status
curl http://localhost:8000/monitoring/database

# Response includes:
# - database_type: "postgresql" or "sqlite"
# - pool_size: 20 (PostgreSQL)
# - connections_in_use: current active connections
# - connections_available: idle connections
# - overflow_connections: connections beyond pool_size
```

#### Performance Tuning (PostgreSQL)
```sql
-- Check slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- Check cache hit ratio (should be >90%)
SELECT 
  sum(heap_blks_read) as heap_read,
  sum(heap_blks_hit) as heap_hit,
  sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as ratio
FROM pg_statio_user_tables;
```

### Rollback Procedures

If you need to rollback from PostgreSQL to SQLite:

```bash
# 1. Stop the application
pkill -f "uvicorn backend.app.main:app"

# 2. Run reverse migration
python backend/scripts/migrate_postgresql_to_sqlite.py \
  --source postgresql://user:password@host:5432/database \
  --target sqlite:///./backend.db \
  --validate

# 3. Update environment
DATABASE_URL=sqlite:///./backend.db

# 4. Restart application
uvicorn backend.app.main:app --reload
```

**⚠️ Rollback Limitations:**
- JSONB columns converted to JSON text (no binary optimization)
- PostgreSQL full-text search vectors not migrated (FTS5 must be rebuilt)
- Some PostgreSQL-specific indexes cannot be recreated in SQLite
- Performance may degrade for large datasets

### Security Considerations
- **Database Security:**
  - Use strong passwords for database users
  - Enable SSL/TLS for database connections in production
  - Restrict database access to application servers only
  - Regular security updates for PostgreSQL
  
- **Application Security:**
  - API key authentication (future release)
  - Rate limiting and abuse prevention
  - Input validation and sanitization
  - Secure content storage and access controls

### Additional Resources
- **[PostgreSQL Migration Guide](backend/docs/POSTGRESQL_MIGRATION_GUIDE.md)** - Complete migration procedures
- **[PostgreSQL Backup Guide](backend/docs/POSTGRESQL_BACKUP_GUIDE.md)** - Backup and recovery procedures
- **[SQLite Compatibility Guide](backend/docs/SQLITE_COMPATIBILITY_MAINTENANCE.md)** - Maintaining compatibility
- **[Developer Guide](backend/docs/DEVELOPER_GUIDE.md)** - Database configuration details

## Support and Documentation

### Steering Documentation (Start Here)
- **[Product Overview](../.kiro/steering/product.md)** - Product vision, goals, and non-goals
- **[Tech Stack](../.kiro/steering/tech.md)** - Technology choices, commands, and constraints
- **[Repository Structure](../.kiro/steering/structure.md)** - Navigation guide and truth sources
- **[Agent Routing](../AGENTS.md)** - Context management for AI agents

### Technical Documentation
- **[Documentation Index](docs/index.md)** - Complete documentation hub
- **[API Reference](docs/api/overview.md)** - Modular API documentation by domain
- **[Architecture Guide](docs/architecture/overview.md)** - System architecture and design
- **[Developer Guide](docs/guides/setup.md)** - Setup and development workflows
- **[Testing Guide](docs/guides/testing.md)** - Testing strategies and patterns

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