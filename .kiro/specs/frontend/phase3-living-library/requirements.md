# Phase 3: Living Library - Requirements

## Overview

Phase 3 delivers a professional document management system for PDFs and scholarly papers with intelligent features like auto-linking, equation/table extraction, and collection management.

## User Stories

### Epic 1: Document Management

**US-3.1: Upload Documents**
- As a researcher, I want to upload PDF documents so that I can manage my research library
- **Acceptance Criteria**:
  - Drag-and-drop file upload
  - Multi-file upload support
  - Progress indicators during upload
  - File type validation (PDF, HTML, TXT)
  - File size validation (max 50MB)
  - Success/error notifications
  - Automatic metadata extraction

**US-3.2: View Document Grid**
- As a user, I want to see all my documents in a grid view so that I can browse my library
- **Acceptance Criteria**:
  - Responsive grid layout (1-4 columns based on screen size)
  - Document cards with thumbnails
  - Display title, authors, date, quality score
  - Hover effects and quick actions
  - Empty state with upload prompt
  - Loading skeletons during fetch

**US-3.3: Filter and Sort Documents**
- As a user, I want to filter and sort documents so that I can find what I need quickly
- **Acceptance Criteria**:
  - Filter by type (PDF, HTML, Code)
  - Filter by quality score range
  - Filter by date range
  - Sort by date, title, quality score
  - Search by title/content
  - Clear filters button
  - Filter state persisted in URL

**US-3.4: Delete Documents**
- As a user, I want to delete documents so that I can manage my library
- **Acceptance Criteria**:
  - Delete button on document card
  - Confirmation dialog
  - Optimistic UI update
  - Success/error notifications
  - Undo option (5 second window)

### Epic 2: PDF Viewer

**US-3.5: View PDF Documents**
- As a user, I want to view PDF documents so that I can read them
- **Acceptance Criteria**:
  - Full-screen PDF viewer
  - Page navigation (prev/next, jump to page)
  - Zoom controls (fit width, fit page, custom zoom)
  - Pan and scroll
  - Page thumbnails sidebar
  - Current page indicator
  - Total page count display

**US-3.6: Highlight PDF Text**
- As a user, I want to highlight text in PDFs so that I can mark important sections
- **Acceptance Criteria**:
  - Text selection with mouse
  - Highlight color picker
  - Save highlights to backend
  - Display saved highlights
  - Delete highlights
  - Highlight persistence across sessions

**US-3.7: Annotate PDFs**
- As a user, I want to add notes to PDFs so that I can capture my thoughts
- **Acceptance Criteria**:
  - Click to add annotation
  - Annotation form with text input
  - Link annotation to page/position
  - Display annotation markers
  - Click marker to view/edit annotation
  - Delete annotations
  - Annotation list sidebar

### Epic 3: Scholarly Assets

**US-3.8: View Extracted Equations**
- As a researcher, I want to see extracted equations so that I can review mathematical content
- **Acceptance Criteria**:
  - Equation drawer/panel
  - LaTeX rendering with KaTeX
  - Equation numbering
  - Copy LaTeX source
  - Jump to equation in document
  - Equation search
  - Export equations

**US-3.9: View Extracted Tables**
- As a researcher, I want to see extracted tables so that I can review data
- **Acceptance Criteria**:
  - Table drawer/panel
  - Formatted table display
  - Table numbering
  - Copy table data (CSV, JSON)
  - Jump to table in document
  - Table search
  - Export tables

**US-3.10: View Metadata Completeness**
- As a user, I want to see metadata completeness so that I know data quality
- **Acceptance Criteria**:
  - Completeness indicator (percentage)
  - Missing fields highlighted
  - Metadata edit form
  - Save metadata updates
  - Metadata history
  - Bulk metadata operations

### Epic 4: Auto-Linking Intelligence

**US-3.11: View Related Code Files**
- As a developer, I want to see related code files so that I can connect papers to implementation
- **Acceptance Criteria**:
  - "Related Code" panel
  - List of suggested code files
  - Similarity scores displayed
  - Click to open in code editor
  - Refresh suggestions button
  - Explanation of why related

**US-3.12: View Related Papers**
- As a researcher, I want to see related papers so that I can explore connections
- **Acceptance Criteria**:
  - "Related Papers" panel
  - List of suggested papers
  - Similarity scores displayed
  - Click to open paper
  - Citation relationships shown
  - Refresh suggestions button

**US-3.13: Manual Link Creation**
- As a user, I want to manually create links so that I can capture custom relationships
- **Acceptance Criteria**:
  - "Add Link" button
  - Search for target resource
  - Select link type (cites, implements, extends)
  - Add link description
  - Save link
  - View/delete links

### Epic 5: Collection Management

**US-3.14: Create Collections**
- As a user, I want to create collections so that I can organize documents
- **Acceptance Criteria**:
  - "New Collection" button
  - Collection name input
  - Collection description input
  - Collection tags
  - Save collection
  - Success notification

**US-3.15: Add Documents to Collections**
- As a user, I want to add documents to collections so that I can organize them
- **Acceptance Criteria**:
  - "Add to Collection" button on document card
  - Collection picker dialog
  - Multi-select collections
  - Save selections
  - Visual indicator of collection membership
  - Remove from collection option

**US-3.16: Batch Collection Operations**
- As a user, I want to perform batch operations so that I can manage collections efficiently
- **Acceptance Criteria**:
  - Multi-select documents (checkboxes)
  - "Add to Collection" batch action
  - "Remove from Collection" batch action
  - Progress indicator for batch operations
  - Success/error summary
  - Undo option

**US-3.17: Find Similar Collections**
- As a user, I want to find similar collections so that I can discover related content
- **Acceptance Criteria**:
  - "Find Similar" button on collection page
  - List of similar collections
  - Similarity scores displayed
  - Click to view collection
  - Explanation of similarity
  - Merge collections option

**US-3.18: View Collection Statistics**
- As a user, I want to see collection statistics so that I understand my library
- **Acceptance Criteria**:
  - Total documents count
  - Document type breakdown
  - Average quality score
  - Date range of documents
  - Top tags/topics
  - Visual charts

### Epic 6: Search and Discovery

**US-3.19: Search Within Documents**
- As a user, I want to search within documents so that I can find specific content
- **Acceptance Criteria**:
  - Search input in PDF viewer
  - Highlight search results
  - Navigate between results
  - Result count display
  - Case-sensitive option
  - Whole word option

**US-3.20: Global Document Search**
- As a user, I want to search across all documents so that I can find information
- **Acceptance Criteria**:
  - Global search bar
  - Search by title, content, metadata
  - Hybrid search (keyword + semantic)
  - Search results with snippets
  - Click to open document
  - Filter search results
  - Search history

## API Integration Requirements

### Resource Management APIs (6 endpoints)

**POST /resources** - Upload resource
- Request: multipart/form-data with file
- Response: Resource object with ID
- Error handling: file too large, invalid type
- Loading state: upload progress
- Success: redirect to document view

**GET /resources** - List resources
- Query params: type, quality_min, quality_max, limit, offset
- Response: paginated resource list
- Caching: 5 minutes
- Loading state: skeleton grid
- Error handling: retry with exponential backoff

**GET /resources/{resource_id}** - Get resource
- Response: full resource object with metadata
- Caching: 10 minutes
- Loading state: skeleton card
- Error handling: 404 not found

**PUT /resources/{resource_id}** - Update resource
- Request: partial resource object
- Response: updated resource
- Optimistic update: immediate UI update
- Error handling: rollback on failure

**DELETE /resources/{resource_id}** - Delete resource
- Response: 204 no content
- Optimistic update: remove from grid
- Undo window: 5 seconds
- Error handling: restore on failure

**POST /resources/ingest-repo** - Ingest repository
- Request: { repo_url, branch }
- Response: job ID and status
- Polling: check status every 2 seconds
- Loading state: progress indicator
- Error handling: job failure notification

### Scholarly APIs (4 endpoints)

**GET /scholarly/resources/{resource_id}/equations** - Get equations
- Response: array of equation objects
- Caching: 30 minutes
- Loading state: skeleton list
- Error handling: empty state

**GET /scholarly/resources/{resource_id}/tables** - Get tables
- Response: array of table objects
- Caching: 30 minutes
- Loading state: skeleton list
- Error handling: empty state

**GET /scholarly/metadata/{resource_id}** - Get metadata
- Response: metadata object with completeness
- Caching: 10 minutes
- Loading state: skeleton form
- Error handling: partial data display

**GET /scholarly/metadata/completeness-stats** - Metadata completeness
- Response: aggregated completeness statistics
- Caching: 1 hour
- Loading state: skeleton chart
- Error handling: fallback to cached data

### Collection APIs (11 endpoints)

**POST /collections** - Create collection
- Request: { name, description, tags }
- Response: collection object with ID
- Optimistic update: add to list immediately
- Error handling: rollback on failure

**GET /collections** - List collections
- Query params: limit, offset
- Response: paginated collection list
- Caching: 5 minutes
- Loading state: skeleton list
- Error handling: retry with backoff

**GET /collections/{collection_id}** - Get collection
- Response: collection with resource list
- Caching: 5 minutes
- Loading state: skeleton page
- Error handling: 404 not found

**PUT /collections/{collection_id}** - Update collection
- Request: partial collection object
- Response: updated collection
- Optimistic update: immediate UI update
- Error handling: rollback on failure

**DELETE /collections/{collection_id}** - Delete collection
- Response: 204 no content
- Confirmation dialog required
- Optimistic update: remove from list
- Error handling: restore on failure

**GET /collections/{collection_id}/resources** - List collection resources
- Query params: limit, offset
- Response: paginated resource list
- Caching: 5 minutes
- Loading state: skeleton grid
- Error handling: empty state

**PUT /collections/{collection_id}/resources** - Add resource to collection
- Request: { resource_id }
- Response: updated collection
- Optimistic update: add to list
- Error handling: rollback on failure

**GET /collections/{collection_id}/similar-collections** - Find similar
- Query params: limit
- Response: array of similar collections with scores
- Caching: 1 hour
- Loading state: skeleton list
- Error handling: empty state

**POST /collections/{collection_id}/resources/batch** - Batch add
- Request: { resource_ids: [] }
- Response: { added: number, failed: [] }
- Progress indicator during operation
- Error handling: partial success handling

**DELETE /collections/{collection_id}/resources/batch** - Batch remove
- Request: { resource_ids: [] }
- Response: { removed: number, failed: [] }
- Progress indicator during operation
- Error handling: partial success handling

**GET /collections/health** - Collections health
- Response: health status
- Used for: connection testing
- Error handling: fallback mode

### Search APIs (2 endpoints)

**POST /search** - Search resources
- Request: { query, type, limit }
- Response: search results with scores
- Debounced: 300ms
- Loading state: skeleton results
- Error handling: show last results

**GET /search/health** - Search health
- Response: health status
- Used for: connection testing
- Error handling: fallback mode

### Health Check APIs (1 endpoint)

**GET /scholarly/health** - Scholarly health
- Response: health status
- Used for: connection testing
- Error handling: fallback mode

## Performance Requirements

- Document grid load: <2s for 100 documents
- PDF viewer open: <1s
- Search results: <500ms
- Equation/table extraction: <3s
- Collection operations: <1s
- Batch operations: <5s for 50 documents
- Auto-linking suggestions: <2s

## Accessibility Requirements

- Keyboard navigation for all features
- Screen reader support for document grid
- ARIA labels for all interactive elements
- Focus indicators
- Color contrast compliance (WCAG AA)
- Alt text for thumbnails

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Dependencies

- Phase 1 (Workbench) ✅
- Phase 2 (Code Editor) ✅
- Phase 2.5 (Backend Integration) ✅
- Backend API deployed at https://pharos.onrender.com ✅
