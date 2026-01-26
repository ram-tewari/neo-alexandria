# Phase 3: Living Library - Specification Summary

## Quick Reference

**Status**: 📋 Ready to Start  
**Complexity**: ⭐⭐⭐⭐ High  
**Estimated Time**: 4-5 weeks  
**Dependencies**: Phase 1 ✅, Phase 2 ✅, Phase 2.5 ✅  
**API Endpoints**: 24 total

## What This Phase Delivers

A professional document management system for PDFs and scholarly papers with:
- Document upload and grid view
- Full-featured PDF viewer with highlighting
- Equation and table extraction display
- Auto-linking between papers and code
- Collection management with batch operations
- Search and discovery features

## Key Features

### 1. Document Management
- Upload PDFs, HTML, and text documents
- Grid view with thumbnails and metadata
- Filter by type, quality, date
- Sort by multiple criteria
- Search across documents

### 2. PDF Viewer
- Full-screen PDF rendering
- Page navigation and zoom controls
- Text highlighting with colors
- Annotation support
- Page thumbnails sidebar

### 3. Scholarly Assets
- Extracted equations with LaTeX rendering
- Extracted tables with formatting
- Metadata display and editing
- Completeness indicators

### 4. Auto-Linking Intelligence
- Suggest related code files
- Suggest related papers
- Similarity scores
- One-click navigation

### 5. Collection Management
- Create and organize collections
- Batch add/remove operations
- Find similar collections
- Collection statistics dashboard

## API Integration (24 Endpoints)

### Resources (6 endpoints)
- POST /resources - Upload
- GET /resources - List
- GET /resources/{id} - Get
- PUT /resources/{id} - Update
- DELETE /resources/{id} - Delete
- POST /resources/ingest-repo - Ingest

### Scholarly (4 endpoints)
- GET /scholarly/resources/{id}/equations
- GET /scholarly/resources/{id}/tables
- GET /scholarly/metadata/{id}
- GET /scholarly/metadata/completeness-stats

### Collections (11 endpoints)
- POST /collections - Create
- GET /collections - List
- GET /collections/{id} - Get
- PUT /collections/{id} - Update
- DELETE /collections/{id} - Delete
- GET /collections/{id}/resources - List resources
- PUT /collections/{id}/resources - Add resource
- GET /collections/{id}/similar-collections - Find similar
- POST /collections/{id}/resources/batch - Batch add
- DELETE /collections/{id}/resources/batch - Batch remove
- GET /collections/health - Health check

### Search (2 endpoints)
- POST /search - Search resources
- GET /search/health - Health check

### Health (1 endpoint)
- GET /scholarly/health - Health check

## Technical Architecture

### State Management
- **Library Store**: Resources, filters, sorting
- **PDF Viewer Store**: Pages, zoom, highlights
- **Collections Store**: Collections, selection

### Custom Hooks
- **useDocuments**: Fetch, upload, update, delete
- **usePDFViewer**: Page navigation, zoom, highlights
- **useScholarlyAssets**: Equations, tables, metadata
- **useCollections**: CRUD, batch operations
- **useAutoLinking**: Related resources

### Key Components
- DocumentGrid, DocumentCard, DocumentUpload
- PDFViewer, PDFToolbar, PDFHighlighter
- EquationDrawer, TableDrawer, MetadataPanel
- RelatedCodePanel, RelatedPapersPanel
- CollectionManager, CollectionPicker, BatchOperations

### Dependencies
- react-pdf - PDF rendering
- pdfjs-dist - PDF.js library
- katex - LaTeX rendering
- react-window - Virtual scrolling
- react-dropzone - File upload

## Implementation Timeline

### Week 1: Foundation
- Setup and dependencies
- TypeScript types
- API clients (library, scholarly, collections)
- State stores
- Initial tests

### Week 2: Document Management
- Custom hooks
- Document grid and cards
- Upload interface
- Filters and sorting
- Component tests

### Week 3: PDF Viewer
- PDF viewer component
- Toolbar and controls
- Text highlighting
- Scholarly asset drawers
- Viewer tests

### Week 4: Collections & Auto-Linking
- Auto-linking panels
- Collection manager
- Batch operations
- Collection statistics
- Integration tests

### Week 5: Testing & Polish
- Integration tests
- Property-based tests
- E2E tests
- Performance optimization
- Accessibility audit
- Documentation

## Success Metrics

### Functionality
- [ ] All 24 API endpoints integrated
- [ ] All user stories implemented
- [ ] Upload, view, annotate, organize workflows complete

### Quality
- [ ] 90%+ test coverage
- [ ] All integration tests passing
- [ ] Property tests passing
- [ ] E2E tests passing

### Performance
- [ ] Document grid loads in <2s (100 docs)
- [ ] PDF viewer opens in <1s
- [ ] Search results in <500ms
- [ ] Batch operations in <5s (50 docs)

### Accessibility
- [ ] WCAG AA compliance
- [ ] Keyboard navigation working
- [ ] Screen reader support verified
- [ ] Focus management correct

### Documentation
- [ ] Component documentation complete
- [ ] User guide written
- [ ] API integration guide written
- [ ] Keyboard shortcuts documented

## Files Created

```
frontend/src/
├── features/library/
│   ├── DocumentGrid.tsx
│   ├── DocumentCard.tsx
│   ├── DocumentUpload.tsx
│   ├── DocumentFilters.tsx
│   ├── PDFViewer.tsx
│   ├── PDFToolbar.tsx
│   ├── PDFHighlighter.tsx
│   ├── EquationDrawer.tsx
│   ├── TableDrawer.tsx
│   ├── MetadataPanel.tsx
│   ├── RelatedCodePanel.tsx
│   ├── RelatedPapersPanel.tsx
│   ├── CollectionManager.tsx
│   ├── CollectionPicker.tsx
│   ├── CollectionStats.tsx
│   ├── BatchOperations.tsx
│   └── __tests__/ (15+ test files)
├── lib/api/
│   ├── library.ts
│   ├── scholarly.ts
│   ├── collections.ts
│   └── __tests__/ (3 test files)
├── lib/hooks/
│   ├── useDocuments.ts
│   ├── usePDFViewer.ts
│   ├── useScholarlyAssets.ts
│   ├── useCollections.ts
│   ├── useAutoLinking.ts
│   └── __tests__/ (7+ test files)
├── stores/
│   ├── library.ts
│   ├── pdfViewer.ts
│   ├── collections.ts
│   └── __tests__/ (3 test files)
├── types/
│   └── library.ts
└── routes/
    └── _auth.library.tsx
```

**Total Files**: 50+ new files

## Related Documentation

- [Requirements](./requirements.md) - User stories and acceptance criteria
- [Design](./design.md) - Technical architecture and component design
- [Tasks](./tasks.md) - Implementation checklist (60+ tasks)
- [Frontend Roadmap](../ROADMAP.md) - Overall frontend plan
- [Backend API - Resources](../../../../backend/docs/api/resources.md)
- [Backend API - Scholarly](../../../../backend/docs/api/scholarly.md)
- [Backend API - Collections](../../../../backend/docs/api/collections.md)

## Next Steps

1. Review this specification
2. Confirm API endpoints are available
3. Start with Task 1.1 (Project Setup)
4. Follow tasks sequentially
5. Test continuously
6. Document as you go

## Questions?

- Check the [requirements](./requirements.md) for user stories
- Check the [design](./design.md) for technical details
- Check the [tasks](./tasks.md) for implementation steps
- Refer to Phase 2.5 for API integration patterns
