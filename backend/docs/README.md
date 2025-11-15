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
- Phase 6: Citation network and link intelligence ✅

## License and Legal

This documentation is part of the Neo Alexandria 2.0 project and is subject to the same license terms. See the main project repository for license information.

---

**Last Updated:** November 9, 2025
**Documentation Version:** 1.1.0
**API Version:** 0.8.0