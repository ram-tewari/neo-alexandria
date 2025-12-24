# Architecture Documentation

System architecture and design documentation for Neo Alexandria 2.0.

## Quick Links

| Topic | Description | File |
|-------|-------------|------|
| Overview | High-level system design | [overview.md](overview.md) |
| Database | Schema, models, migrations | [database.md](database.md) |
| Event System | Event-driven architecture | [event-system.md](event-system.md) |
| Modules | Vertical slice architecture | [modules.md](modules.md) |
| Decisions | Architectural Decision Records | [decisions.md](decisions.md) |

## Architecture Principles

1. **Modular Monolith** - Vertical slices with clear boundaries
2. **Event-Driven** - Loose coupling via event bus
3. **Domain-Driven** - Rich domain models
4. **API-First** - All features accessible via REST API
5. **Database Agnostic** - Support SQLite and PostgreSQL

## System Layers

```
┌─────────────────────────────────────┐
│         API Layer (FastAPI)         │
│  Routers → Schemas → Validation     │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│      Service Layer (Business)       │
│  Services → Domain Objects          │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│     Data Layer (Persistence)        │
│  SQLAlchemy → Database              │
└─────────────────────────────────────┘
```

## Key Components

- **Modules** - Self-contained vertical slices (collections, resources, search)
- **Services** - Shared business logic (embedding, ML, quality)
- **Events** - Decoupled communication between modules
- **Domain** - Rich domain objects and business rules

## Migration Status

### Completed
- ✅ Event-driven architecture (Phase 12.5)
- ✅ PostgreSQL support (Phase 13)
- ✅ Vertical slice modules (Phase 13.5 - Partial)

### In Progress
- 🔄 Complete vertical slice migration
- 🔄 Module isolation improvements

### Planned
- 📋 API versioning
- 📋 GraphQL support
- 📋 Microservices extraction (if needed)

## Related Documentation

- [API Reference](../api/) - API endpoints
- [Developer Guides](../guides/) - Development workflows
- [Steering: Tech](../../../.kiro/steering/tech.md) - Tech stack
