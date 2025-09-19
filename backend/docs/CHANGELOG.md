# Neo Alexandria 2.0 Changelog

All notable changes to Neo Alexandria 2.0 are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.7.1] - 2025-01-15 - Phase 5.5: Personalized Recommendation Engine

### Added
- **Personalized Recommendation System**
  - `app/services/recommendation_service.py` - Core recommendation engine with user profile generation
  - `app/schemas/recommendation.py` - Pydantic models for recommendation responses
  - `app/routers/recommendation.py` - REST API endpoint for recommendations
  - `tests/test_phase55_recommendations.py` - Comprehensive test suite with 31 test cases

- **User Profile Generation**
  - Automatic user profile vector creation from top-quality library resources
  - Configurable profile size (default: 50 resources)
  - Embedding averaging for preference learning
  - Graceful handling of empty or insufficient libraries

- **External Content Discovery**
  - Pluggable search provider architecture (default: DuckDuckGo Search)
  - Configurable keyword extraction from authority subjects
  - Candidate sourcing with deduplication and caching
  - Timeout and error handling for external services

- **Recommendation Scoring**
  - Cosine similarity-based relevance scoring
  - Lightweight in-memory processing
  - Explainable recommendation reasoning
  - Relevance score validation (0.0-1.0 range)

- **Configuration System**
  - `RECOMMENDATION_PROFILE_SIZE` - Number of top resources for profile (default: 50)
  - `RECOMMENDATION_KEYWORD_COUNT` - Number of seed keywords (default: 5)
  - `RECOMMENDATION_CANDIDATES_PER_KEYWORD` - Candidates per keyword (default: 10)
  - `SEARCH_PROVIDER` - External search provider (default: "ddgs")
  - `SEARCH_TIMEOUT` - Search timeout in seconds (default: 10)

### Technical Implementation
- **Dependencies**
  - Added `duckduckgo-search==5.3.1` for external content discovery
  - Updated `numpy>=2.0.0` for vector operations and cosine similarity
  - Maintained compatibility with existing AI and search infrastructure

- **Performance Optimizations**
  - In-memory caching for search results (5-minute TTL)
  - Efficient vector operations using NumPy
  - Batch candidate processing with early termination
  - Graceful degradation on external service failures

- **Testing Infrastructure**
  - Comprehensive test coverage with unit, integration, and API tests
  - Mocked external dependencies for reliable testing
  - Performance benchmarking and edge case validation
  - Custom test markers for organized test execution

### API Changes
- **New Endpoint**
  - `GET /recommendations?limit=N` - Retrieve personalized content recommendations
  - Query parameter validation (limit: 1-100, default: 10)
  - Structured JSON response with relevance scores and reasoning

### Documentation
- **Updated Documentation**
  - Comprehensive API reference with recommendation examples
  - Developer guide with architecture and setup instructions
  - Practical examples and tutorials in multiple programming languages
  - Professional-grade documentation following API documentation standards

## [0.7.0] - 2025-01-15 - Phase 5: Hybrid Knowledge Graph

### Added
- **Hybrid Knowledge Graph System**
  - `app/services/graph_service.py` - Core graph computation service with multi-signal scoring
  - `app/schemas/graph.py` - Pydantic models for graph data structures
  - `app/routers/graph.py` - REST API endpoints for graph functionality
  - `tests/test_phase5_graph_api.py` - Comprehensive test suite for graph functionality

- **Graph Scoring Algorithms**
  - NumPy-based cosine similarity computation with fallback for zero vectors
  - Tag overlap scoring with diminishing returns heuristic
  - Binary classification code matching for exact code matches
  - Hybrid weight fusion combining vector (60%), tag (30%), and classification (10%) signals

- **Mind-Map Neighbor Discovery**
  - `GET /graph/resource/{id}/neighbors` endpoint for resource-centric exploration
  - Configurable neighbor limits (default: 7, range: 1-20)
  - Multi-signal candidate gathering from vector similarity, shared subjects, and classification matches
  - Transparent edge details explaining connection reasoning

- **Global Overview Analysis**
  - `GET /graph/overview` endpoint for system-wide relationship analysis
  - Configurable edge limits (default: 50, range: 10-100)
  - Vector similarity threshold filtering for candidate pruning (default: 0.85)
  - Combines high vector similarity pairs and significant tag overlap pairs

### Technical Implementation
- **Database Integration**
  - Leverages existing `embedding` JSON column for vector similarity
  - Uses `subject` JSON array for tag overlap analysis
  - Utilizes `classification_code` for exact matching
  - No additional database schema changes required

- **Performance Optimizations**
  - Efficient JSON queries for subject overlap detection
  - Candidate pre-filtering by vector threshold for global overview
  - Optimized NumPy operations for similarity computation
  - Configurable limits to prevent performance issues

### Configuration
- **Graph Settings**
  - `GRAPH_WEIGHT_VECTOR` - Vector similarity weight (default: 0.6)
  - `GRAPH_WEIGHT_TAGS` - Tag overlap weight (default: 0.3)
  - `GRAPH_WEIGHT_CLASSIFICATION` - Classification match weight (default: 0.1)
  - `GRAPH_VECTOR_MIN_SIM_THRESHOLD` - Minimum similarity threshold (default: 0.85)
  - `DEFAULT_GRAPH_NEIGHBORS` - Default neighbor limit (default: 7)
  - `GRAPH_OVERVIEW_MAX_EDGES` - Default overview edge limit (default: 50)

## [0.6.0] - 2025-01-12 - Phase 4: Vector & Hybrid Search

### Added
- **Vector Embeddings and Semantic Search**
  - `app/services/ai_core.py` - Enhanced with vector embedding generation using `nomic-ai/nomic-embed-text-v1`
  - `app/services/hybrid_search_methods.py` - Vector similarity computation and score fusion
  - `app/services/search_service.py` - Enhanced with hybrid search capabilities
  - Database migration for vector embeddings storage

- **Hybrid Search Fusion**
  - Weighted combination of keyword (FTS5) and semantic (vector) search
  - User-controllable hybrid weight parameter (0.0-1.0)
  - Score normalization using min-max scaling for fair combination
  - Transparent integration with existing search endpoint

- **Search Modes**
  - Pure keyword search (`hybrid_weight=0.0`) - Traditional FTS5 search
  - Pure semantic search (`hybrid_weight=1.0`) - Vector similarity search
  - Balanced hybrid search (`hybrid_weight=0.5`) - Default balanced approach

### Technical Implementation
- **Embedding Generation**
  - Automatic embedding creation during resource ingestion
  - Composite text generation from title, description, and subjects
  - Cross-database storage using JSON columns for portability
  - Model caching for performance optimization

- **Vector Operations**
  - NumPy-based cosine similarity computation
  - Efficient vector storage and retrieval
  - Fallback handling for missing embeddings
  - Performance optimizations for large datasets

### Configuration
- **Search Settings**
  - `EMBEDDING_MODEL_NAME` - Embedding model (default: "nomic-ai/nomic-embed-text-v1")
  - `DEFAULT_HYBRID_SEARCH_WEIGHT` - Default fusion weight (default: 0.5)
  - `EMBEDDING_CACHE_SIZE` - Model cache size (default: 1000)

### Dependencies
- Added `sentence-transformers` for embedding generation
- Updated `numpy` for vector operations
- Enhanced AI core with embedding capabilities

## [0.5.0] - 2025-01-11 - Phase 3.5: AI-Powered Asynchronous Ingestion

### Added
- **Real AI Processing**
  - `app/services/ai_core.py` - AI processing service with Hugging Face transformers
  - Intelligent summarization using `facebook/bart-large-cnn`
  - Zero-shot tagging using `facebook/bart-large-mnli`
  - Graceful fallback when AI models are unavailable

- **Asynchronous Ingestion Pipeline**
  - `POST /resources` returns immediately with `202 Accepted` status
  - Background processing using FastAPI BackgroundTasks
  - `GET /resources/{id}/status` for real-time status monitoring
  - Comprehensive error handling and recovery mechanisms

- **Enhanced Content Extraction**
  - Multi-format support for HTML, PDF, and plain text
  - Primary PDF extraction via PyMuPDF with pdfminer.six fallback
  - Content type detection based on headers, URLs, and file signatures
  - Robust error handling for network errors and timeouts

### Technical Implementation
- **AI Model Integration**
  - Lazy model loading to minimize startup time
  - CPU-only PyTorch configuration for broad compatibility
  - Model caching for performance optimization
  - Fallback logic for production reliability

- **Background Processing**
  - FastAPI BackgroundTasks for in-process async processing
  - Status tracking with timestamps and error reporting
  - Transaction-safe database updates
  - Comprehensive logging and monitoring

### Configuration
- **AI Model Settings**
  - `SUMMARIZER_MODEL` - Summarization model (default: "facebook/bart-large-cnn")
  - `TAGGER_MODEL` - Tagging model (default: "facebook/bart-large-mnli")
  - Configurable via environment variables or code injection

### Dependencies
- Added `transformers` and `torch` for AI processing
- Added `PyMuPDF` and `pdfminer.six` for PDF processing
- Enhanced content extraction capabilities

## [0.4.0] - 2025-01-10 - Phase 3: Advanced Search & Discovery

### Added
- **Full-Text Search with FTS5**
  - SQLite FTS5 contentless virtual table implementation
  - Automatic trigger synchronization with resources table
  - Search result snippets and highlighting
  - Graceful fallback to LIKE search if FTS5 unavailable

- **Faceted Search Capabilities**
  - Advanced filtering by classification, type, language, and subjects
  - Facet counts computed over filtered pre-paginated sets
  - Support for multiple filter types (any, all, range, exact)
  - Transparent integration with existing search infrastructure

- **Authority Control System**
  - `app/services/authority_service.py` - Subject normalization and canonical forms
  - `app/routers/authority.py` - Authority control endpoints
  - Built-in synonyms and smart formatting (e.g., "ML" → "Machine Learning")
  - Usage tracking and variant management

- **Personal Classification System**
  - `app/services/classification_service.py` - UDC-inspired classification system
  - `app/routers/classification.py` - Classification management endpoints
  - Rule-based keyword matching with weighted scoring
  - Hierarchical classification tree with parent-child relationships

- **Enhanced Quality Control**
  - `app/services/quality_service.py` - Multi-factor quality assessment
  - Source credibility evaluation using domain reputation
  - Content depth analysis and vocabulary richness assessment
  - Quality level classification (HIGH ≥0.8, MEDIUM ≥0.5, LOW <0.5)

### Technical Implementation
- **Database Enhancements**
  - New authority tables for subject and creator normalization
  - Classification code tables with hierarchical relationships
  - FTS5 virtual table with automatic synchronization
  - Enhanced resource model with quality scoring

- **Search Infrastructure**
  - Portable FTS5 implementation with fallback support
  - Efficient facet computation using SQL aggregation
  - Query optimization for large datasets
  - Comprehensive error handling and validation

### Configuration
- **Search Settings**
  - Configurable search limits and pagination
  - Customizable facet computation
  - FTS5 availability detection and fallback
  - Performance tuning parameters

## [0.3.0] - 2025-01-09 - Phase 2: CRUD & Curation

### Added
- **Resource Management**
  - Complete CRUD operations for resources
  - `GET /resources` with filtering, sorting, and pagination
  - `PUT /resources/{id}` for partial updates
  - `DELETE /resources/{id}` for resource removal

- **Curation Workflows**
  - `GET /curation/review-queue` for low-quality item review
  - `POST /curation/batch-update` for bulk operations
  - Quality-based filtering and sorting
  - Batch processing with transaction safety

- **Enhanced Resource Model**
  - Dublin Core metadata compliance
  - Custom fields for classification and quality
  - Audit fields with automatic timestamps
  - Cross-database compatibility

### Technical Implementation
- **Database Schema**
  - Enhanced resource table with additional fields
  - Proper indexing for performance
  - Migration system with Alembic
  - Cross-database type compatibility

- **API Design**
  - RESTful endpoint design
  - Comprehensive query parameter support
  - Structured error responses
  - OpenAPI documentation generation

## [0.2.0] - 2025-01-08 - Phase 1: Content Ingestion

### Added
- **URL Ingestion System**
  - `POST /resources` endpoint for URL submission
  - Content fetching and extraction
  - Local content archiving
  - Basic metadata extraction

- **Content Processing**
  - HTML content extraction using readability-lxml
  - Text cleaning and processing
  - Metadata extraction and validation
  - Local storage with organized archive structure

- **Database Foundation**
  - SQLAlchemy ORM setup
  - Resource model definition
  - Database session management
  - Migration system initialization

### Technical Implementation
- **Content Extraction**
  - HTTP client with timeout handling
  - HTML parsing and text extraction
  - Content type detection
  - Error handling and recovery

- **Storage System**
  - Organized archive structure by date and domain
  - Raw HTML and processed text storage
  - Metadata persistence
  - File system organization

## [0.1.0] - 2025-01-07 - Phase 0: Foundation

### Added
- **Project Foundation**
  - FastAPI application setup
  - SQLAlchemy database configuration
  - Pydantic settings management
  - Basic project structure

- **Database Models**
  - Resource model with Dublin Core fields
  - Database migrations with Alembic
  - Cross-database compatibility
  - Proper indexing and constraints

- **Configuration System**
  - Environment-based configuration
  - Pydantic settings validation
  - Database URL configuration
  - Development and production settings

### Technical Implementation
- **Architecture**
  - Clean separation of concerns
  - Dependency injection pattern
  - Modular service architecture
  - Comprehensive error handling

- **Development Tools**
  - Testing framework setup
  - Code quality tools
  - Documentation generation
  - Development server configuration

---

## Breaking Changes

### Version 0.7.1
- No breaking changes

### Version 0.7.0
- No breaking changes

### Version 0.6.0
- No breaking changes

### Version 0.5.0
- `POST /resources` now returns `202 Accepted` instead of `200 OK` for async processing
- Added `ingestion_status` field to resource model

### Version 0.4.0
- Enhanced search endpoint with new filter parameters
- Added new database tables for authority control and classification

### Version 0.3.0
- Enhanced resource model with additional fields
- Updated API response formats

### Version 0.2.0
- Initial API implementation
- No breaking changes from previous versions

### Version 0.1.0
- Initial release
- No breaking changes

## Migration Guide

### Upgrading to 0.7.1
1. Install new dependencies: `pip install -r requirements.txt`
2. Run database migrations: `alembic upgrade head`
3. No additional configuration required

### Upgrading to 0.7.0
1. Run database migrations: `alembic upgrade head`
2. No additional configuration required

### Upgrading to 0.6.0
1. Install new dependencies: `pip install sentence-transformers numpy`
2. Run database migrations: `alembic upgrade head`
3. Existing resources will generate embeddings on next update

### Upgrading to 0.5.0
1. Install AI dependencies: `pip install transformers torch`
2. Run database migrations: `alembic upgrade head`
3. Update client code to handle `202 Accepted` responses for ingestion

### Upgrading to 0.4.0
1. Run database migrations: `alembic upgrade head`
2. Update search queries to use new filter parameters
3. No breaking changes to existing functionality

## Deprecation Notices

- No current deprecations

## Security Updates

- All versions include input validation and sanitization
- SQL injection protection through SQLAlchemy ORM
- XSS protection through proper content handling
- Rate limiting planned for future releases

## Performance Improvements

### Version 0.7.1
- In-memory caching for recommendation search results
- Optimized vector operations using NumPy
- Efficient candidate processing with early termination

### Version 0.7.0
- Optimized graph computation with efficient JSON queries
- Candidate pre-filtering for performance
- Configurable limits to prevent resource exhaustion

### Version 0.6.0
- Model caching for embedding generation
- Optimized vector similarity computation
- Efficient storage and retrieval of embeddings

### Version 0.5.0
- Lazy model loading for faster startup
- Background processing for non-blocking ingestion
- Optimized content extraction pipeline

## Known Issues

### Version 0.7.1
- External search provider may be rate-limited
- Large libraries may require tuning of recommendation parameters

### Version 0.7.0
- Graph computation may be slow for very large libraries
- Memory usage increases with library size

### Version 0.6.0
- Embedding generation requires significant memory
- First-time model loading may be slow

### Version 0.5.0
- AI models require substantial memory and CPU resources
- Background processing is in-process (not distributed)

## Future Roadmap

### Version 0.8.0 (Planned)
- API key authentication and rate limiting
- Advanced analytics and reporting
- Multi-user support and permissions
- Enhanced recommendation algorithms

### Version 0.9.0 (Planned)
- Real-time collaboration features
- Mobile API optimizations
- Advanced caching strategies
- Performance monitoring and metrics

### Version 1.0.0 (Planned)
- Production-ready deployment options
- Enterprise-grade security features
- Scalable cloud deployment
- Integration with popular knowledge management tools