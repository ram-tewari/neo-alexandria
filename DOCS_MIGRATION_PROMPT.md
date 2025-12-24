# Documentation Migration Prompt

Use this prompt in a new chat session to complete the documentation migration.

---

## PROMPT START

I need you to complete the documentation migration for Neo Alexandria 2.0. The directory structure has been created with placeholder files, but the actual content needs to be migrated from the monolithic files.

### Current State

**Structure created (placeholders only):**
```
backend/docs/
├── index.md                    ✅ Created
├── api/
│   ├── README.md               ✅ Created
│   ├── overview.md             ✅ Partially populated
│   ├── resources.md            📋 Placeholder
│   ├── search.md               📋 Placeholder
│   ├── collections.md          📋 Placeholder
│   ├── annotations.md          📋 Placeholder
│   ├── taxonomy.md             📋 Placeholder
│   ├── graph.md                📋 Placeholder
│   ├── recommendations.md      📋 Placeholder
│   ├── quality.md              📋 Placeholder
│   └── monitoring.md           📋 Placeholder
├── architecture/
│   ├── README.md               ✅ Created
│   ├── overview.md             📋 Placeholder
│   ├── database.md             📋 Placeholder
│   ├── event-system.md         📋 Placeholder
│   ├── modules.md              📋 Placeholder
│   └── decisions.md            📋 Placeholder
└── guides/
    ├── README.md               ✅ Created
    ├── setup.md                📋 Placeholder
    ├── workflows.md            📋 Placeholder
    ├── testing.md              📋 Placeholder
    ├── deployment.md           📋 Placeholder
    └── troubleshooting.md      📋 Placeholder
```

**Source files to migrate:**
1. `backend/docs/API_DOCUMENTATION.md` (~132KB) → Split into `api/*.md`
2. `backend/docs/ARCHITECTURE_DIAGRAM.md` → Split into `architecture/*.md`
3. `backend/docs/DEVELOPER_GUIDE.md` → Split into `guides/*.md`

### Migration Tasks

#### Task 1: Migrate API Documentation

Read `backend/docs/API_DOCUMENTATION.md` and split content into:

| Section | Destination |
|---------|-------------|
| Base URL, Auth, Errors, Pagination | `api/overview.md` (update existing) |
| Resource endpoints (`/resources/*`) | `api/resources.md` |
| Search endpoints (`/search/*`) | `api/search.md` |
| Collection endpoints (`/collections/*`) | `api/collections.md` |
| Annotation endpoints (`/annotations/*`) | `api/annotations.md` |
| Taxonomy endpoints (`/taxonomy/*`) | `api/taxonomy.md` |
| Graph & Citation endpoints (`/graph/*`, `/citations/*`) | `api/graph.md` |
| Recommendation endpoints (`/recommendations/*`) | `api/recommendations.md` |
| Quality endpoints (`/quality/*`, `/curation/*`) | `api/quality.md` |
| Monitoring endpoints (`/monitoring/*`, `/health`) | `api/monitoring.md` |

**Format for each API file:**
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

#### Task 2: Migrate Architecture Documentation

Read `backend/docs/ARCHITECTURE_DIAGRAM.md` and split content into:

| Section | Destination |
|---------|-------------|
| High-level diagrams, system overview | `architecture/overview.md` |
| Database schema, models, migrations | `architecture/database.md` |
| Event system, event bus, handlers | `architecture/event-system.md` |
| Vertical slice modules, module structure | `architecture/modules.md` |
| Design decisions, ADRs | `architecture/decisions.md` |

#### Task 3: Migrate Developer Guide

Read `backend/docs/DEVELOPER_GUIDE.md` and split content into:

| Section | Destination |
|---------|-------------|
| Installation, environment setup, prerequisites | `guides/setup.md` |
| Common tasks, adding features, code patterns | `guides/workflows.md` |
| Testing strategies, running tests, coverage | `guides/testing.md` |
| Docker, production deployment, monitoring | `guides/deployment.md` |
| Common issues, debugging, FAQ | `guides/troubleshooting.md` |

#### Task 4: Update Steering Docs

After migration, update these files to reflect the new structure:

1. **`.kiro/steering/structure.md`** - Update the documentation hierarchy section
2. **`AGENTS.md`** - Verify routing rules point to new locations
3. **`backend/docs/MODULAR_DOCS_MIGRATION.md`** - Mark tasks as complete

#### Task 5: Add Deprecation Notices

Add deprecation notices to the top of old files:

```markdown
> ⚠️ **DEPRECATED**: This file has been split into modular documentation.
> See `backend/docs/index.md` for the new structure.
> 
> **New locations:**
> - API docs: `backend/docs/api/`
> - Architecture: `backend/docs/architecture/`
> - Guides: `backend/docs/guides/`
```

### Guidelines

1. **Preserve all content** - Don't lose any information during migration
2. **Improve organization** - Group related content logically
3. **Add cross-references** - Link between related docs
4. **Keep files focused** - Each file should cover one topic (~5-15KB ideal)
5. **Update internal links** - Fix any broken references
6. **Maintain consistency** - Use consistent formatting across all files

### Execution Order

1. Start with `api/resources.md` (most commonly used)
2. Then `api/search.md` (second most common)
3. Continue with remaining API files
4. Move to architecture files
5. Finish with guide files
6. Update steering docs
7. Add deprecation notices

### Verification

After migration, verify:
- [ ] All content from source files is in destination files
- [ ] All internal links work
- [ ] `backend/docs/index.md` navigation is accurate
- [ ] `AGENTS.md` routing table is correct
- [ ] No duplicate content between old and new files

---

## PROMPT END

---

**Note:** This is a large task. You may need to do it in multiple sessions, focusing on one source file at a time. Start with the API documentation as it's the largest and most frequently used.
