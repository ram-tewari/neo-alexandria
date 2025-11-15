# Neo Alexandria 2.0 Documentation

Welcome to the comprehensive documentation for Neo Alexandria 2.0, an advanced knowledge management system with AI-powered content processing, hybrid search capabilities, and personalized recommendations.

## Documentation Overview

This documentation suite provides complete coverage of Neo Alexandria 2.0's features, from basic usage to advanced development and deployment. The documentation is organized to serve different audiences and use cases.

## Quick Navigation

### For API Users
- **[API Reference](API_DOCUMENTATION.md)** - Complete endpoint documentation with examples
- **[Examples and Tutorials](EXAMPLES.md)** - Practical code samples and step-by-step guides

### For Developers
- **[Developer Guide](DEVELOPER_GUIDE.md)** - Architecture, setup, and development workflows
- **[Changelog](CHANGELOG.md)** - Version history and release notes

### For System Administrators
- **[Developer Guide - Deployment](DEVELOPER_GUIDE.md#deployment-guide)** - Production deployment instructions
- **[API Reference - Configuration](API_DOCUMENTATION.md#configuration)** - System configuration options

## Documentation Structure

### API Reference Documentation

The **[API Reference](API_DOCUMENTATION.md)** provides comprehensive documentation for all API endpoints, including:

- **Authentication and Security** - API access and security considerations
- **Endpoint Documentation** - Complete reference for all REST endpoints
- **Request/Response Formats** - Detailed data models and examples
- **Error Handling** - HTTP status codes and error response formats
- **Rate Limits** - API usage limits and best practices
- **SDK Examples** - Code samples in Python and JavaScript

**Key Features Covered:**
- Content ingestion and processing
- Advanced search with hybrid keyword/semantic capabilities
- Knowledge graph exploration and visualization
- Citation network and link intelligence
- Personalized content recommendations
- Authority control and classification systems
- Curation workflows and quality control

### Examples and Tutorials

The **[Examples and Tutorials](EXAMPLES.md)** document provides practical, working examples for:

- **Quick Start Tutorial** - Get up and running in minutes
- **Content Ingestion** - Submit and process web content
- **Search and Discovery** - Find content using various search methods
- **Knowledge Graph** - Explore relationships between resources
- **Recommendation System** - Get personalized content suggestions
- **Multi-Language Examples** - Python, JavaScript, and cURL examples
- **Advanced Use Cases** - Complex workflows and integrations
- **Error Handling** - Robust error handling patterns

**Programming Languages Covered:**
- Python with requests library
- JavaScript/Node.js with fetch API
- cURL command-line examples
- Complete client SDK implementations

### Developer Guide

The **[Developer Guide](DEVELOPER_GUIDE.md)** provides comprehensive information for developers:

- **Architecture Overview** - System design and component relationships
- **Project Structure** - Code organization and file structure
- **Development Setup** - Local development environment configuration
- **Code Architecture** - Design patterns and best practices
- **Testing Framework** - Comprehensive testing strategies
- **Deployment Guide** - Production deployment instructions
- **Contributing Guidelines** - Code standards and contribution process
- **Troubleshooting** - Common issues and solutions

**Technical Topics Covered:**
- FastAPI application architecture
- SQLAlchemy database integration
- AI model integration and processing
- Vector embeddings and semantic search
- Knowledge graph computation
- Recommendation system implementation
- Performance optimization strategies

### Changelog and Release Notes

The **[Changelog](CHANGELOG.md)** provides detailed information about:

- **Version History** - Complete release history with dates
- **Feature Additions** - New functionality and capabilities
- **Breaking Changes** - API changes that require client updates
- **Migration Guides** - Step-by-step upgrade instructions
- **Security Updates** - Security improvements and fixes
- **Performance Improvements** - Optimization and speed enhancements
- **Known Issues** - Current limitations and workarounds
- **Future Roadmap** - Planned features and improvements

**Release Information:**
- Semantic versioning (SemVer) compliance
- Detailed feature descriptions
- Technical implementation notes
- Configuration changes
- Dependency updates

## System Features

### Core Capabilities

**Content Management**
- Asynchronous URL ingestion with AI processing
- Multi-format content extraction (HTML, PDF, text)
- Intelligent summarization and tagging
- Quality assessment and scoring
- Local content archiving

**Search and Discovery**
- Hybrid keyword and semantic search
- Vector embeddings for semantic similarity
- Faceted search with advanced filtering
- Full-text search with SQLite FTS5
- Configurable search weights and modes

**Knowledge Graph**
- Relationship detection between resources
- Multi-signal scoring (vector, subject, classification)
- Mind-map neighbor discovery
- Global relationship overview
- Transparent connection reasoning

**Personalized Recommendations**
- User profile generation from library content
- External content discovery and sourcing
- Cosine similarity-based relevance scoring
- Explainable recommendation reasoning
- Configurable recommendation parameters

**Citation Network & Link Intelligence**
- Multi-format citation extraction (HTML, PDF, Markdown)
- Internal citation resolution and linking
- PageRank-style importance scoring
- Citation graph visualization
- Smart citation type classification

**Authority Control**
- Subject normalization and canonical forms
- Creator and publisher standardization
- Usage tracking and variant management
- Built-in synonyms and smart formatting

**Classification System**
- UDC-inspired hierarchical classification
- Rule-based keyword matching
- Automatic classification assignment
- Hierarchical tree management

### Technical Architecture

**API-First Design**
- RESTful API with OpenAPI documentation
- FastAPI framework with automatic validation
- Comprehensive error handling and status codes
- Rate limiting and security considerations

**Database Integration**
- SQLAlchemy ORM with cross-database support
- SQLite for development, PostgreSQL for production
- Alembic migrations for schema management
- Optimized queries and indexing

**AI and Machine Learning**
- Hugging Face transformers for NLP tasks
- Vector embeddings for semantic search
- Model caching and performance optimization
- Graceful fallback when AI services unavailable

**Performance and Scalability**
- Asynchronous processing for heavy operations
- In-memory caching for frequently accessed data
- Efficient vector operations using NumPy
- Configurable limits and thresholds

## Getting Started

### Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r backend/requirements.txt
   ```

2. **Run Database Migrations**
   ```bash
   cd backend && alembic upgrade head
   ```

3. **Start the Server**
   ```bash
   uvicorn backend.app.main:app --reload
   ```

4. **Ingest Your First Resource**
   ```bash
   curl -X POST http://127.0.0.1:8000/resources \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com/article"}'
   ```

5. **Search Your Content**
   ```bash
   curl -X POST http://127.0.0.1:8000/search \
     -H "Content-Type: application/json" \
     -d '{"text": "your search query", "limit": 10}'
   ```

### Next Steps

- **Explore the API** - Use the [API Reference](API_DOCUMENTATION.md) to understand all available endpoints
- **Try Examples** - Follow the [Examples and Tutorials](EXAMPLES.md) for practical usage
- **Develop Integrations** - Use the [Developer Guide](DEVELOPER_GUIDE.md) for custom development
- **Stay Updated** - Check the [Changelog](CHANGELOG.md) for new features and updates

## Support and Community

### Documentation Issues
- Report documentation problems via GitHub Issues
- Suggest improvements and clarifications
- Contribute examples and tutorials

### Technical Support
- GitHub Issues for bug reports and feature requests
- Community discussions and Q&A
- Developer collaboration and contributions

### Contributing
- Follow the contributing guidelines in the [Developer Guide](DEVELOPER_GUIDE.md)
- Submit pull requests for documentation improvements
- Share examples and use cases with the community

## Version Information

**Current Version:** 0.8.0 (Phase 6)
**Latest Features:** Citation Network & Link Intelligence
**Documentation Version:** Updated for all phases through 6

**Supported Phases:**
- Phase 0: Foundation and infrastructure
- Phase 1: Content ingestion
- Phase 2: CRUD operations and curation
- Phase 3: Advanced search and discovery
- Phase 3.5: AI-powered asynchronous processing
- Phase 4: Vector embeddings and hybrid search
- Phase 5: Hybrid knowledge graph
- Phase 5.5: Personalized recommendations
- Phase 6: Citation network and link intelligence
- Phase 9: Multi-dimensional quality assessment ✅

## Phase 9: Multi-Dimensional Quality Assessment

Phase 9 introduces a sophisticated quality assessment framework that evaluates resources across multiple dimensions and provides automated quality monitoring.

### Quick Start Guide

**1. Compute Quality for a Resource**
```bash
curl -X POST http://127.0.0.1:8000/quality/recalculate \
  -H "Content-Type: application/json" \
  -d '{"resource_id": "550e8400-e29b-41d4-a716-446655440000"}'
```

**2. Get Quality Details**
```bash
curl http://127.0.0.1:8000/resources/550e8400-e29b-41d4-a716-446655440000/quality-details
```

**3. Find Quality Outliers**
```bash
curl http://127.0.0.1:8000/quality/outliers?limit=20
```

**4. Monitor Quality Degradation**
```bash
curl http://127.0.0.1:8000/quality/degradation?time_window_days=30
```

**5. Evaluate Summary Quality**
```bash
curl -X POST http://127.0.0.1:8000/summaries/550e8400-e29b-41d4-a716-446655440000/evaluate?use_g_eval=false
```

### Quality Dimensions

Resources are assessed across five independent dimensions:

**Accuracy (30% default weight)**
- Citation validity from Phase 6 citation data
- Source credibility based on domain reputation (.edu, .gov, .org, arxiv.org, doi.org)
- Scholarly metadata presence (DOI, PMID, arXiv ID)
- Author information completeness

**Completeness (25% default weight)**
- Required fields: title, content, url
- Important fields: summary, tags, authors, publication_year
- Scholarly fields: doi, journal, affiliations, funding_sources
- Multi-modal content: equations, tables, figures

**Consistency (20% default weight)**
- Title-content alignment using keyword overlap
- Summary-content alignment using semantic similarity
- Internal coherence without contradictions

**Timeliness (15% default weight)**
- Publication recency with 20-year decay function
- Ingestion recency bonus for recently added content
- Content freshness indicators

**Relevance (10% default weight)**
- Classification confidence from Phase 8.5 ML classification
- Citation count using logarithmic scaling from Phase 6
- Topical alignment with user interests

### Summarization Evaluation Metrics

Summaries are evaluated using state-of-the-art metrics:

**G-Eval (LLM-based evaluation using GPT-4)**
- **Coherence**: Logical flow and structure (1-5 scale)
- **Consistency**: Factual alignment with source document (1-5 scale)
- **Fluency**: Grammatical correctness and readability (1-5 scale)
- **Relevance**: Key information capture (1-5 scale)

**FineSurE (Fine-grained summarization evaluation)**
- **Completeness**: Coverage of key information from reference (0.0-1.0)
- **Conciseness**: Information density with optimal 5-15% compression ratio (0.0-1.0)

**BERTScore (Semantic similarity)**
- **F1 Score**: Token-level semantic similarity using BERT embeddings (0.0-1.0)
- Model: microsoft/deberta-xlarge-mnli for high accuracy

**Composite Score**: Weighted average of all metrics
- Coherence 20%, Consistency 20%, Fluency 15%, Relevance 15%, Completeness 15%, Conciseness 5%, BERTScore 10%

### Automated Quality Monitoring

**Outlier Detection**
- Uses Isolation Forest algorithm to detect anomalous quality scores
- Processes resources in batches (default 1000)
- Identifies specific outlier reasons (low accuracy, low completeness, etc.)
- Automatically flags resources for human review

**Quality Degradation Monitoring**
- Compares historical quality scores to detect degradation over time
- Configurable time window (default 30 days)
- Detects 20% quality drops indicating content issues
- Identifies broken links, outdated content, metadata corruption

**Scheduled Tasks**
- Daily outlier detection to maintain quality standards
- Weekly degradation monitoring to catch content issues
- Automatic review queue population for curator attention

### Custom Quality Weights

Adjust dimension weights for domain-specific priorities:

**Academic Research**
```json
{
  "accuracy": 0.40,
  "completeness": 0.30,
  "consistency": 0.15,
  "timeliness": 0.10,
  "relevance": 0.05
}
```

**News/Current Events**
```json
{
  "accuracy": 0.25,
  "completeness": 0.15,
  "consistency": 0.15,
  "timeliness": 0.35,
  "relevance": 0.10
}
```

**Educational Content**
```json
{
  "accuracy": 0.30,
  "completeness": 0.20,
  "consistency": 0.25,
  "timeliness": 0.10,
  "relevance": 0.15
}
```

### Integration with Recommendations

Quality scores enhance the recommendation system:
- Filters out low-quality resources (quality_overall < 0.5)
- Excludes quality outliers from recommendations
- Applies 20% boost to high-quality resources (quality_overall > 0.8)
- Weights recommendations by quality scores

### Performance Characteristics

- **Quality Computation**: <1 second per resource (excluding G-Eval)
- **G-Eval Evaluation**: <10 seconds per resource (OpenAI API latency)
- **Outlier Detection**: <30 seconds for 1000 resources
- **Batch Processing**: 100 resources/minute throughput

## License and Legal

This documentation is part of the Neo Alexandria 2.0 project and is subject to the same license terms. See the main project repository for license information.

---

**Last Updated:** November 14, 2025
**Documentation Version:** 1.2.0
**API Version:** 1.2.0