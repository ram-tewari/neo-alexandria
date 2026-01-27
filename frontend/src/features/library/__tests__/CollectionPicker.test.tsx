import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { CollectionPicker } from '../CollectionPicker';
import { useCollections } from '@/lib/hooks/useCollections';
import type { Collection } from '@/types/library';

// Mock dependencies
vi.mock('@/lib/hooks/useCollections', () => ({
  useCollections: vi.fn(),
}));

const mockCollections: Collection[] = [
  {
    id: 'col_1',
    name: 'Research Papers',
    description: 'Academic research',
    tags: ['research'],
    is_public: false,
    resource_count: 15,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-02T00:00:00Z',
  },
  {
    id: 'col_2',
    name: 'Code Samples',
    description: 'Code snippets',
    tags: ['code'],
    is_public: true,
    resource_count: 8,
    created_at: '2024-01-03T00:00:00Z',
    updated_at: '2024-01-04T00:00:00Z',
  },
  {
    id: 'col_3',
    name: 'Documentation',
    description: 'Docs',
    tags: ['docs'],
    is_public: false,
    resource_count: 12,
    created_at: '2024-01-05T00:00:00Z',
    updated_at: '2024-01-06T00:00:00Z',
  },
];

describe('CollectionPicker', () => {
  const mockOnSelect = vi.fn();
  const mockOnOpenChange = vi.fn();
  const mockCreateCollection = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();

    (useCollections as ReturnType<typeof vi.fn>).mockReturnValue({
      collections: mockCollections,
      isLoading: false,
      error: null,
      createCollection: mockCreateCollection,
      updateCollection: vi.fn(),
      deleteCollection: vi.fn(),
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
  });

  describe('Rendering', () => {
    it('renders when open', () => {
      render(
        <CollectionPicker
          open={true}
          onOpenChange={mockOnOpenChange}
          onSelect={mockOnSelect}
        />
      );

      expect(screen.getByText('Select Collections')).toBeInTheDocument();
    });

    it('does not render when closed', () => {
      render(
        <CollectionPicker
          open={false}
          onOpenChange={mockOnOpenChange}
          onSelect={mockOnSelect}
        />
      );

      expect(screen.queryByText('Select Collections')).not.toBeInTheDocument();
    });

    it('displays custom title', () => {
      render(
        <CollectionPicker
          open={true}
          onOpenChange={mockOnOpenChange}
          onSelect={mockOnSelect}
          title="Choose Collections"
        />
      );

      expect(screen.getByText('Choose Collections')).toBeInTheDocument();
    });

    it('displays all collections', () => {
      render(
        <CollectionPicker
          open={true}
          onOpenChange={mockOnOpenChange}
          onSelect={mockOnSelect}
        />
      );

      expect(screen.getByText('Research Papers')).toBeInTheDocument();
      expect(screen.getByText('Code Samples')).toBeInTheDocument();
      expect(screen.getByText('Documentation')).toBeInTheDocument();
    });

    it('displays resource counts', () => {
      render(
        <CollectionPicker
          open={true}
          onOpenChange={mockOnOpenChange}
          onSelect={mockOnSelect}
        />
      );

      expect(screen.getByText('15 documents')).toBeInTheDocument();
      expect(screen.getByText('8 documents')).toBeInTheDocument();
      expect(screen.getByText('12 documents')).toBeInTheDocument();
    });
  });

  describe('Search Functionality', () => {
    it('filters collections by search query', () => {
      render(
        <CollectionPicker
          open={true}
          onOpenChange={mockOnOpenChange}
          onSelect={mockOnSelect}
        />
      );

      const searchInput = screen.getByPlaceholderText('Search collections...');
      fireEvent.change(searchInput, { target: { value: 'code' } });

      expect(screen.getByText('Code Samples')).toBeInTheDocument();
      expect(screen.queryByText('Research Papers')).not.toBeInTheDocument();
      expect(screen.queryByText('Documentation')).not.toBeInTheDocument();
    });

    it('shows no results message when search has no matches', () => {
      render(
        <CollectionPicker
          open={true}
          onOpenChange={mockOnOpenChange}
          onSelect={mockOnSelect}
        />
      );

      const searchInput = screen.getByPlaceholderText('Search collections...');
      fireEvent.change(searchInput, { target: { value: 'nonexistent' } });

      expect(screen.getByText('No collections found')).toBeInTheDocument();
      expect(screen.getByText('Try a different search term')).toBeInTheDocument();
    });

    it('search is case-insensitive', () => {
      render(
        <CollectionPicker
          open={true}
          onOpenChange={mockOnOpenChange}
          onSelect={mockOnSelect}
        />
      );

      const searchInput = screen.getByPlaceholderText('Search collections...');
      fireEvent.change(searchInput, { target: { value: 'CODE' } });

      expect(screen.getByText('Code Samples')).toBeInTheDocument();
    });
  });

  describe('Multi-Select Mode', () => {
    it('allows selecting multiple collections', () => {
      render(
        <CollectionPicker
          open={true}
          onOpenChange={mockOnOpenChange}
          onSelect={mockOnSelect}
          multiSelect={true}
        />
      );

      const collection1 = screen.getByText('Research Papers').closest('div')!;
      const collection2 = screen.getByText('Code Samples').closest('div')!;

      fireEvent.click(collection1);
      fireEvent.click(collection2);

      expect(screen.getByText('2 selected')).toBeInTheDocument();
    });

    it('toggles selection on click', () => {
      render(
        <CollectionPicker
          open={true}
          onOpenChange={mockOnOpenChange}
          onSelect={mockOnSelect}
          multiSelect={true}
        />
      );

      const collection = screen.getByText('Research Papers').closest('div')!;

      fireEvent.click(collection);
      expect(screen.getByText('1 selected')).toBeInTheDocument();

      fireEvent.click(collection);
      expect(screen.getByText('0 selected')).toBeInTheDocument();
    });

    it('shows Add to Collections button in multi-select', () => {
      render(
        <CollectionPicker
          open={true}
          onOpenChange={mockOnOpenChange}
          onSelect={mockOnSelect}
          multiSelect={true}
        />
      );

      const collection = screen.getByText('Research Papers').closest('div')!;
      fireEvent.click(collection);

      expect(screen.getByRole('button', { name: /Add to Collections/i })).toBeInTheDocument();
    });
  });

  describe('Single-Select Mode', () => {
    it('allows selecting only one collection', () => {
      render(
        <CollectionPicker
          open={true}
          onOpenChange={mockOnOpenChange}
          onSelect={mockOnSelect}
          multiSelect={false}
        />
      );

      const collection1 = screen.getByText('Research Papers').closest('div')!;
      const collection2 = screen.getByText('Code Samples').closest('div')!;

      fireEvent.click(collection1);
      expect(screen.getByText('1 selected')).toBeInTheDocument();

      fireEvent.click(collection2);
      expect(screen.getByText('1 selected')).toBeInTheDocument();
    });

    it('shows Select button in single-select', () => {
      render(
        <CollectionPicker
          open={true}
          onOpenChange={mockOnOpenChange}
          onSelect={mockOnSelect}
          multiSelect={false}
        />
      );

      const collection = screen.getByText('Research Papers').closest('div')!;
      fireEvent.click(collection);

      expect(screen.getByRole('button', { name: /^Select$/i })).toBeInTheDocument();
    });

    it('submits on Enter key in single-select mode', () => {
      render(
        <CollectionPicker
          open={true}
          onOpenChange={mockOnOpenChange}
          onSelect={mockOnSelect}
          multiSelect={false}
        />
      );

      const collection = screen.getByText('Research Papers').closest('div')!;
      fireEvent.click(collection);

      const searchInput = screen.getByPlaceholderText('Search collections...');
      fireEvent.keyDown(searchInput, { key: 'Enter' });

      expect(mockOnSelect).toHaveBeenCalledWith(['col_1']);
      expect(mockOnOpenChange).toHaveBeenCalledWith(false);
    });
  });

  describe('Pre-selected Collections', () => {
    it('shows pre-selected collections', () => {
      render(
        <CollectionPicker
          open={true}
          onOpenChange={mockOnOpenChange}
          onSelect={mockOnSelect}
          selectedIds={['col_1', 'col_2']}
        />
      );

      expect(screen.getByText('2 selected')).toBeInTheDocument();
    });
  });

  describe('Inline Collection Creation', () => {
    it('shows create form when button clicked', () => {
      render(
        <CollectionPicker
          open={true}
          onOpenChange={mockOnOpenChange}
          onSelect={mockOnSelect}
        />
      );

      const createButton = screen.getByRole('button', { name: /Create New Collection/i });
      fireEvent.click(createButton);

      expect(screen.getByLabelText(/New Collection Name/i)).toBeInTheDocument();
    });

    it('creates collection with entered name', async () => {
      const newCollection: Collection = {
        id: 'col_new',
        name: 'New Collection',
        description: '',
        tags: [],
        is_public: false,
        resource_count: 0,
        created_at: '2024-01-07T00:00:00Z',
        updated_at: '2024-01-07T00:00:00Z',
      };

      mockCreateCollection.mockImplementation((_data, options) => {
        options?.onSuccess?.(newCollection);
      });

      render(
        <CollectionPicker
          open={true}
          onOpenChange={mockOnOpenChange}
          onSelect={mockOnSelect}
        />
      );

      // Open create form
      fireEvent.click(screen.getByRole('button', { name: /Create New Collection/i }));

      // Enter name
      const nameInput = screen.getByLabelText(/New Collection Name/i);
      fireEvent.change(nameInput, { target: { value: 'New Collection' } });

      // Submit
      const createButton = screen.getByRole('button', { name: /^Create$/i });
      fireEvent.click(createButton);

      await waitFor(() => {
        expect(mockCreateCollection).toHaveBeenCalledWith(
          { name: 'New Collection', is_public: false },
          expect.any(Object)
        );
      });
    });

    it('auto-selects newly created collection', async () => {
      const newCollection: Collection = {
        id: 'col_new',
        name: 'New Collection',
        description: '',
        tags: [],
        is_public: false,
        resource_count: 0,
        created_at: '2024-01-07T00:00:00Z',
        updated_at: '2024-01-07T00:00:00Z',
      };

      mockCreateCollection.mockImplementation((_data, options) => {
        options?.onSuccess?.(newCollection);
      });

      render(
        <CollectionPicker
          open={true}
          onOpenChange={mockOnOpenChange}
          onSelect={mockOnSelect}
        />
      );

      // Create collection
      fireEvent.click(screen.getByRole('button', { name: /Create New Collection/i }));
      const nameInput = screen.getByLabelText(/New Collection Name/i);
      fireEvent.change(nameInput, { target: { value: 'New Collection' } });
      fireEvent.click(screen.getByRole('button', { name: /^Create$/i }));

      await waitFor(() => {
        expect(screen.getByText('1 selected')).toBeInTheDocument();
      });
    });

    it('cancels create form', async () => {
      render(
        <CollectionPicker
          open={true}
          onOpenChange={mockOnOpenChange}
          onSelect={mockOnSelect}
        />
      );

      fireEvent.click(screen.getByRole('button', { name: /Create New Collection/i }));
      expect(screen.getByLabelText(/New Collection Name/i)).toBeInTheDocument();

      // Click the Cancel button in the create form (not the dialog footer)
      const cancelButtons = screen.getAllByRole('button', { name: /Cancel/i });
      // The create form cancel button should be the first one after the form appears
      const formCancelButton = cancelButtons[0];
      fireEvent.click(formCancelButton);

      // Wait for form to close
      await waitFor(() => {
        expect(screen.queryByLabelText(/New Collection Name/i)).not.toBeInTheDocument();
      });
    });

    it('submits on Enter key in create form', () => {
      render(
        <CollectionPicker
          open={true}
          onOpenChange={mockOnOpenChange}
          onSelect={mockOnSelect}
        />
      );

      fireEvent.click(screen.getByRole('button', { name: /Create New Collection/i }));
      
      const nameInput = screen.getByLabelText(/New Collection Name/i);
      fireEvent.change(nameInput, { target: { value: 'New Collection' } });
      fireEvent.keyDown(nameInput, { key: 'Enter' });

      expect(mockCreateCollection).toHaveBeenCalled();
    });

    it('cancels on Escape key in create form', () => {
      render(
        <CollectionPicker
          open={true}
          onOpenChange={mockOnOpenChange}
          onSelect={mockOnSelect}
        />
      );

      fireEvent.click(screen.getByRole('button', { name: /Create New Collection/i }));
      
      const nameInput = screen.getByLabelText(/New Collection Name/i);
      fireEvent.keyDown(nameInput, { key: 'Escape' });

      expect(screen.queryByLabelText(/New Collection Name/i)).not.toBeInTheDocument();
    });
  });

  describe('Loading State', () => {
    it('displays loading skeletons', () => {
      (useCollections as ReturnType<typeof vi.fn>).mockReturnValue({
        collections: [],
        isLoading: true,
        error: null,
        createCollection: mockCreateCollection,
        updateCollection: vi.fn(),
        deleteCollection: vi.fn(),
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

      render(
        <CollectionPicker
          open={true}
          onOpenChange={mockOnOpenChange}
          onSelect={mockOnSelect}
        />
      );

      // Check for skeleton loading elements by class
      const skeletons = document.querySelectorAll('.animate-pulse');
      expect(skeletons.length).toBeGreaterThan(0);
    });
  });

  describe('Submit and Cancel', () => {
    it('calls onSelect with selected IDs', () => {
      render(
        <CollectionPicker
          open={true}
          onOpenChange={mockOnOpenChange}
          onSelect={mockOnSelect}
        />
      );

      const collection = screen.getByText('Research Papers').closest('div')!;
      fireEvent.click(collection);

      const submitButton = screen.getByRole('button', { name: /Add to Collections/i });
      fireEvent.click(submitButton);

      expect(mockOnSelect).toHaveBeenCalledWith(['col_1']);
    });

    it('closes dialog after submit', () => {
      render(
        <CollectionPicker
          open={true}
          onOpenChange={mockOnOpenChange}
          onSelect={mockOnSelect}
        />
      );

      const collection = screen.getByText('Research Papers').closest('div')!;
      fireEvent.click(collection);

      const submitButton = screen.getByRole('button', { name: /Add to Collections/i });
      fireEvent.click(submitButton);

      expect(mockOnOpenChange).toHaveBeenCalledWith(false);
    });

    it('disables submit button when nothing selected', () => {
      render(
        <CollectionPicker
          open={true}
          onOpenChange={mockOnOpenChange}
          onSelect={mockOnSelect}
        />
      );

      const submitButton = screen.getByRole('button', { name: /Add to Collections/i });
      expect(submitButton).toBeDisabled();
    });

    it('calls onOpenChange when cancel clicked', () => {
      render(
        <CollectionPicker
          open={true}
          onOpenChange={mockOnOpenChange}
          onSelect={mockOnSelect}
        />
      );

      const cancelButton = screen.getAllByRole('button', { name: /Cancel/i })[0];
      fireEvent.click(cancelButton);

      expect(mockOnOpenChange).toHaveBeenCalledWith(false);
    });
  });
});
