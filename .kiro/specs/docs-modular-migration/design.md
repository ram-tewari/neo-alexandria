# Design Document

## Overview

This design document describes the approach for migrating Neo Alexandria 2.0's monolithic documentation into a modular, topic-focused structure. The migration transforms three large source files (~140KB total) into 20+ focused destination files organized by domain.

## Architecture

### Source to Destination Mapping

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DOCUMENTATION MIGRATION FLOW                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  SOURCE FILES                          DESTINATION STRUCTURE            │
│  ────────────                          ─────────────────────            │
│                                                                         │
│  API_DOCUMENTATION.md ──────────────►  backend/docs/api/                │
│  (~132KB)                              ├── overview.md                  │
│                                        ├── resources.md                 │
│                                        ├── search.md                    │
│                                        ├── collections.md               │
│                                        ├── annotations.md               │
│                                        ├── taxonomy.md                  │
│                                        ├── graph.md                     │
│                                        ├── recommendations.md           │
│                                        ├── quality.md                   │
│                                        └── monitoring.md                │
│                                                                         │
│  ARCHITECTURE_DIAGRAM.md ───────────►  backend/docs/architecture/       │
│  (~4200 lines)                         ├── overview.md                  │
│                                        ├── database.md                  │
│                                        ├── event-system.md              │
│                                        ├── modules.md                   │
│                                        └── decisions.md                 │
│                                                                         │
│  DEVELOPER_GUIDE.md ────────────────►  backend/docs/guides/             │
│  (~large)                              ├── setup.md                     │
│                                        ├── workflows.md                 │
│                                        ├── testing.md                   │
│                                        ├── deployment.md                │
│                                        └── troubleshooting.md           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### File Structure After Migration

```
backend/docs/
├── index.md                    # Navigation hub (updated)
├── api/
│   ├── README.md               # API section overview
│   ├── overview.md             # Base URL, auth, errors, pagination
│   ├── resources.md            # /resources/* endpoints
│   ├── search.md               # /search/* endpoints
│   ├── collections.md          # /collections/* endpoints
│   ├── annotations.md          # /annotations/* endpoints
│   ├── taxonomy.md             # /taxonomy/* endpoints
│   ├── graph.md                # /graph/*, /citations/* endpoints
│   ├── recommendations.md      # /recommendations/* endpoints
│   ├── quality.md              # /quality/*, /curation/* endpoints
│   └── monitoring.md           # /monitoring/*, /health endpoints
├── architecture/
│   ├── README.md               # Architecture section overview
│   ├── overview.md             # High-level system diagrams
│   ├── database.md             # Schema, models, migrations
│   ├── event-system.md         # Event bus, handlers
│   ├── modules.md              # Vertical slice architecture
│   └── decisions.md            # ADRs and design decisions
├── guides/
│   ├── README.md               # Guides section overview
│   ├── setup.md                # Installation, environment
│   ├── workflows.md            # Development tasks, patterns
│   ├── testing.md              # Test strategies, coverage
│   ├── deployment.md           # Docker, production
│   └── troubleshooting.md      # Common issues, FAQ
└── [existing files]            # Other docs remain unchanged
```

## Components and Interfaces

### Content Extraction Strategy

Each API domain file follows a consistent structure:

```markdown
# [Domain] API

## Overview
Brief description of this API domain.

## Endpoints

### `METHOD /endpoint`
Description

**Request:**
```json
{ ... }
```

**Response:**
```json
{ ... }
```

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|

## Examples
curl examples

## Related
- Links to related docs
```

### Cross-Reference Pattern

All destination files include a "Related Documentation" section with relative links:

```markdown
## Related Documentation

- [API Overview](overview.md) - Base URL, authentication, errors
- [Resources API](resources.md) - Resource management endpoints
- [Architecture Overview](../architecture/overview.md) - System design
```

### Deprecation Notice Template

```markdown
> ⚠️ **DEPRECATED**: This file has been split into modular documentation.
> See `backend/docs/index.md` for the new structure.
> 
> **New locations:**
> - API docs: `backend/docs/api/`
> - Architecture: `backend/docs/architecture/`
> - Guides: `backend/docs/guides/`
```

## Data Models

### Content Mapping Table

| Source Section | Destination File | Estimated Size |
|----------------|------------------|----------------|
| Base URL, Auth, Errors | `api/overview.md` | ~5KB |
| `/resources/*` endpoints | `api/resources.md` | ~15KB |
| `/search/*` endpoints | `api/search.md` | ~12KB |
| `/collections/*` endpoints | `api/collections.md` | ~10KB |
| `/annotations/*` endpoints | `api/annotations.md` | ~8KB |
| `/taxonomy/*` endpoints | `api/taxonomy.md` | ~6KB |
| `/graph/*`, `/citations/*` | `api/graph.md` | ~10KB |
| `/recommendations/*` | `api/recommendations.md` | ~8KB |
| `/quality/*`, `/curation/*` | `api/quality.md` | ~10KB |
| `/monitoring/*`, `/health` | `api/monitoring.md` | ~5KB |
| System diagrams | `architecture/overview.md` | ~15KB |
| Database schema | `architecture/database.md` | ~10KB |
| Event system | `architecture/event-system.md` | ~8KB |
| Vertical slices | `architecture/modules.md` | ~10KB |
| Design decisions | `architecture/decisions.md` | ~5KB |
| Installation, setup | `guides/setup.md` | ~10KB |
| Development tasks | `guides/workflows.md` | ~8KB |
| Testing strategies | `guides/testing.md` | ~10KB |
| Deployment | `guides/deployment.md` | ~8KB |
| Troubleshooting | `guides/troubleshooting.md` | ~5KB |

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

This migration is primarily a documentation task without executable code, so formal property-based testing is not applicable. However, we can define verification properties that must hold after migration:

### Verification Property 1: Content Completeness
*For any* section in the source documentation, there exists a corresponding section in one of the destination files containing equivalent information.
**Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**

### Verification Property 2: Link Integrity
*For any* internal link in a destination file, the target file exists and the link resolves correctly.
**Validates: Requirements 5.1, 5.2, 5.3, 5.4**

### Verification Property 3: Deprecation Coverage
*For any* source file that has been migrated, a deprecation notice exists at the top of that file listing all new locations.
**Validates: Requirements 6.1, 6.2, 6.3, 6.4**

### Verification Property 4: Navigation Accuracy
*For any* file listed in `backend/docs/index.md`, the file exists at the specified path.
**Validates: Requirements 5.3**

## Error Handling

### Missing Content Handling
- If content doesn't fit a specific destination, create a note in the most relevant file
- Document any content that couldn't be migrated in a migration log

### Link Resolution
- Use relative paths for all internal links
- Verify links exist before finalizing migration
- Update broken links in source files if discovered

### Large File Handling
- If a destination file exceeds 15KB, consider further subdivision
- Document any files that exceed guidelines with justification

## Testing Strategy

Since this is a documentation migration (not code), testing focuses on manual verification:

### Verification Checklist

1. **Content Audit**
   - Compare source and destination file sizes
   - Verify all major sections are present
   - Check code examples are preserved

2. **Link Verification**
   - Test all internal links in destination files
   - Verify `index.md` navigation works
   - Check cross-references between sections

3. **Format Consistency**
   - Verify markdown renders correctly
   - Check code blocks have proper syntax highlighting
   - Ensure tables are properly formatted

4. **Deprecation Notices**
   - Verify notices are at top of source files
   - Check all new locations are listed
   - Confirm links in notices work

### Post-Migration Validation

After migration, verify:
- [ ] All content from source files is in destination files
- [ ] All internal links work
- [ ] `backend/docs/index.md` navigation is accurate
- [ ] `AGENTS.md` routing table is correct
- [ ] No duplicate content between old and new files
- [ ] File sizes are within 5-15KB guideline (where practical)
