# Library Feature

This directory contains all components and logic for the Living Library feature (Phase 3).

## Structure

```
library/
├── __tests__/              # Component tests
├── DocumentCard.tsx        # Individual document card
├── DocumentGrid.tsx        # Main grid view
├── DocumentUpload.tsx      # Upload interface
├── DocumentFilters.tsx     # Filter controls
├── PDFViewer.tsx          # PDF viewing component
├── PDFToolbar.tsx         # Zoom, navigation controls
├── PDFHighlighter.tsx     # Text highlighting
├── EquationDrawer.tsx     # Equation panel
├── TableDrawer.tsx        # Table panel
├── MetadataPanel.tsx      # Metadata display/edit
├── RelatedCodePanel.tsx   # Auto-linked code files
├── RelatedPapersPanel.tsx # Auto-linked papers
├── CollectionManager.tsx  # Collection CRUD
├── CollectionPicker.tsx   # Collection selection dialog
├── CollectionStats.tsx    # Statistics dashboard
└── BatchOperations.tsx    # Batch action toolbar
```

## Dependencies

- **react-pdf**: PDF rendering
- **pdfjs-dist**: PDF.js library
- **katex**: LaTeX equation rendering
- **react-katex**: React wrapper for KaTeX
- **react-window**: Virtual scrolling for large lists
- **react-dropzone**: File upload with drag-and-drop

## Configuration

### PDF.js Worker

The PDF.js worker is configured in `src/lib/pdf/worker.ts` and imported in `main.tsx`.
It uses a CDN-hosted worker to avoid bundling issues.

### KaTeX Styles

KaTeX CSS is imported in `src/lib/katex/styles.ts` and loaded in `main.tsx`.

## Usage

Components in this directory integrate with:
- **API Layer**: `src/lib/api/library.ts`, `src/lib/api/scholarly.ts`, `src/lib/api/collections.ts`
- **State Management**: `src/stores/library.ts`, `src/stores/pdfViewer.ts`, `src/stores/collections.ts`
- **Custom Hooks**: `src/lib/hooks/useDocuments.ts`, `src/lib/hooks/usePDFViewer.ts`, etc.

## Testing

All components have corresponding tests in the `__tests__/` directory.
Run tests with: `npm test`

## Related Documentation

- [Phase 3 Requirements](../../../../.kiro/specs/frontend/phase3-living-library/requirements.md)
- [Phase 3 Design](../../../../.kiro/specs/frontend/phase3-living-library/design.md)
- [Phase 3 Tasks](../../../../.kiro/specs/frontend/phase3-living-library/tasks.md)
