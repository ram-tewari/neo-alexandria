# Implementation Plan: Phase 2 - Living Code Editor

## Overview

This implementation plan breaks down the Phase 2 Living Code Editor into discrete, incremental tasks. Each task builds on previous work and includes testing sub-tasks to validate functionality early. The plan follows the "Hybrid Power" approach using magic-mcp for scaffolding, shadcn-ui for core components, and magic-ui for strategic animations.

## Tasks

- [x] 1. Set up Monaco Editor foundation and project structure
  - Install Monaco Editor dependencies (@monaco-editor/react, monaco-editor)
  - Create feature directory structure (`src/features/editor/`)
  - Set up Monaco utilities directory (`src/lib/monaco/`)
  - Configure Vite for Monaco Editor web workers
  - Create basic TypeScript types for editor domain models
  - _Requirements: 1.1, 1.2_

- [x] 1.1 Write unit tests for Monaco configuration
  - Test Monaco options generation
  - Test theme switching
  - Test language detection
  - _Requirements: 1.1, 1.5_

- [x] 2. Create Zustand stores for editor state management
  - [x] 2.1 Implement editorStore with file, cursor, and selection state
    - Create store with activeFile, cursorPosition, selection, scrollPosition
    - Implement setActiveFile, updateCursorPosition, updateSelection actions
    - Add local storage persistence for scroll position
    - _Requirements: 9.1, 9.2_

  - [x] 2.2 Implement annotationStore with CRUD operations
    - Create store with annotations array and selectedAnnotation
    - Implement fetchAnnotations, createAnnotation, updateAnnotation, deleteAnnotation
    - Add optimistic updates for better UX
    - _Requirements: 4.1, 4.6, 4.7_

  - [x] 2.3 Implement chunkStore for semantic chunk management
    - Create store with chunks array and selectedChunk
    - Implement fetchChunks, selectChunk, toggleChunkVisibility
    - Add chunk caching logic
    - _Requirements: 2.1, 2.4_

  - [x] 2.4 Implement qualityStore for quality data management
    - Create store with qualityData and badgeVisibility
    - Implement fetchQualityData, toggleBadgeVisibility
    - Add quality score caching
    - _Requirements: 3.1, 3.2_

  - [x] 2.5 Implement editorPreferencesStore with persistence
    - Create store with theme, fontSize, lineNumbers, minimap, wordWrap preferences
    - Add chunkBoundaries, qualityBadges, annotations, references toggles
    - Implement local storage persistence
    - _Requirements: 9.1, 9.3_

- [x] 2.6 Write unit tests for all Zustand stores
  - Test state updates and actions
  - Test persistence logic
  - Test optimistic updates
  - _Requirements: All Requirement 2 sub-tasks_

- [x] 3. Implement API client for editor features
  - Create `src/lib/api/editor.ts` with annotation endpoints
  - Add chunk fetching endpoints
  - Add quality data endpoints
  - Add placeholder for Node2Vec/graph endpoints
  - Configure TanStack Query hooks for caching
  - _Requirements: 4.1, 4.6, 4.7, 2.1, 3.1_

- [x] 3.1 Write unit tests for API client
  - Test API calls with MSW mocks
  - Test error handling
  - Test request/response transformations
  - _Requirements: 10.1, 10.2, 10.3, 10.4_

- [x] 4. Build MonacoEditorWrapper core component
  - [x] 4.1 Create MonacoEditorWrapper component with basic Monaco integration
    - Use @monaco-editor/react for React integration
    - Configure read-only mode
    - Set up theme switching (light/dark)
    - Implement cursor and selection tracking
    - Add scroll position restoration
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 9.2_

  - [x] 4.2 Add Monaco decoration API setup
    - Create decoration manager utility
    - Implement decoration update batching
    - Add decoration disposal on unmount
    - Set up glyph margin for gutter decorations
    - _Requirements: 2.2, 3.2, 4.2_

  - [x] 4.3 Implement virtualized rendering for large files
    - Configure Monaco for files >5000 lines
    - Add lazy-loading for decorations
    - Implement scroll-based decoration updates
    - _Requirements: 7.1, 7.2_

- [x] 4.4 Write unit tests for MonacoEditorWrapper
  - Test Monaco initialization
  - Test theme switching
  - Test cursor/selection tracking
  - Test decoration management
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 5. Implement SemanticChunkOverlay component
  - [x] 5.1 Create SemanticChunkOverlay with chunk boundary rendering
    - Fetch chunks from chunkStore on file load
    - Use Monaco deltaDecorations for chunk boundaries
    - Implement chunk hover highlighting
    - Add chunk click selection
    - Handle nested/overlapping chunks
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [x] 5.2 Add chunk visibility toggle
    - Connect to editorPreferencesStore
    - Implement smooth show/hide transition
    - Persist visibility preference
    - _Requirements: 8.5, 9.3_


- [x] 5.3 Write unit tests for SemanticChunkOverlay
  - Test chunk boundary rendering
  - Test hover and click interactions
  - Test nested chunk handling
  - Test visibility toggle
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 6. Implement QualityBadgeGutter component
  - [x] 6.1 Create QualityBadgeGutter with badge rendering
    - Fetch quality data from qualityStore
    - Render badges in Monaco glyph margin
    - Implement color coding (green/yellow/red)
    - Add hover tooltips with detailed metrics
    - Handle badge click events
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [x] 6.2 Add quality badge visibility toggle
    - Connect to editorPreferencesStore
    - Implement smooth show/hide transition
    - Persist visibility preference
    - _Requirements: 8.4, 9.3_

  - [x] 6.3 Implement lazy-loading for quality data
    - Load quality data on scroll
    - Debounce quality data requests
    - Cache quality data per resource
    - _Requirements: 7.3_


- [x] 6.4 Write unit tests for QualityBadgeGutter
  - Test badge rendering and color coding
  - Test tooltip display
  - Test visibility toggle
  - Test lazy-loading
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 7. Implement AnnotationGutter component
  - [x] 7.1 Create AnnotationGutter with chip rendering
    - Fetch annotations from annotationStore
    - Render colored chips in Monaco glyph margin
    - Implement chip stacking for multiple annotations on same line
    - Add hover highlighting for annotated text
    - Handle chip click to open annotation details
    - _Requirements: 4.2, 4.3, 4.4, 4.5_

  - [x] 7.2 Add annotation text highlighting
    - Use Monaco decorations for text highlights
    - Apply annotation color to highlights
    - Handle overlapping annotations

    - _Requirements: 4.3_

- [x] 7.3 Write unit tests for AnnotationGutter
  - Test chip rendering and stacking
  - Test hover and click interactions
  - Test text highlighting
  - Test overlapping annotations
  - _Requirements: 4.2, 4.3, 4.4, 4.5_

- [x] 8. Implement AnnotationPanel component
  - [x] 8.1 Create AnnotationPanel with list view
    - Use shadcn-ui Sheet for slide-out panel
    - Display list of all annotations
    - Implement annotation selection
    - Add scroll-to-annotation on click
    - Use magic-ui slide animation
    - _Requirements: 4.4_

  - [x] 8.2 Add annotation editor form
    - Use shadcn-ui Input and Textarea
    - Implement create annotation flow
    - Implement edit annotation flow
    - Add tag input with shadcn-ui Badge
    - Add color picker
    - _Requirements: 4.1, 4.6_

  - [x] 8.3 Implement annotation deletion
    - Add delete button with confirmation
    - Update annotationStore on delete
    - Remove chip from gutter
    - _Requirements: 4.7_

  - [x] 8.4 Add annotation search
    - Use shadcn-ui Command for search UI
    - Implement full-text search
    - Add semantic search (when backend ready)

    - Filter annotations by tags
    - _Requirements: 8.3_

- [x] 8.5 Write unit tests for AnnotationPanel
  - Test annotation list rendering
  - Test create/edit/delete flows
  - Test search functionality
  - Test panel open/close
  - _Requirements: 4.1, 4.4, 4.6, 4.7, 8.3_

- [x] 9. Implement HoverCardProvider component
  - [x] 9.1 Create HoverCardProvider with debounced hover detection
    - Listen to Monaco onMouseMove events
    - Implement 300ms debounce
    - Detect symbol under cursor
    - Fetch Node2Vec summary from backend (placeholder for now)
    - _Requirements: 5.1, 7.4_

  - [x] 9.2 Build hover card UI with shadcn-ui HoverCard
    - Display Node2Vec summary
    - Show 1-hop graph connections
    - Add navigation links to related symbols
    - Use magic-ui fade-in animation
    - Show loading skeleton while fetching
    - _Requirements: 5.2, 5.3, 5.4, 5.5_

  - [x] 9.3 Add fallback to Monaco IntelliSense

    - Show basic symbol info when Node2Vec unavailable
    - Display error message gracefully
    - _Requirements: 5.6, 10.6_

- [x] 9.4 Write unit tests for HoverCardProvider
  - Test hover detection and debouncing
  - Test data fetching
  - Test hover card display
  - Test fallback behavior
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

- [x] 10. Implement ReferenceGutter component (placeholder)
  - [x] 10.1 Create ReferenceGutter with book icon rendering
    - Render book icons in Monaco glyph margin
    - Add hover tooltips with paper title
    - Handle click to open reference panel
    - _Requirements: 6.1, 6.2, 6.3_

  - [x] 10.2 Create reference details panel
    - Use shadcn-ui Dialog for modal

    - Display full citation details
    - Add "View in Library" button (Phase 3 integration)
    - Use magic-ui modal animation
    - _Requirements: 6.4, 6.5_

- [x] 10.3 Write unit tests for ReferenceGutter
  - Test icon rendering
  - Test tooltip display
  - Test panel open/close
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [-] 11. Implement ChunkMetadataPanel component

  - Create ChunkMetadataPanel with shadcn-ui Card
  - Display selected chunk metadata (function name, lines, language)
  - Add navigation to related chunks
  - Use magic-ui expand/collapse animation
  - _Requirements: 2.4_

- [ ] 11.1 Write unit tests for ChunkMetadataPanel
  - Test metadata display
  - Test navigation
  - Test expand/collapse
  - _Requirements: 2.4_

- [ ] 12. Implement keyboard navigation system
  - [ ] 12.1 Add global keyboard shortcuts
    - Implement Cmd+/ for annotation mode toggle
    - Implement Cmd+Shift+A for show all annotations
    - Implement Cmd+Shift+Q for quality badge toggle
    - Implement Cmd+Shift+C for chunk boundary toggle
    - Implement Cmd+Shift+R for reference toggle
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_


  - [ ] 12.2 Add annotation mode shortcuts
    - Implement Enter for create annotation
    - Implement Cmd+S for save annotation
    - Implement Cmd+Backspace for delete annotation
    - Implement Tab/Shift+Tab for navigation
    - _Requirements: 8.2, 8.3_

- [ ] 12.3 Write unit tests for keyboard navigation
  - Test all keyboard shortcuts
  - Test focus management
  - Test shortcut conflicts
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ] 13. Implement error handling and fallbacks
  - [ ] 13.1 Add Monaco fallback for load failures
    - Create fallback text viewer component
    - Show error message with retry button
    - Preserve file content
    - _Requirements: 10.1_

  - [ ] 13.2 Add API error handling
    - Handle annotation API failures with cached data
    - Handle chunk API failures with line-based fallback
    - Handle quality API failures with badge hiding
    - Show appropriate error messages and retry options

    - _Requirements: 10.2, 10.3, 10.4_

  - [ ] 13.3 Add hover card error handling
    - Fall back to Monaco IntelliSense on Node2Vec failure
    - Show "Unable to load summary" message
    - Provide retry button
    - _Requirements: 10.6_

- [ ] 13.4 Write unit tests for error handling
  - Test Monaco fallback
  - Test API error scenarios
  - Test hover card fallback
  - Test error message display
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.6_


- [ ] 14. Integrate editor into repository detail route
  - Update `_auth.repositories.tsx` route to include code editor view
  - Add file tree navigation (simple list for now)
  - Connect editor to repository store
  - Add file loading logic
  - Implement file switching
  - _Requirements: 1.1_

- [ ] 14.1 Write integration tests for editor route
  - Test file loading
  - Test file switching
  - Test editor initialization
  - Test store integration
  - _Requirements: 1.1_


- [ ] 15. Implement accessibility features
  - Add ARIA labels to all icon-only buttons
  - Implement focus management for modals and popovers
  - Add keyboard navigation for all interactive elements
  - Ensure color contrast meets WCAG 2.1 AA
  - Add screen reader announcements for status updates
  - Test with keyboard-only navigation
  - _Requirements: All requirements (accessibility is cross-cutting)_

- [ ] 15.1 Write accessibility tests
  - Test keyboard navigation
  - Test ARIA labels
  - Test focus management
  - Test color contrast
  - _Requirements: All requirements_

- [ ] 16. Optimize performance
  - [ ] 16.1 Implement decoration batching
    - Batch decoration updates to reduce reflows
    - Debounce decoration updates (100ms)
    - Limit concurrent decoration operations
    - _Requirements: 7.1, 7.2_

  - [ ] 16.2 Add React optimization
    - Memoize MonacoEditorWrapper and overlay components


    - Use React.memo for annotation chips
    - Virtualize annotation list with react-window
    - Debounce scroll events (100ms)
    - _Requirements: 7.2, 7.3_

  - [ ] 16.3 Implement API caching
    - Configure TanStack Query cache times
    - Add prefetching for active file chunks
    - Implement request deduplication
    - _Requirements: 7.3, 7.4_

- [ ] 16.4 Write performance tests
  - Test large file rendering (>5000 lines)
  - Test decoration update performance
  - Test scroll performance
  - Test API caching
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ] 17. Add Monaco theme customization
  - Create custom Monaco themes for light/dark modes
  - Add syntax highlighting for all supported languages
  - Implement theme switching without editor reload
  - Style gutter decorations to match theme
  - _Requirements: 1.2, 1.5_

- [ ] 17.1 Write tests for theme customization
  - Test theme switching
  - Test syntax highlighting
  - Test gutter decoration styling
  - _Requirements: 1.2, 1.5_

- [ ] 18. Final integration and polish
  - [ ] 18.1 Test all features together
    - Open file with all overlays enabled
    - Create, edit, delete annotations
    - Toggle chunk boundaries and quality badges
    - Test hover cards and reference panel
    - Test keyboard shortcuts
    - _Requirements: All requirements_


  - [ ] 18.2 Add loading states and skeletons
    - Show skeleton for Monaco while loading
    - Show skeleton for hover cards while fetching
    - Show loading indicators for API operations
    - _Requirements: 5.5_

  - [ ] 18.3 Polish animations and transitions
    - Smooth overlay show/hide transitions
    - Smooth panel slide animations
    - Smooth hover card fade-in
    - Smooth badge glow effects
    - _Requirements: All requirements (polish is cross-cutting)_

- [ ] 18.4 Write end-to-end tests
  - Test complete user workflows
  - Test error recovery
  - Test performance with realistic data
  - _Requirements: All requirements_

- [ ] 19. Documentation and cleanup
  - Write component documentation
  - Document API integration points
  - Document keyboard shortcuts
  - Update Phase 2 README
  - Clean up console logs and debug code
  - _Requirements: All requirements_

## Notes

- All tasks are required for comprehensive implementation
- Each task references specific requirements for traceability
- Monaco Editor is complex - expect iteration on decoration management
- Backend Node2Vec/graph endpoints are placeholders - implement fallbacks
- Phase 3 will integrate Library PDFs with reference overlay
- Property-based tests will be added after prework analysis
- All tests should use Vitest + React Testing Library + MSW for API mocking
- Use TanStack Query for all API calls to get automatic caching
- Follow Phase 1 patterns for store structure and component organization

