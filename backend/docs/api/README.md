# API Reference

Complete API documentation for Neo Alexandria 2.0.

## Module-Based Architecture

Neo Alexandria 2.0 uses a modular architecture where each domain is implemented as a self-contained vertical slice. Each module has its own router, service, schemas, models, and event handlers.

## Quick Links

| Module | Description | File |
|--------|-------------|------|
| Overview | Auth, errors, pagination, module architecture | [overview.md](overview.md) |
| Resources | Content management and ingestion | [resources.md](resources.md) |
| Search | Hybrid search with vector and FTS | [search.md](search.md) |
| Collections | Collection management and sharing | [collections.md](collections.md) |
| Annotations | Active reading with highlights and notes | [annotations.md](annotations.md) |
| Taxonomy | ML classification and taxonomy trees | [taxonomy.md](taxonomy.md) |
| Graph | Knowledge graph, citations, and discovery | [graph.md](graph.md) |
| Recommendations | Hybrid recommendation engine | [recommendations.md](recommendations.md) |
| Quality | Multi-dimensional quality assessment | [quality.md](quality.md) |
| Scholarly | Academic metadata extraction | [scholarly.md](scholarly.md) |
| Authority | Subject authority and classification | [authority.md](authority.md) |
| Curation | Content review and batch operations | [curation.md](curation.md) |
| Monitoring | System health and metrics | [monitoring.md](monitoring.md) |

## Getting Started

1. Read [overview.md](overview.md) for API basics and module architecture
2. Check [resources.md](resources.md) for content ingestion
3. Explore [search.md](search.md) for discovery features
4. Review module structure sections in each API doc for import examples

## Module Structure

Each module follows a consistent structure:

```
app/modules/{module_name}/
├── __init__.py       # Public interface exports
├── router.py         # FastAPI endpoints
├── service.py        # Business logic
├── schema.py         # Pydantic models
├── model.py          # SQLAlchemy models
├── handlers.py       # Event handlers
└── README.md         # Module documentation
```

### Importing from Modules

```python
# Import from specific modules
from app.modules.resources import ResourceService, ResourceCreate
from app.modules.search import SearchService, SearchRequest
from app.modules.collections import CollectionService

# Import from shared kernel
from app.shared.embeddings import EmbeddingService
from app.shared.ai_core import AICore
from app.shared.database import get_db
from app.shared.event_bus import event_bus
```

## API Design Principles

- **RESTful** - Standard HTTP methods and status codes
- **JSON** - All requests and responses use JSON
- **Modular** - Self-contained modules with clear boundaries
- **Event-Driven** - Modules communicate via event bus
- **Pagination** - Large result sets are paginated
- **Filtering** - Flexible filtering on list endpoints
- **Versioning** - API versioning (planned for v2)

## Interactive Documentation

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## Related Documentation

- [Architecture: Modules](../architecture/modules.md) - Vertical slice architecture
- [Architecture: Events](../architecture/events.md) - Event system
- [Architecture Overview](../architecture/overview.md) - System design
- [Developer Guides](../guides/) - Development workflows
- [Steering Docs](../../../.kiro/steering/) - Project context
