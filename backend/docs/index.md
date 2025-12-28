# Backend Documentation Index

## Quick Navigation

| Need | Read |
|------|------|
| API endpoints | [API Reference](api/) |
| System architecture | [Architecture](architecture/) |
| Development setup | [Developer Guides](guides/) |
| Database info | [Architecture: Database](architecture/database.md) |
| Testing | [Guides: Testing](guides/testing.md) |

## Documentation Structure

```
backend/docs/
├── index.md                    # This file
├── api/                        # API Reference (split by domain/module)
│   ├── overview.md             # Auth, errors, base URLs, module architecture
│   ├── resources.md            # Resource management endpoints
│   ├── search.md               # Search endpoints (hybrid, vector, FTS)
│   ├── collections.md          # Collection management
│   ├── annotations.md          # Annotation system
│   ├── taxonomy.md             # Taxonomy & classification
│   ├── graph.md                # Knowledge graph & citations
│   ├── recommendations.md      # Recommendation engine
│   ├── quality.md              # Quality assessment
│   ├── scholarly.md            # Academic metadata extraction
│   ├── authority.md            # Subject authority
│   ├── curation.md             # Content review
│   └── monitoring.md           # Monitoring & health checks
├── architecture/               # System Architecture
│   ├── overview.md             # High-level system design
│   ├── database.md             # Database schema & models
│   ├── event-system.md         # Event-driven architecture
│   ├── events.md               # Event catalog
│   ├── modules.md              # Vertical slice modules
│   └── decisions.md            # Architectural Decision Records (ADRs)
└── guides/                     # Developer Guides
    ├── setup.md                # Installation & environment
    ├── workflows.md            # Common development tasks
    ├── testing.md              # Testing strategies
    ├── deployment.md           # Docker & production
    └── troubleshooting.md      # Common issues & solutions
```

## API Reference

Complete REST API documentation organized by module:

- [API Overview](api/overview.md) - Authentication, errors, pagination, module architecture
- [Resources API](api/resources.md) - Content management and ingestion
- [Search API](api/search.md) - Hybrid search, three-way fusion
- [Collections API](api/collections.md) - Collection management
- [Annotations API](api/annotations.md) - Text highlighting and notes
- [Taxonomy API](api/taxonomy.md) - Classification and ML
- [Graph API](api/graph.md) - Knowledge graph and citations
- [Recommendations API](api/recommendations.md) - Personalized content
- [Quality API](api/quality.md) - Quality assessment
- [Scholarly API](api/scholarly.md) - Academic metadata extraction
- [Authority API](api/authority.md) - Subject authority and classification
- [Curation API](api/curation.md) - Content review and batch operations
- [Monitoring API](api/monitoring.md) - Health checks and metrics

## Architecture

System design and technical decisions:

- [Architecture Overview](architecture/overview.md) - High-level system design and module structure
- [Database](architecture/database.md) - Schema, models, migrations
- [Event System](architecture/event-system.md) - Event-driven communication patterns
- [Event Catalog](architecture/events.md) - Complete event reference
- [Modules](architecture/modules.md) - Vertical slice architecture
- [Design Decisions](architecture/decisions.md) - ADRs

## Developer Guides

Getting started and development workflows:

- [Setup Guide](guides/setup.md) - Installation and configuration
- [Development Workflows](guides/workflows.md) - Common tasks
- [Testing Guide](guides/testing.md) - Running and writing tests
- [Deployment Guide](guides/deployment.md) - Docker and production
- [Troubleshooting](guides/troubleshooting.md) - Common issues

## Interactive Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## Related Documentation

- [Steering Docs](../../.kiro/steering/) - High-level project context
- [Spec Organization](../../.kiro/specs/) - Feature specifications
- [Frontend Docs](../../frontend/README.md) - Frontend documentation
