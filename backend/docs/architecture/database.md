# Database Architecture

Database schema, models, and migration strategies for Neo Alexandria 2.0.

## Database Support

Neo Alexandria supports both SQLite and PostgreSQL with automatic detection.

### SQLite (Development)

```bash
DATABASE_URL=sqlite:///./backend.db
```

**Use Cases:**
- Local development and prototyping
- Single-user deployments
- Testing and CI/CD pipelines
- Small datasets (<10,000 resources)

**Advantages:**
- Zero configuration
- File-based (portable)
- No separate server needed

**Limitations:**
- Single writer (limited concurrency)
- No advanced indexing (GIN, JSONB)

### PostgreSQL (Production)

```bash
DATABASE_URL=postgresql://user:password@host:5432/database
```

**Use Cases:**
- Production deployments
- Multi-user environments
- High concurrency (100+ users)
- Large datasets (>10,000 resources)

**Advantages:**
- Excellent concurrent write performance
- Advanced indexing (GIN for JSONB)
- Native JSONB support
- Connection pooling

---

## Database Model Hierarchy

```
                    ┌─────────────────────┐
                    │   SQLAlchemy Base   │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┬────────────────┐
              │                │                │                │
    ┌─────────▼────────┐  ┌───▼──────────┐  ┌─▼──────────┐  ┌──▼─────────┐
    │    Resource      │  │ TaxonomyNode │  │ Collection │  │ Annotation │
    ├──────────────────┤  ├──────────────┤  ├────────────┤  ├────────────┤
    │ • id: UUID       │  │ • id: UUID   │  │ • id: UUID │  │ • id: UUID │
    │ • title: str     │  │ • code: str  │  │ • name     │  │ • content  │
    │ • description    │  │ • name: str  │  │ • owner_id │  │ • user_id  │
    │ • creator        │  │ • parent_id  │  │ • public   │  │ • type     │
    │ • subject: JSON  │  │ • level: int │  └────────────┘  └────────────┘
    │ • type           │  └──────────────┘
    │ • language       │         │
    │ • identifier     │         │ self-referential
    │ • doi            │         ▼
    │ • embedding      │  ┌──────────────┐
    │ • created_at     │  │   children   │
    │ • updated_at     │  │  (List[Node])│
    └──────────────────┘  └──────────────┘
            │
            │ one-to-many
            ▼
    ┌──────────────────┐
    │ ResourceTaxonomy │
    ├──────────────────┤
    │ • resource_id    │
    │ • taxonomy_id    │
    │ • confidence     │
    │ • method         │
    └──────────────────┘
```

---

## Core Schema

### Resource Model

```
┌──────────────────────────────────────────────────────────────────┐
│                         Resource                                 │
├──────────────────────────────────────────────────────────────────┤
│ id: UUID (PK)                                                    │
│ title: String (required)                                         │
│ description: Text                                                │
│ creator: String                                                  │
│ publisher: String                                                │
│ source: String (URL)                                             │
│ language: String                                                 │
│ type: String                                                     │
│ subject: JSON (array of strings)                                 │
│ classification_code: String                                      │
│ quality_score: Float (0.0-1.0)                                   │
│ read_status: Enum (unread, in_progress, completed, archived)     │
│ embedding: JSON (vector array)                                   │
│ created_at: DateTime                                             │
│ updated_at: DateTime                                             │
└──────────────────────────────────────────────────────────────────┘
```

### Collection Model

```
┌──────────────────────────────────────────────────────────────────┐
│                         Collection                               │
├──────────────────────────────────────────────────────────────────┤
│ id: UUID (PK)                                                    │
│ name: String (1-255 chars)                                       │
│ description: Text (max 2000 chars)                               │
│ owner_id: String (indexed)                                       │
│ visibility: Enum (private, shared, public)                       │
│ parent_id: UUID (FK → Collection, nullable)                      │
│ embedding: JSON (aggregate vector)                               │
│ created_at: DateTime                                             │
│ updated_at: DateTime                                             │
└──────────────────────────────────────────────────────────────────┘
```

### Annotation Model

```
┌──────────────────────────────────────────────────────────────────┐
│                         Annotation                               │
├──────────────────────────────────────────────────────────────────┤
│ id: UUID (PK)                                                    │
│ resource_id: UUID (FK → Resource)                                │
│ user_id: String                                                  │
│ start_offset: Integer                                            │
│ end_offset: Integer                                              │
│ highlighted_text: Text                                           │
│ note: Text (max 10,000 chars)                                    │
│ tags: JSON (array, max 20)                                       │
│ color: String (hex)                                              │
│ embedding: JSON (384-dim vector)                                 │
│ is_shared: Boolean                                               │
│ created_at: DateTime                                             │
│ updated_at: DateTime                                             │
└──────────────────────────────────────────────────────────────────┘
```

### Taxonomy Node Model

```
┌──────────────────────────────────────────────────────────────────┐
│                       TaxonomyNode                               │
├──────────────────────────────────────────────────────────────────┤
│ id: UUID (PK)                                                    │
│ name: String                                                     │
│ slug: String (unique)                                            │
│ parent_id: UUID (FK → TaxonomyNode, nullable)                    │
│ level: Integer                                                   │
│ path: String (materialized path)                                 │
│ description: Text                                                │
│ keywords: JSON (array)                                           │
│ resource_count: Integer                                          │
│ descendant_resource_count: Integer                               │
│ is_leaf: Boolean                                                 │
│ allow_resources: Boolean                                         │
│ created_at: DateTime                                             │
│ updated_at: DateTime                                             │
└──────────────────────────────────────────────────────────────────┘
```

### Citation Model

```
┌──────────────────────────────────────────────────────────────────┐
│                         Citation                                 │
├──────────────────────────────────────────────────────────────────┤
│ id: UUID (PK)                                                    │
│ source_resource_id: UUID (FK → Resource)                         │
│ target_resource_id: UUID (FK → Resource)                         │
│ citation_type: String (cites, cited_by, related)                 │
│ context: Text (surrounding text)                                 │
│ confidence: Float (0.0-1.0)                                      │
│ created_at: DateTime                                             │
└──────────────────────────────────────────────────────────────────┘
```

### User Interaction Model

```
┌──────────────────────────────────────────────────────────────────┐
│                      UserInteraction                             │
├──────────────────────────────────────────────────────────────────┤
│ id: UUID (PK)                                                    │
│ user_id: String (indexed)                                        │
│ resource_id: UUID (FK → Resource)                                │
│ interaction_type: String (view, bookmark, rate, download)        │
│ rating: Integer (1-5, nullable)                                  │
│ duration_seconds: Integer (nullable)                             │
│ metadata: JSON                                                   │
│ created_at: DateTime                                             │
└──────────────────────────────────────────────────────────────────┘
```

---

## Association Tables

### Collection-Resource Association

```sql
CREATE TABLE collection_resources (
    collection_id UUID REFERENCES collections(id) ON DELETE CASCADE,
    resource_id UUID REFERENCES resources(id) ON DELETE CASCADE,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (collection_id, resource_id)
);

CREATE INDEX idx_collection_resources_collection ON collection_resources(collection_id);
CREATE INDEX idx_collection_resources_resource ON collection_resources(resource_id);
```

### Resource-Taxonomy Association

```sql
CREATE TABLE resource_taxonomy (
    resource_id UUID REFERENCES resources(id) ON DELETE CASCADE,
    taxonomy_id UUID REFERENCES taxonomy_nodes(id) ON DELETE CASCADE,
    confidence FLOAT,
    is_predicted BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (resource_id, taxonomy_id)
);
```

---

## Connection Pool Configuration

### PostgreSQL

```python
postgresql_params = {
    'pool_size': 20,              # Base connections
    'max_overflow': 40,           # Burst connections
    'pool_recycle': 3600,         # Recycle after 1 hour
    'pool_pre_ping': True,        # Validate before use
}
```

### SQLite

```python
sqlite_params = {
    'pool_size': 5,
    'max_overflow': 10,
    'connect_args': {
        'check_same_thread': False,
        'timeout': 30
    }
}
```

---

## Database Layer Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       DATABASE LAYER                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    Shared Kernel (app/shared/)                   │   │
│  │                                                                  │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │   │
│  │  │   database.py   │  │  base_model.py  │  │   event_bus.py  │   │   │
│  │  │                 │  │                 │  │                 │   │   │
│  │  │ • get_db()      │  │ • BaseModel     │  │ • publish()     │   │   │
│  │  │ • SessionLocal  │  │   - id (GUID)   │  │ • subscribe()   │   │   │
│  │  │ • engine        │  │   - created_at  │  │ • Event class   │   │   │
│  │  │ • Base          │  │   - updated_at  │  │                 │   │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│                                    │ used by                            │
│                                    ▼                                    │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    Module Models                                 │   │
│  │                                                                  │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │   │
│  │  │ resources/      │  │ collections/    │  │ search/         │   │   │
│  │  │   model.py      │  │   model.py      │  │   (uses shared) │   │   │
│  │  │                 │  │                 │  │                 │   │   │
│  │  │ • Resource      │  │ • Collection    │  │ • FTS5 tables   │   │   │
│  │  │ • Annotation    │  │ • CollectionRes │  │ • Vector index  │   │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Migration Commands

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Check current version
alembic current
```

## Database Migration (SQLite ↔ PostgreSQL)

### SQLite → PostgreSQL

```bash
python backend/scripts/migrate_sqlite_to_postgresql.py \
  --source sqlite:///./backend.db \
  --target postgresql://user:pass@host:5432/db \
  --validate
```

### PostgreSQL → SQLite

```bash
python backend/scripts/migrate_postgresql_to_sqlite.py \
  --source postgresql://user:pass@host:5432/db \
  --target sqlite:///./backend.db \
  --validate
```

---

## Backup Strategies

### PostgreSQL

```bash
# Full backup
pg_dump -h localhost -U postgres -d neo_alexandria > backup.sql

# Compressed backup
pg_dump -h localhost -U postgres -d neo_alexandria | gzip > backup.sql.gz
```

### SQLite

```bash
# Simple copy
cp backend.db backend.db.backup

# SQLite backup command
sqlite3 backend.db ".backup 'backup.db'"
```

---

## Related Documentation

- [Architecture Overview](overview.md) - System design
- [PostgreSQL Migration Guide](../POSTGRESQL_MIGRATION_GUIDE.md) - Detailed migration
- [PostgreSQL Backup Guide](../POSTGRESQL_BACKUP_GUIDE.md) - Backup procedures
