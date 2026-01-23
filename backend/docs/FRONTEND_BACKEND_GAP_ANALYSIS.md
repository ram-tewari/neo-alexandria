# Frontend-Backend Gap Analysis
**Date**: January 21, 2026  
**Status**: Phase 19 Complete, Frontend Whitepaper Review

## Executive Summary

This document maps the Frontend Whitepaper features against current backend capabilities to identify what's ready, what needs minor adjustments, and what requires new development.

**Overall Status**: 70% backend support exists, 30% needs development

---

## Feature Matrix

### ✅ FULLY SUPPORTED (Ready to Use)

#### 1. **Module 1: Living Code Editor - Annotations**
**Backend Support**: Complete ✅
- **Endpoints**: `/api/annotations/*` (Full CRUD)
- **Features**:
  - Create/update/delete annotations with position tracking
  - Color-coded highlights
  - Tag support
  - Semantic search across annotations
  - Export to Markdown/JSON
- **Module**: `backend/app/modules/annotations/`
- **Frontend Action**: Wire up existing API

#### 2. **Module 2: Graph Explorer - Blast Radius**
**Backend Support**: Complete ✅
- **Endpoint**: `GET /api/graph/resource/{resource_id}/neighbors`
- **Features**:
  - Hybrid-scored neighbors (vector + tags + classification)
  - Configurable limit (1-20 neighbors)
  - Weighted edges with relationship types
- **Module**: `backend/app/modules/graph/`
- **Frontend Action**: Build React Flow visualization
- **⚠️ Gap**: No `depth` parameter (currently 1-hop only)

#### 3. **Module 2: Graph Explorer - Global Overview**
**Backend Support**: Complete ✅
- **Endpoint**: `GET /api/graph/overview`
- **Features**:
  - Strongest connections across library
  - Vector similarity + tag overlap
  - Configurable thresholds
- **Frontend Action**: Build "City Map" view

#### 4. **Module 3: Unified Search - Hybrid Search**
**Backend Support**: Complete ✅
- **Endpoint**: `POST /api/search/hybrid`
- **Features**:
  - Keyword + semantic fusion (RRF)
  - Configurable weights
  - Filtering by type, tags, quality
  - Pagination
- **Module**: `backend/app/modules/search/`
- **Frontend Action**: Already implemented in Phase 2!

#### 5. **Module 6: Ops & Edge Management**
**Backend Support**: Complete ✅
- **Endpoints**:
  - `POST /api/v1/ingestion/ingest` - Submit repo
  - `GET /api/v1/ingestion/status` - Worker status
  - `GET /api/v1/ingestion/history` - Job history
  - `GET /api/v1/ingestion/queue` - Queue status
- **Features**:
  - Real-time worker heartbeat
  - Job progress tracking
  - Queue management (max 10 tasks)
  - Task TTL (24 hours)
- **Module**: `backend/app/routers/ingestion.py`
- **Frontend Action**: Build status dashboard

#### 6. **Graph Embeddings (Node2Vec/DeepWalk)**
**Backend Support**: Complete ✅
- **Endpoints**:
  - `POST /api/graph/embeddings/generate` - Train embeddings
  - `GET /api/graph/embeddings/{node_id}` - Get embedding
  - `GET /api/graph/embeddings/{node_id}/similar` - Find similar
- **Features**:
  - Node2Vec and DeepWalk algorithms
  - Configurable dimensions, walk parameters
  - Similarity search
- **Frontend Action**: Use for "hover card" summaries

#### 7. **Literature-Based Discovery (LBD)**
**Backend Support**: Complete ✅
- **Endpoint**: `POST /api/graph/discover`
- **Features**:
  - ABC pattern hypothesis discovery
  - Bridging concept identification
  - Time-slicing support
  - Ranked by support strength
- **Frontend Action**: Could power "Reference Overlay"

---

### 🔧 PARTIALLY SUPPORTED (Needs Minor Work)

#### 8. **Module 1: Reference Overlay (Code-to-Paper Links)**
**Backend Support**: Partial 🔧
- **What Exists**:
  - Citation extraction: `POST /api/graph/resources/{id}/extract-citations`
  - Graph entity/relationship extraction
  - Vector similarity search
- **What's Missing**:
  - No explicit "code-to-paper" linking table
  - No metadata for `category="paper"` vs `category="code"`
  - No cross-collection similarity API
- **Required Work**:
  1. Add `category` field to Resource model
  2. Create endpoint: `GET /api/resources/{id}/related-papers`
  3. Background job to auto-link on ingestion
- **Effort**: 2-3 days

#### 9. **Module 1: Hover Cards (Node2Vec Summaries)**
**Backend Support**: Partial 🔧
- **What Exists**:
  - Node2Vec embeddings generation
  - Similar nodes API
- **What's Missing**:
  - No "summary" field in embedding response
  - No 1-hop graph API for hover context
- **Required Work**:
  1. Add `GET /api/graph/resource/{id}/context` endpoint
  2. Return: summary + 1-hop neighbors + embedding similarity
- **Effort**: 1 day

#### 10. **Module 2: Blast Radius - Multi-Hop Depth**
**Backend Support**: Partial 🔧
- **What Exists**:
  - 1-hop neighbor traversal
- **What's Missing**:
  - No `depth` query parameter
  - No recursive neighbor fetching
- **Required Work**:
  1. Add `depth` parameter to `/api/graph/resource/{id}/neighbors`
  2. Implement BFS traversal up to depth N
  3. Add cycle detection
- **Effort**: 1-2 days

---

### ❌ NOT SUPPORTED (Needs New Development)

#### 11. **Module 4: Implementation Planner**
**Backend Support**: None ❌
- **What's Missing**:
  - No "planner" service
  - No multi-hop agent logic
  - No architecture doc retrieval
  - No sample code matching
- **Required Work**:
  1. Create `backend/app/modules/planner/` module
  2. Implement `PlannerService.generate_plan(goal)`
  3. Multi-step workflow:
     - Step 1: Search for architecture docs
     - Step 2: Search for sample code
     - Step 3: LLM synthesis to Markdown checklist
  4. Store plans in database for tracking
- **Effort**: 5-7 days
- **⚠️ Scope Concern**: This is essentially an AI coding assistant, which conflicts with product.md non-goals

#### 12. **Module 5: Living Library (PDF Management)**
**Backend Support**: Minimal ❌
- **What Exists**:
  - PDF detection in content extractor
  - Basic format field in Resource model
- **What's Missing**:
  - No PDF upload endpoint
  - No PDF text extraction pipeline
  - No PDF chunking (different from code chunking)
  - No page number + offset metadata
  - No PDF-to-code auto-linking
- **Required Work**:
  1. Add PDF upload: `POST /api/resources/upload-pdf`
  2. Integrate PyMuPDF or PyPDF2 for text extraction
  3. Create PDF chunking strategy (by paragraph/section)
  4. Store `page_number` and `text_offset` in chunk metadata
  5. Background job: `link_docs_to_code(doc_id)`
  6. Endpoint: `GET /api/resources/{id}/linked-code`
- **Effort**: 7-10 days

#### 13. **Module 1: Semantic Highlighting (Tree-Sitter)**
**Backend Support**: None ❌
- **What's Missing**:
  - No Tree-Sitter integration
  - No AST tokenization API
  - No syntax highlighting metadata
- **Required Work**:
  - This is **frontend-only** work
  - Backend doesn't need to support this
  - Use Tree-Sitter WASM in browser
- **Effort**: Frontend team handles

#### 14. **Module 3: Reverse HyDE**
**Backend Support**: None ❌
- **What Exists**:
  - Standard hybrid search
- **What's Missing**:
  - No Reverse HyDE implementation
  - No hypothetical document generation
- **Required Work**:
  1. Add `reverse_hyde` parameter to search endpoint
  2. Generate hypothetical answer using LLM
  3. Embed hypothetical answer
  4. Search using hypothetical embedding
- **Effort**: 2-3 days
- **Note**: May not be needed if standard hybrid search performs well

#### 15. **MCP Interface (Head B)**
**Backend Support**: None ❌
- **What's Missing**:
  - No FastMCP integration
  - No `/mcp/sse` endpoint
  - No MCP tool wrappers
- **Required Work**:
  1. Install `fastmcp` package
  2. Create `backend/app/mcp/` module
  3. Wrap existing services as MCP tools:
     - `@mcp.tool()` for search
     - `@mcp.tool()` for graph neighbors
     - `@mcp.tool()` for planner (if built)
  4. Mount at `/mcp/sse`
- **Effort**: 3-4 days
- **Priority**: HIGH (enables IDE integration)

---

## Priority Recommendations

### Phase 1: Quick Wins (1-2 weeks)
**Goal**: Enable 80% of frontend features with minimal backend work

1. **Add depth parameter to Blast Radius** (1-2 days)
   - Endpoint: `GET /api/graph/resource/{id}/neighbors?depth=2`
   - Enables multi-hop visualization

2. **Add hover context endpoint** (1 day)
   - Endpoint: `GET /api/graph/resource/{id}/context`
   - Returns: summary + 1-hop graph + similar nodes

3. **Add code-to-paper linking** (2-3 days)
   - Endpoint: `GET /api/resources/{id}/related-papers`
   - Background job for auto-linking

4. **Build Ops Dashboard** (Frontend only)
   - Wire up existing ingestion endpoints
   - Real-time status updates

### Phase 2: PDF Pipeline (2-3 weeks)
**Goal**: Enable "Living Library" module

1. **PDF upload and extraction** (3-4 days)
   - Endpoint: `POST /api/resources/upload-pdf`
   - PyMuPDF integration

2. **PDF chunking strategy** (2-3 days)
   - Paragraph/section-based chunking
   - Store page_number + text_offset

3. **Cross-linking service** (2-3 days)
   - Background job: `link_docs_to_code()`
   - Vector similarity matching

### Phase 3: MCP Interface (1 week)
**Goal**: Enable IDE integration (Head B)

1. **FastMCP integration** (2 days)
   - Install and configure
   - Mount at `/mcp/sse`

2. **Tool wrappers** (2-3 days)
   - Wrap search, graph, and other services
   - Test with VS Code/Cursor

### Phase 4: Advanced Features (Optional)
**Goal**: Planner and advanced intelligence

1. **Implementation Planner** (5-7 days)
   - ⚠️ **Scope concern**: Review against product.md
   - May conflict with "No authoring tools" non-goal

2. **Reverse HyDE** (2-3 days)
   - Only if standard search underperforms

---

## API Endpoint Summary

### ✅ Ready to Use (No Changes Needed)
```
POST   /api/annotations                    # Create annotation
GET    /api/annotations/{id}               # Get annotation
PUT    /api/annotations/{id}               # Update annotation
DELETE /api/annotations/{id}               # Delete annotation
GET    /api/annotations/search/semantic    # Semantic search
GET    /api/annotations/export/markdown    # Export to Markdown

GET    /api/graph/resource/{id}/neighbors  # Blast radius (1-hop)
GET    /api/graph/overview                 # Global overview
POST   /api/graph/embeddings/generate      # Train Node2Vec
GET    /api/graph/embeddings/{id}/similar  # Find similar nodes
POST   /api/graph/discover                 # LBD hypothesis discovery

POST   /api/search/hybrid                  # Hybrid search
POST   /api/search/semantic                # Semantic search

POST   /api/v1/ingestion/ingest            # Submit repo
GET    /api/v1/ingestion/status            # Worker status
GET    /api/v1/ingestion/history           # Job history
GET    /api/v1/ingestion/queue             # Queue status
```

### 🔧 Needs Minor Updates
```
GET    /api/graph/resource/{id}/neighbors?depth=N  # Add depth param
GET    /api/graph/resource/{id}/context            # New: hover context
GET    /api/resources/{id}/related-papers          # New: code-to-paper links
```

### ❌ Needs New Development
```
POST   /api/resources/upload-pdf           # PDF upload
GET    /api/resources/{id}/linked-code     # PDF-to-code links
POST   /api/planner/generate               # Implementation planner
GET    /mcp/sse                            # MCP interface
```

---

## Conclusion

**Backend Readiness**: 70%

Your backend is **remarkably well-prepared** for the frontend whitepaper. The core infrastructure (annotations, graph, search, ops) is production-ready. The main gaps are:

1. **PDF pipeline** - Needs 2-3 weeks of work
2. **MCP interface** - Needs 1 week of work
3. **Implementation Planner** - Needs scope clarification (conflicts with product goals)

**Recommendation**: Focus on Phase 1 (Quick Wins) and Phase 3 (MCP) first. These unlock 80% of the frontend vision with minimal backend work. Phase 2 (PDF) can follow based on user demand.
