import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { CollectionManager } from '../CollectionManager';
import { useCollections } from '@/lib/hooks/useCollections';
import { useCollectionsStore } from '@/stores/collections';
import type { Collection } from '@/types/library';

// Mock dependencies
vi.mock('@/lib/hooks/useCollections', () => ({
  useCollections: vi.fn(),
}));
vi.mock('@/stores/collections', () => ({
  useCollectionsStore: vi.fn(),
}));

const mockCollections: Collection[] = [
  {
    id: 'col_1',
    name: 'Research Papers',
    description: 'Academic research collection',
    tags: ['research', 'academic', 'papers'],
    is_public: false,
    resource_count: 15,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-02T00:00:00Z',
  },
  {
    id: 'col_2',
    name: 'Code Samples',
    description: 'Useful code snippets',
    tags: ['code', 'examples'],
    is_public: true,
    resource_count: 8,
    created_at: '2024-01-03T00:00:00Z',
    updated_at: '2024-01-04T00:00:00Z',
  },
];

describe('CollectionManager', () => {
  const mockCreateCollection = vi.fn();
  const mockUpdateCollection = vi.fn();
  const mockDeleteCollection = vi.fn();
  const mockSelectCollection = vi.fn();
  const mockOnCollectionSelect = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();

    // Mock useCollections hook
    (useCollections as ReturnType<typeof vi.fn>).mockReturnValue({
      collections: mockCollections,
      isLoading: false,
      error: null,
      createCollection: mockCreateCollection,
      updateCollection: mockUpdateCollection,
      deleteCollection: mockDeleteCollection,
      isCreating: false,
      isUpdating: false,
      isDeleting: false,
      total: mockCollections.length,
      createError: null,
      updateError: null,
      deleteError: null,
      batchAddError: null,
      batchRemoveError: null,
      batchAddResources: vi.fn(),
      batchRemoveResources: vi.fn(),
      isBatchAdding: false,
      isBatchRemoving: false,
      refetch: vi.fn(),
    });

    // Mock useCollectionsStore hook
    (useCollectionsStore as ReturnType<typeof vi.fn>).mockReturnValue({
      selectCollection: mockSelectCollection,
      collections: mockCollections,
      selectedCollection: null,
      selectedResourceIds: new Set(),
      batchMode: false,
      setCollections: vi.fn(),
      addCollection: vi.fn(),
      updateCollection: vi.fn(),
      removeCollection: vi.fn(),
      toggleResourceSelection: vi.fn(),
      clearSelection: vi.fn(),
      selectAll: vi.fn(),
      isResourceSelected: vi.fn(),
      enableBatchMode: vi.fn(),
      disableBatchMode: vi.fn(),
      toggleBatchMode: vi.fn(),
    });
  });

  describe('Rendering', () => {
    it('renders collection list', () => {
      render(<CollectionManager />);

      expect(screen.getByText('Collections')).toBeInTheDocument();
      expect(screen.getByText('Research Papers')).toBeInTheDocument();
      expect(screen.getByText('Code Samples')).toBeInTheDocument();
    });

    it('displays collection count badge', () => {
      render(<CollectionManager />);

      const badge = screen.getByText('2');
      expect(badge).toBeInTheDocument();
    });

    it('displays collection statistics', () => {
      render(<CollectionManager />);

      expect(screen.getByText('15 documents')).toBeInTheDocument();
      expect(screen.getByText('8 documents')).toBeInTheDocument();
    });

    it('displays collection tags', () => {
      render(<CollectionManager />);

      expect(screen.getByText('research')).toBeInTheDocument();
      expect(screen.getByText('academic')).toBeInTheDocument();
      expect(screen.getByText('code')).toBeInTheDocument();
    });

    it('shows public/private indicators', () => {
      render(<CollectionManager />);

      // Check for Lock icon (private) or Globe icon (public) by checking for SVG elements with title
      const lockIcons = screen.getAllByTitle('Private');
      expect(lockIcons.length).toBeGreaterThan(0);
    });
  });

  describe('Loading State', () => {
    it('displays loading skeletons', () => {
      (useCollections as ReturnType<typeof vi.fn>).mockReturnValue({
        collections: [],
        isLoading: true,
        error: null,
        createCollection: mockCreateCollection,
        updateCollection: mockUpdateCollection,
        deleteCollection: mockDeleteCollection,
        isCreating: false,
        isUpdating: false,
        isDeleting: false,
        total: 0,
        createError: null,
        updateError: null,
        deleteError: null,
        batchAddError: null,
        batchRemoveError: null,
        batchAddResources: vi.fn(),
        batchRemoveResources: vi.fn(),
        isBatchAdding: false,
        isBatchRemoving: false,
        refetch: vi.fn(),
      });

      render(<CollectionManager />);

      // Check for skeleton loading elements by class
      const skeletons = document.querySelectorAll('.animate-pulse');
      expect(skeletons.length).toBeGreaterThan(0);
    });
  });

  describe('Error State', () => {
    it('displays error message', () => {
      (useCollections as ReturnType<typeof vi.fn>).mockReturnValue({
        collections: [],
        isLoading: false,
        error: new Error('Failed to load'),
        createCollection: mockCreateCollection,
        updateCollection: mockUpdateCollection,
        deleteCollection: mockDeleteCollection,
        isCreating: false,
        isUpdating: false,
        isDeleting: false,
        total: 0,
        createError: null,
        updateError: null,
        deleteError: null,
        batchAddError: null,
        batchRemoveError: null,
        batchAddResources: vi.fn(),
        batchRemoveResources: vi.fn(),
        isBatchAdding: false,
        isBatchRemoving: false,
        refetch: vi.fn(),
      });

      render(<CollectionManager />);

      expect(screen.getByText(/Failed to load collections/i)).toBeInTheDocument();
    });
  });

  describe('Empty State', () => {
    it('displays empty state message', () => {
      (useCollections as ReturnType<typeof vi.fn>).mockReturnValue({
        collections: [],
        isLoading: false,
        error: null,
        createCollection: mockCreateCollection,
        updateCollection: mockUpdateCollection,
        deleteCollection: mockDeleteCollection,
        isCreating: false,
        isUpdating: false,
        isDeleting: false,
        total: 0,
        createError: null,
        updateError: null,
        deleteError: null,
        batchAddError: null,
        batchRemoveError: null,
        batchAddResources: vi.fn(),
        batchRemoveResources: vi.fn(),
        isBatchAdding: false,
        isBatchRemoving: false,
        refetch: vi.fn(),
      });

      render(<CollectionManager />);

      expect(screen.getByText('No collections yet')).toBeInTheDocument();
      expect(screen.getByText(/Create your first collection/i)).toBeInTheDocument();
    });
  });

  describe('Create Collection', () => {
    it('opens create dialog when New button clicked', () => {
      render(<CollectionManager />);

      const newButton = screen.getByRole('button', { name: /New/i });
      fireEvent.click(newButton);

      expect(screen.getByText('Create Collection')).toBeInTheDocument();
    });

    it('creates collection with valid data', async () => {
      mockCreateCollection.mockImplementation((_data, options) => {
        options?.onSuccess?.();
      });

      render(<CollectionManager />);

      // Open dialog
      fireEvent.click(screen.getByRole('button', { name: /New/i }));

      // Fill form
      const nameInput = screen.getByLabelText(/Name/i);
      fireEvent.change(nameInput, { target: { value: 'New Collection' } });

      const descInput = screen.getByLabelText(/Description/i);
      fireEvent.change(descInput, { target: { value: 'Test description' } });

      // Submit
      const createButton = screen.getByRole('button', { name: /^Create$/i });
      fireEvent.click(createButton);

      await waitFor(() => {
        expect(mockCreateCollection).toHaveBeenCalledWith(
          expect.objectContaining({
            name: 'New Collection',
            description: 'Test description',
          }),
          expect.any(Object)
        );
      });
    });

    it('disables create button when name is empty', () => {
      render(<CollectionManager />);

      fireEvent.click(screen.getByRole('button', { name: /New/i }));

      const createButton = screen.getByRole('button', { name: /^Create$/i });
      expect(createButton).toBeDisabled();
    });
  });

  describe('Edit Collection', () => {
    it('opens edit dialog when Edit button clicked', () => {
      render(<CollectionManager />);

      const editButtons = screen.getAllByRole('button', { name: '' });
      const editButton = editButtons.find(btn => btn.querySelector('svg'));
      if (editButton) {
        fireEvent.click(editButton);
      }

      expect(screen.getByText('Edit Collection')).toBeInTheDocument();
    });

    it('pre-fills form with collection data', () => {
      render(<CollectionManager />);

      // Click first edit button
      const editButtons = screen.getAllByRole('button', { name: '' });
      const editButton = editButtons[0];
      fireEvent.click(editButton);

      const nameInput = screen.getByDisplayValue('Research Papers');
      expect(nameInput).toBeInTheDocument();
    });

    it('updates collection with new data', async () => {
      mockUpdateCollection.mockImplementation((_data, options) => {
        options?.onSuccess?.();
      });

      render(<CollectionManager />);

      // Open edit dialog
      const editButtons = screen.getAllByRole('button', { name: '' });
      fireEvent.click(editButtons[0]);

      // Update name
      const nameInput = screen.getByDisplayValue('Research Papers');
      fireEvent.change(nameInput, { target: { value: 'Updated Name' } });

      // Submit
      const saveButton = screen.getByRole('button', { name: /Save/i });
      fireEvent.click(saveButton);

      await waitFor(() => {
        expect(mockUpdateCollection).toHaveBeenCalled();
      });
    });
  });

  describe('Delete Collection', () => {
    it('opens delete dialog when Delete button clicked', () => {
      render(<CollectionManager />);

      const deleteButtons = screen.getAllByRole('button', { name: '' });
      const deleteButton = deleteButtons[deleteButtons.length - 1];
      fireEvent.click(deleteButton);

      expect(screen.getByText('Delete Collection')).toBeInTheDocument();
    });

    it('shows collection name in confirmation', () => {
      render(<CollectionManager />);

      const deleteButtons = screen.getAllByRole('button', { name: '' });
      fireEvent.click(deleteButtons[deleteButtons.length - 1]);

      expect(screen.getByText(/Research Papers/i)).toBeInTheDocument();
    });

    it('deletes collection when confirmed', async () => {
      mockDeleteCollection.mockImplementation((_id, options) => {
        options?.onSuccess?.();
      });

      render(<CollectionManager />);

      // Find all collection cards
      const researchPapersCard = screen.getByText('Research Papers').closest('.p-3');
      expect(researchPapersCard).toBeInTheDocument();
      
      // Find the delete button within the first collection card (has Trash2 icon)
      const deleteButtons = researchPapersCard!.querySelectorAll('button');
      const deleteButton = Array.from(deleteButtons).find(btn => 
        btn.querySelector('svg.lucide-trash2, svg.lucide-trash-2')
      );
      
      expect(deleteButton).toBeInTheDocument();
      fireEvent.click(deleteButton!);

      // Confirm
      const confirmButton = screen.getByRole('button', { name: /^Delete$/i });
      fireEvent.click(confirmButton);

      await waitFor(() => {
        expect(mockDeleteCollection).toHaveBeenCalledWith('col_1', expect.any(Object));
      });
    });
  });

  describe('Collection Selection', () => {
    it('calls selectCollection when collection clicked', () => {
      render(<CollectionManager />);

      const collection = screen.getByText('Research Papers');
      fireEvent.click(collection.closest('div')!);

      expect(mockSelectCollection).toHaveBeenCalledWith(mockCollections[0]);
    });

    it('calls onCollectionSelect callback', () => {
      render(<CollectionManager onCollectionSelect={mockOnCollectionSelect} />);

      const collection = screen.getByText('Research Papers');
      fireEvent.click(collection.closest('div')!);

      expect(mockOnCollectionSelect).toHaveBeenCalledWith(mockCollections[0]);
    });
  });

  describe('Dialog Interactions', () => {
    it('closes create dialog on cancel', () => {
      render(<CollectionManager />);

      fireEvent.click(screen.getByRole('button', { name: /New/i }));
      expect(screen.getByText('Create Collection')).toBeInTheDocument();

      fireEvent.click(screen.getByRole('button', { name: /Cancel/i }));
      
      waitFor(() => {
        expect(screen.queryByText('Create Collection')).not.toBeInTheDocument();
      });
    });

    it('closes edit dialog on cancel', () => {
      render(<CollectionManager />);

      const editButtons = screen.getAllByRole('button', { name: '' });
      fireEvent.click(editButtons[0]);
      expect(screen.getByText('Edit Collection')).toBeInTheDocument();

      fireEvent.click(screen.getByRole('button', { name: /Cancel/i }));
      
      waitFor(() => {
        expect(screen.queryByText('Edit Collection')).not.toBeInTheDocument();
      });
    });
  });
});
