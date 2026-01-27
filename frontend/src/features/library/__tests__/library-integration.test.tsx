import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { LibraryPage } from '../LibraryPage';
import { useDocuments } from '@/lib/hooks/useDocuments';
import { useCollections } from '@/lib/hooks/useCollections';
import { useScholarlyAssets } from '@/lib/hooks/useScholarlyAssets';
import { useAutoLinking } from '@/lib/hooks/useAutoLinking';
import { usePDFViewer } from '@/lib/hooks/usePDFViewer';
import { useCollectionsStore } from '@/stores/collections';
import { usePDFViewerStore } from '@/stores/pdfViewer';
import { useLibraryStore } from '@/stores/library';
import type { Document, Collection } from '@/types/library';

/**
 * Integration tests for the complete Library workflow
 * Tests the interaction between all components and stores
 */

// Mock all hooks
vi.mock('@/lib/hooks/useDocuments');
vi.mock('@/lib/hooks/useCollections');
vi.mock('@/lib/hooks/useScholarlyAssets');
vi.mock('@/lib/hooks/useAutoLinking');
vi.mock('@/lib/hooks/usePDFViewer');

// Mock stores
vi.mock('@/stores/collections');
vi.mock('@/stores/pdfViewer');
vi.mock('@/stores/library');

// Mock UI components to simplify testing
vi.mock('@/components/ui/tabs', () => ({
  Tabs: ({ children }: any) => <div>{children}</div>,
  TabsContent: ({ children, value }: any) => <div data-tab-content={value}>{children}</div>,
  TabsList: ({ children }: any) => <div>{children}</div>,
  TabsTrigger: ({ children, value }: any) => (
    <button role="tab" data-value={value}>{children}</button>
  ),
}));

vi.mock('@/components/ui/resizable', () => ({
  ResizablePanelGroup: ({ children }: any) => <div>{children}</div>,
  ResizablePanel: ({ children }: any) => <div>{children}</div>,
  ResizableHandle: () => null,
}));

vi.mock('@/components/ui/scroll-area', () => ({
  ScrollArea: ({ children }: any) => <div>{children}</div>,
}));

// Mock child components with realistic behavior
vi.mock('../DocumentGrid', () => ({
  DocumentGrid: ({ documents, onDocumentSelect }: any) => (
    <div data-testid="document-grid">
      {documents.map((doc: Document) => (
        <button key={doc.id} onClick={() => onDocumentSelect(doc)}>
          {doc.title}
        </button>
      ))}
    </div>
  ),
}));

vi.mock('../DocumentFilters', () => ({
  DocumentFilters: () => <div data-testid="document-filters">Filters</div>,
}));

vi.mock('../DocumentUpload', () => ({
  DocumentUpload: ({ open, onOpenChange }: any) => 
    open ? (
      <div data-testid="document-upload">
        <button onClick={() => onOpenChange(false)}>Close Upload</button>
      </div>
    ) : null,
}));

vi.mock('../CollectionManager', () => ({
  CollectionManager: ({ onCollectionSelect }: any) => (
    <div data-testid="collection-manager">
      <button onClick={() => onCollectionSelect('col_1')}>My Collection</button>
    </div>
  ),
}));

vi.mock('../BatchOperations', () => ({
  BatchOperations: () => <div data-testid="batch-operations">Batch Operations</div>,
}));

vi.mock('../PDFViewer', () => ({
  PDFViewer: ({ document }: any) => (
    <div data-testid="pdf-viewer">Viewing: {document.title}</div>
  ),
}));

vi.mock('../EquationDrawer', () => ({
  EquationDrawer: ({ documentId }: any) => (
    <div data-testid="equation-drawer">Equations for {documentId}</div>
  ),
}));

vi.mock('../TableDrawer', () => ({
  TableDrawer: ({ documentId }: any) => (
    <div data-testid="table-drawer">Tables for {documentId}</div>
  ),
}));

vi.mock('../MetadataPanel', () => ({
  MetadataPanel: ({ document }: any) => (
    <div data-testid="metadata-panel">Metadata for {document.title}</div>
  ),
}));

vi.mock('../RelatedCodePanel', () => ({
  RelatedCodePanel: ({ documentId }: any) => (
    <div data-testid="related-code-panel">Related code for {documentId}</div>
  ),
}));

vi.mock('../RelatedPapersPanel', () => ({
  RelatedPapersPanel: ({ documentId }: any) => (
    <div data-testid="related-papers-panel">Related papers for {documentId}</div>
  ),
}));

const mockDocuments: Document[] = [
  {
    id: 'doc_1',
    title: 'Machine Learning Paper',
    type: 'pdf',
    url: 'https://example.com/ml.pdf',
    uploadedAt: '2024-01-01T00:00:00Z',
    size: 1024000,
    qualityScore: 85,
  },
  {
    id: 'doc_2',
    title: 'Deep Learning Research',
    type: 'pdf',
    url: 'https://example.com/dl.pdf',
    uploadedAt: '2024-01-02T00:00:00Z',
    size: 2048000,
    qualityScore: 90,
  },
];

describe('Library Integration Tests', () => {
  const mockSetCurrentDocument = vi.fn();
  const mockRefetch = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();

    // Mock useDocuments
    (useDocuments as ReturnType<typeof vi.fn>).mockReturnValue({
      documents: mockDocuments,
      isLoading: false,
      error: null,
      total: 2,
      refetch: mockRefetch,
    });

    // Mock useCollectionsStore
    (useCollectionsStore as unknown as ReturnType<typeof vi.fn>).mockImplementation((selector) => {
      const state = {
        batchMode: false,
        selectedDocuments: [],
        toggleBatchMode: vi.fn(),
        selectDocument: vi.fn(),
      };
      return selector ? selector(state) : state;
    });

    // Mock usePDFViewerStore
    (usePDFViewerStore as unknown as ReturnType<typeof vi.fn>).mockImplementation((selector) => {
      const state = {
        currentDocument: null,
        setCurrentDocument: mockSetCurrentDocument,
      };
      return selector ? selector(state) : state;
    });

    (usePDFViewerStore as any).getState = vi.fn(() => ({
      setCurrentDocument: mockSetCurrentDocument,
    }));
  });

  describe('Complete Document Workflow', () => {
    it('allows user to browse, filter, and select documents', async () => {
      render(<LibraryPage />);

      // User sees document grid
      expect(screen.getByTestId('document-grid')).toBeInTheDocument();
      expect(screen.getByText('Machine Learning Paper')).toBeInTheDocument();
      expect(screen.getByText('Deep Learning Research')).toBeInTheDocument();

      // User can see filters
      expect(screen.getByTestId('document-filters')).toBeInTheDocument();

      // User selects a document
      fireEvent.click(screen.getByText('Machine Learning Paper'));

      // Document is set as current
      expect(mockSetCurrentDocument).toHaveBeenCalledWith(mockDocuments[0]);
    });

    it('shows PDF viewer and metadata when document selected', async () => {
      // Mock document selection
      (usePDFViewerStore as unknown as ReturnType<typeof vi.fn>).mockImplementation((selector) => {
        const state = {
          currentDocument: mockDocuments[0],
          setCurrentDocument: mockSetCurrentDocument,
        };
        return selector ? selector(state) : state;
      });

      render(<LibraryPage />);

      // PDF viewer is shown
      expect(screen.getByTestId('pdf-viewer')).toBeInTheDocument();
      expect(screen.getByText('Viewing: Machine Learning Paper')).toBeInTheDocument();

      // All tabs are available
      expect(screen.getByRole('tab', { name: /PDF Viewer/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /Metadata/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /Equations/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /Tables/i })).toBeInTheDocument();
    });

    it('allows switching between different document views', async () => {
      (usePDFViewerStore as unknown as ReturnType<typeof vi.fn>).mockImplementation((selector) => {
        const state = {
          currentDocument: mockDocuments[0],
          setCurrentDocument: mockSetCurrentDocument,
        };
        return selector ? selector(state) : state;
      });

      render(<LibraryPage />);

      // Switch to metadata tab
      fireEvent.click(screen.getByRole('tab', { name: /Metadata/i }));
      await waitFor(() => {
        expect(screen.getByTestId('metadata-panel')).toBeInTheDocument();
      });

      // Switch to equations tab
      fireEvent.click(screen.getByRole('tab', { name: /Equations/i }));
      await waitFor(() => {
        expect(screen.getByTestId('equation-drawer')).toBeInTheDocument();
      });

      // Switch to tables tab
      fireEvent.click(screen.getByRole('tab', { name: /Tables/i }));
      await waitFor(() => {
        expect(screen.getByTestId('table-drawer')).toBeInTheDocument();
      });
    });
  });

  describe('Collection Management Workflow', () => {
    it('allows switching to collections view', () => {
      render(<LibraryPage />);

      // Switch to collections view
      fireEvent.click(screen.getByRole('button', { name: /Collections/i }));

      // Collection manager is shown
      expect(screen.getByTestId('collection-manager')).toBeInTheDocument();
      expect(screen.queryByTestId('document-grid')).not.toBeInTheDocument();
    });

    it('allows selecting collections and viewing documents', () => {
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {});

      render(<LibraryPage />);

      // Switch to collections view
      fireEvent.click(screen.getByRole('button', { name: /Collections/i }));

      // Select a collection
      fireEvent.click(screen.getByText('My Collection'));

      // Collection is selected
      expect(consoleSpy).toHaveBeenCalledWith('Selected collection:', 'col_1');

      consoleSpy.mockRestore();
    });

    it('can switch back to document grid from collections', () => {
      render(<LibraryPage />);

      // Switch to collections
      fireEvent.click(screen.getByRole('button', { name: /Collections/i }));
      expect(screen.getByTestId('collection-manager')).toBeInTheDocument();

      // Switch back to documents
      fireEvent.click(screen.getByRole('button', { name: /Documents/i }));
      expect(screen.getByTestId('document-grid')).toBeInTheDocument();
      expect(screen.queryByTestId('collection-manager')).not.toBeInTheDocument();
    });
  });

  describe('Batch Operations Workflow', () => {
    it('shows batch operations when batch mode enabled', () => {
      (useCollectionsStore as unknown as ReturnType<typeof vi.fn>).mockImplementation((selector) => {
        const state = {
          batchMode: true,
          selectedDocuments: ['doc_1', 'doc_2'],
          toggleBatchMode: vi.fn(),
          selectDocument: vi.fn(),
        };
        return selector ? selector(state) : state;
      });

      render(<LibraryPage />);

      expect(screen.getByTestId('batch-operations')).toBeInTheDocument();
    });

    it('hides batch operations when batch mode disabled', () => {
      render(<LibraryPage />);

      expect(screen.queryByTestId('batch-operations')).not.toBeInTheDocument();
    });
  });

  describe('Upload Workflow', () => {
    it('opens upload dialog and allows closing', () => {
      render(<LibraryPage />);

      // Open upload dialog
      fireEvent.click(screen.getByRole('button', { name: /Upload/i }));
      expect(screen.getByTestId('document-upload')).toBeInTheDocument();

      // Close upload dialog
      fireEvent.click(screen.getByText('Close Upload'));
      expect(screen.queryByTestId('document-upload')).not.toBeInTheDocument();
    });
  });

  describe('Scholarly Assets Integration', () => {
    it('shows equations panel for selected document', async () => {
      (usePDFViewerStore as unknown as ReturnType<typeof vi.fn>).mockImplementation((selector) => {
        const state = {
          currentDocument: mockDocuments[0],
          setCurrentDocument: mockSetCurrentDocument,
        };
        return selector ? selector(state) : state;
      });

      render(<LibraryPage />);

      // Switch to equations tab
      fireEvent.click(screen.getByRole('tab', { name: /Equations/i }));

      await waitFor(() => {
        expect(screen.getByTestId('equation-drawer')).toBeInTheDocument();
        expect(screen.getByText('Equations for doc_1')).toBeInTheDocument();
      });
    });

    it('shows tables panel for selected document', async () => {
      (usePDFViewerStore as unknown as ReturnType<typeof vi.fn>).mockImplementation((selector) => {
        const state = {
          currentDocument: mockDocuments[0],
          setCurrentDocument: mockSetCurrentDocument,
        };
        return selector ? selector(state) : state;
      });

      render(<LibraryPage />);

      // Switch to tables tab
      fireEvent.click(screen.getByRole('tab', { name: /Tables/i }));

      await waitFor(() => {
        expect(screen.getByTestId('table-drawer')).toBeInTheDocument();
        expect(screen.getByText('Tables for doc_1')).toBeInTheDocument();
      });
    });

    it('shows metadata panel for selected document', async () => {
      (usePDFViewerStore as unknown as ReturnType<typeof vi.fn>).mockImplementation((selector) => {
        const state = {
          currentDocument: mockDocuments[0],
          setCurrentDocument: mockSetCurrentDocument,
        };
        return selector ? selector(state) : state;
      });

      render(<LibraryPage />);

      // Switch to metadata tab
      fireEvent.click(screen.getByRole('tab', { name: /Metadata/i }));

      await waitFor(() => {
        expect(screen.getByTestId('metadata-panel')).toBeInTheDocument();
        expect(screen.getByText('Metadata for Machine Learning Paper')).toBeInTheDocument();
      });
    });
  });

  describe('Auto-Linking Integration', () => {
    it('shows related code panel for selected document', async () => {
      (usePDFViewerStore as unknown as ReturnType<typeof vi.fn>).mockImplementation((selector) => {
        const state = {
          currentDocument: mockDocuments[0],
          setCurrentDocument: mockSetCurrentDocument,
        };
        return selector ? selector(state) : state;
      });

      render(<LibraryPage />);

      // Switch to related code tab
      fireEvent.click(screen.getByRole('tab', { name: /Related Code/i }));

      await waitFor(() => {
        expect(screen.getByTestId('related-code-panel')).toBeInTheDocument();
        expect(screen.getByText('Related code for doc_1')).toBeInTheDocument();
      });
    });

    it('shows related papers panel for selected document', async () => {
      (usePDFViewerStore as unknown as ReturnType<typeof vi.fn>).mockImplementation((selector) => {
        const state = {
          currentDocument: mockDocuments[0],
          setCurrentDocument: mockSetCurrentDocument,
        };
        return selector ? selector(state) : state;
      });

      render(<LibraryPage />);

      // Switch to related papers tab
      fireEvent.click(screen.getByRole('tab', { name: /Related Papers/i }));

      await waitFor(() => {
        expect(screen.getByTestId('related-papers-panel')).toBeInTheDocument();
        expect(screen.getByText('Related papers for doc_1')).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('handles document loading errors gracefully', () => {
      (useDocuments as ReturnType<typeof vi.fn>).mockReturnValue({
        documents: [],
        isLoading: false,
        error: new Error('Failed to load documents'),
        total: 0,
        refetch: mockRefetch,
      });

      render(<LibraryPage />);

      // Page still renders
      expect(screen.getByText('Library')).toBeInTheDocument();
      expect(screen.getByTestId('document-grid')).toBeInTheDocument();
    });

    it('handles loading state', () => {
      (useDocuments as ReturnType<typeof vi.fn>).mockReturnValue({
        documents: [],
        isLoading: true,
        error: null,
        total: 0,
        refetch: mockRefetch,
      });

      render(<LibraryPage />);

      // Page renders with loading state
      expect(screen.getByText('Library')).toBeInTheDocument();
      expect(screen.getByTestId('document-grid')).toBeInTheDocument();
    });
  });

  describe('State Persistence', () => {
    it('maintains selected document when switching views', () => {
      (usePDFViewerStore as unknown as ReturnType<typeof vi.fn>).mockImplementation((selector) => {
        const state = {
          currentDocument: mockDocuments[0],
          setCurrentDocument: mockSetCurrentDocument,
        };
        return selector ? selector(state) : state;
      });

      render(<LibraryPage />);

      // Document is selected
      expect(screen.getByTestId('pdf-viewer')).toBeInTheDocument();

      // Switch to collections view
      fireEvent.click(screen.getByRole('button', { name: /Collections/i }));

      // PDF viewer still shown (document remains selected)
      expect(screen.getByTestId('pdf-viewer')).toBeInTheDocument();
    });
  });
});
