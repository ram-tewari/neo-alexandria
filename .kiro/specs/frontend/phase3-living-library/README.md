# Phase 3: Living Library - PDF/Docs Management

**Status**: 📋 Ready to Start
**Complexity**: ⭐⭐⭐⭐ High
**Dependencies**: Phase 1 (Workbench) ✅, Phase 2 (Code Editor) ✅, Phase 2.5 (Backend Integration) ✅

## Overview

Phase 3 delivers a professional document management system for PDFs and scholarly papers, with intelligent features like auto-linking, equation/table extraction, and collection management.

## What It Delivers

- Grid view of uploaded PDFs/documents
- PDF viewer with text highlighting
- Auto-link suggestions (PDF ↔ Code via embeddings)
- Equation/Table drawers (leverages Scholarly extraction metadata)
- Batch collection operations
- Similar collections discovery
- Page-level navigation
- Search within PDFs
- Extracted scholarly assets visualization

## Key Features

### 1. Document Grid View
- Responsive grid layout with document cards
- Thumbnail previews
- Metadata display (title, authors, date, quality score)
- Filter and sort options
- Quick actions (open, delete, add to collection)

### 2. PDF Viewer
- Full-screen PDF rendering with react-pdf
- Page navigation controls
- Zoom and pan
- Text selection and highlighting
- Annotation support
- Side-by-side view with metadata

### 3. Scholarly Assets
- Equation drawer with LaTeX rendering
- Table extraction and display
- Citation extraction and linking
- Metadata completeness indicators

### 4. Auto-Linking Intelligence
- Suggest related code files based on embeddings
- Suggest related papers
- Visual link indicators
- One-click navigation

### 5. Collection Management
- Create and manage collections
- Batch add/remove resources
- Find similar collections
- Collection statistics

## Backend API Endpoints (24 total)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/resources` | POST | Upload resource |
| `/resources` | GET | List resources |
| `/resources/{resource_id}` | GET | Get resource |
| `/resources/{resource_id}` | PUT | Update resource |
| `/resources/{resource_id}` | DELETE | Delete resource |
| `/resources/ingest-repo` | POST | Repository ingestion |
| `/scholarly/resources/{resource_id}/equations` | GET | Get equations |
| `/scholarly/resources/{resource_id}/tables` | GET | Get tables |
| `/scholarly/metadata/{resource_id}` | GET | Get metadata |
| `/scholarly/metadata/completeness-stats` | GET | Metadata completeness |
| `/scholarly/health` | GET | Scholarly module health |
| `/collections` | POST | Create collection |
| `/collections` | GET | List collections |
| `/collections/{collection_id}` | GET | Get collection |
| `/collections/{collection_id}` | PUT | Update collection |
| `/collections/{collection_id}` | DELETE | Delete collection |
| `/collections/{collection_id}/resources` | GET | List collection resources |
| `/collections/{collection_id}/resources` | PUT | Add resource to collection |
| `/collections/{collection_id}/similar-collections` | GET | Find similar collections |
| `/collections/{collection_id}/resources/batch` | POST | Batch add resources |
| `/collections/{collection_id}/resources/batch` | DELETE | Batch remove resources |
| `/collections/health` | GET | Collections module health |
| `/search` | POST | Search resources |
| `/search/health` | GET | Search module health |

## Implementation Approach

**Recommended: Option C - Hybrid Power** ⭐⭐⭐⭐ High Complexity

- **Style**: Professional document manager
- **Components**: magic-mcp library grid + shadcn-ui + react-pdf
- **Interaction**: Search, filter, preview, smart linking
- **Pros**: Powerful features, good UX
- **Cons**: Complex PDF/code syncing logic

## File Structure

```
.kiro/specs/frontend/phase3-living-library/
├── README.md           # This file
├── requirements.md     # User stories and acceptance criteria
├── design.md          # Technical architecture and component design
└── tasks.md           # Implementation checklist
```

## Related Documentation

- [Frontend Roadmap](../ROADMAP.md)
- [Phase 1 Spec](../phase1-workbench-navigation/)
- [Phase 2 Spec](../phase2-living-code-editor/)
- [Phase 2.5 Spec](../phase2.5-backend-api-integration/)
- [Backend API - Resources](../../../../backend/docs/api/resources.md)
- [Backend API - Scholarly](../../../../backend/docs/api/scholarly.md)
- [Backend API - Collections](../../../../backend/docs/api/collections.md)
- [Backend API - Search](../../../../backend/docs/api/search.md)

## Success Criteria

- [ ] Users can upload and view PDFs
- [ ] Scholarly assets (equations, tables) are extracted and displayed
- [ ] Auto-linking suggests related code and papers
- [ ] Collections can be created and managed
- [ ] Batch operations work efficiently
- [ ] Search within documents works
- [ ] All 24 API endpoints integrated
- [ ] Comprehensive test coverage
- [ ] Performance: <2s to load document grid
- [ ] Performance: <1s to open PDF viewer
