# Neo Alexandria 2.0 Documentation

Welcome to the Neo Alexandria 2.0 documentation hub. This documentation follows a modular structure for easy navigation and maintenance.

## Quick Start

- **New to Neo Alexandria?** Start with [Setup Guide](guides/setup.md)
- **Need API reference?** Check [API Overview](api/overview.md)
- **Understanding the architecture?** Read [Architecture Overview](architecture/overview.md)
- **Development workflows?** See [Developer Workflows](guides/workflows.md)

## Documentation Structure

### 📚 Core Documentation

- **[index.md](index.md)** - Documentation navigation hub
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and release notes

### 🔌 API Reference

Modular API documentation organized by domain:

- **[api/overview.md](api/overview.md)** - Base URL, authentication, error handling
- **[api/resources.md](api/resources.md)** - Resource CRUD operations
- **[api/search.md](api/search.md)** - Search and hybrid search
- **[api/collections.md](api/collections.md)** - Collection management
- **[api/annotations.md](api/annotations.md)** - Annotation and highlighting
- **[api/taxonomy.md](api/taxonomy.md)** - Taxonomy and classification
- **[api/graph.md](api/graph.md)** - Knowledge graph and citations
- **[api/recommendations.md](api/recommendations.md)** - Recommendation engine
- **[api/quality.md](api/quality.md)** - Quality assessment
- **[api/scholarly.md](api/scholarly.md)** - Scholarly metadata
- **[api/authority.md](api/authority.md)** - Authority control
- **[api/curation.md](api/curation.md)** - Content curation
- **[api/monitoring.md](api/monitoring.md)** - Health and monitoring

### 🏗️ Architecture

System architecture and design decisions:

- **[architecture/overview.md](architecture/overview.md)** - High-level system architecture
- **[architecture/database.md](architecture/database.md)** - Schema, models, migrations
- **[architecture/event-system.md](architecture/event-system.md)** - Event bus and handlers
- **[architecture/events.md](architecture/events.md)** - Event catalog and patterns
- **[architecture/modules.md](architecture/modules.md)** - Vertical slice module structure
- **[architecture/decisions.md](architecture/decisions.md)** - Architecture decision records

### 📖 Developer Guides

Step-by-step guides for common tasks:

- **[guides/setup.md](guides/setup.md)** - Installation and environment setup
- **[guides/workflows.md](guides/workflows.md)** - Common development tasks
- **[guides/testing.md](guides/testing.md)** - Testing strategies and patterns
- **[guides/deployment.md](guides/deployment.md)** - Docker and production deployment
- **[guides/troubleshooting.md](guides/troubleshooting.md)** - Common issues and FAQ

### 🗄️ Database & Migration

- **[POSTGRESQL_MIGRATION_GUIDE.md](POSTGRESQL_MIGRATION_GUIDE.md)** - SQLite to PostgreSQL migration
- **[POSTGRESQL_BACKUP_GUIDE.md](POSTGRESQL_BACKUP_GUIDE.md)** - Backup and recovery procedures
- **[SQLITE_COMPATIBILITY_MAINTENANCE.md](SQLITE_COMPATIBILITY_MAINTENANCE.md)** - SQLite compatibility guide
- **[TRANSACTION_ISOLATION_GUIDE.md](TRANSACTION_ISOLATION_GUIDE.md)** - Transaction management

### 🔄 Migration & Refactoring

- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - General migration procedures
- **[EVENT_DRIVEN_REFACTORING.md](EVENT_DRIVEN_REFACTORING.md)** - Event architecture migration
- **[MODULE_ISOLATION_VALIDATION.md](MODULE_ISOLATION_VALIDATION.md)** - Module isolation rules

### 📦 Legacy Documentation

Historical documentation and summaries (archived):

- **[archive/](archive/)** - Legacy docs, summaries, and historical records

## Documentation Hierarchy

```
Level 1: Quick Reference
├── AGENTS.md (root) - Agent routing rules
├── .kiro/steering/product.md - Product overview
├── .kiro/steering/tech.md - Tech stack
└── .kiro/steering/structure.md - Repository map

Level 2: Feature Specs
├── .kiro/specs/[feature]/requirements.md - What to build
├── .kiro/specs/[feature]/design.md - How to build it
└── .kiro/specs/[feature]/tasks.md - Implementation steps

Level 3: Technical Details (this directory)
├── index.md - Documentation hub
├── api/*.md - API reference (13 domain files)
├── architecture/*.md - Architecture docs (6 files)
├── guides/*.md - Developer guides (5 files)
└── *.md - Specialized guides

Level 4: Implementation
├── backend/app/modules/[module]/README.md - Module docs
└── backend/app/modules/[module]/*.py - Implementation
```

## Finding What You Need

### "Where is the API for X?"
1. Check [index.md](index.md) for navigation
2. Check [api/overview.md](api/overview.md) for domain list
3. Find specific endpoint in [api/[domain].md](api/)

### "How does feature X work?"
1. Check `.kiro/specs/[feature]/design.md` for architecture
2. Check [architecture/overview.md](architecture/overview.md) for system context
3. Check implementation in `backend/app/modules/[module]/`

### "What are the requirements for X?"
1. Check `.kiro/specs/[feature]/requirements.md` for user stories
2. Check [api/[domain].md](api/) for API contracts

### "How do I implement X?"
1. Check `.kiro/specs/[feature]/tasks.md` for implementation steps
2. Check [guides/workflows.md](guides/workflows.md) for development workflows
3. Check existing implementations in `backend/app/modules/` for patterns

### "What tests exist for X?"
1. Check `backend/tests/modules/` for module-specific tests
2. Check `backend/tests/integration/` for integration tests
3. Check `backend/tests/conftest.py` for test fixtures

### "How do modules communicate?"
1. Check [architecture/event-system.md](architecture/event-system.md) for event bus details
2. Check [architecture/events.md](architecture/events.md) for event catalog
3. Check `backend/app/modules/[module]/handlers.py` for event handlers

## Current Status

### Architecture (Phase 13.5 + Phase 14)
- ✅ 13 self-contained vertical slice modules
- ✅ Event-driven communication with <1ms latency
- ✅ Zero circular dependencies
- ✅ 97 API routes across all modules
- ✅ Shared kernel for cross-cutting concerns
- ✅ PostgreSQL production support
- ✅ Comprehensive test suite

### Documentation (Current)
- ✅ Modular API documentation (13 domain files)
- ✅ Architecture documentation (6 files)
- ✅ Developer guides (5 files)
- ✅ Specialized guides (database, migration, etc.)
- ✅ Steering documentation for AI agents

## Contributing to Documentation

When updating documentation:

1. **API docs**: Update the specific domain file in `api/`
2. **Architecture**: Update relevant file in `architecture/`
3. **Guides**: Update specific guide in `guides/`
4. **Changelog**: Add entry to `CHANGELOG.md`
5. **Index**: Update `index.md` if adding new docs

## Related Documentation

- [Project Root README](../../README.md) - Project overview
- [Backend README](../README.md) - Backend-specific information
- [Steering Docs](../../.kiro/steering/) - High-level context for AI agents
- [Spec Organization](../../.kiro/specs/README.md) - Feature specifications

## Need Help?

- Check [guides/troubleshooting.md](guides/troubleshooting.md) for common issues
- Review [architecture/overview.md](architecture/overview.md) for system understanding
- Consult [guides/workflows.md](guides/workflows.md) for development tasks
- Ask in team discussions or create a GitHub issue
