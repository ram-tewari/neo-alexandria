/**
 * AnnotationPanel Component Tests
 * 
 * Tests for the annotation panel component including:
 * - Annotation list rendering
 * - Create/edit/delete flows
 * - Search functionality
 * - Panel open/close
 * 
 * Requirements: 4.1, 4.4, 4.6, 4.7, 8.3
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AnnotationPanel } from '../AnnotationPanel';
import { useAnnotationStore } from '@/stores/annotation';
import { useEditorStore } from '@/stores/editor';
import type { Annotation } from '../types';

// Mock stores
vi.mock('@/stores/annotation');
vi.mock('@/stores/editor');

describe('AnnotationPanel', () => {
  // ==========================================================================
  // Test Data
  // ==========================================================================

  const mockAnnotations: Annotation[] = [
    {
      id: 'ann-1',
      resource_id: 'resource-1',
      user_id: 'user-1',
      start_offset: 0,
      end_offset: 10,
      highlighted_text: 'const x = 1',
      note: 'This is a variable declaration',
      tags: ['variable', 'const'],
      color: '#3b82f6',
      is_shared: false,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    },
    {
      id: 'ann-2',
      resource_id: 'resource-1',
      user_id: 'user-1',
      start_offset: 20,
      end_offset: 30,
      highlighted_text: 'function foo',
      note: 'Main function',
      tags: ['function', 'important'],
      color: '#10b981',
      is_shared: false,
      created_at: '2024-01-02T00:00:00Z',
      updated_at: '2024-01-02T00:00:00Z',
    },
    {
      id: 'ann-3',
      resource_id: 'resource-1',
      user_id: 'user-1',
      start_offset: 40,
      end_offset: 50,
      highlighted_text: 'return value',
      color: '#f59e0b',
      is_shared: false,
      created_at: '2024-01-03T00:00:00Z',
      updated_at: '2024-01-03T00:00:00Z',
    },
  ];

  const mockAnnotationStore = {
    annotations: mockAnnotations,
    selectedAnnotation: null,
    isCreating: false,
    isLoading: false,
    error: null,
    selectAnnotation: vi.fn(),
    setIsCreating: vi.fn(),
    fetchAnnotations: vi.fn(),
    createAnnotation: vi.fn(),
    updateAnnotation: vi.fn(),
    deleteAnnotation: vi.fn(),
  };

  const mockEditorStore = {
    updateCursorPosition: vi.fn(),
    selection: {
      start: { line: 1, column: 0 },
      end: { line: 1, column: 10 },
    },
  };

  beforeEach(() => {
    vi.clearAllMocks();
    
    // Mock annotation store
    vi.mocked(useAnnotationStore).mockReturnValue(mockAnnotationStore);
    
    // Mock editor store
    vi.mocked(useEditorStore).mockReturnValue(mockEditorStore);
  });

  // ==========================================================================
  // Rendering Tests
  // ==========================================================================

  describe('Rendering', () => {
    it('should render panel when open', () => {
      render(
        <AnnotationPanel
          open={true}
          onOpenChange={vi.fn()}
          resourceId="resource-1"
        />
      );

      expect(screen.getByText('Annotations')).toBeInTheDocument();
      expect(
        screen.getByText('View and manage your annotations for this file')
      ).toBeInTheDocument();
    });

    it('should not render panel when closed', () => {
      render(
        <AnnotationPanel
          open={false}
          onOpenChange={vi.fn()}
          resourceId="resource-1"
        />
      );

      expect(screen.queryByText('Annotations')).not.toBeInTheDocument();
    });

    it('should render create button', () => {
      render(
        <AnnotationPanel
          open={true}
          onOpenChange={vi.fn()}
          resourceId="resource-1"
        />
      );

      expect(
        screen.getByRole('button', { name: /create new annotation/i })
      ).toBeInTheDocument();
    });

    it('should render empty state when no annotations', () => {
      vi.mocked(useAnnotationStore).mockReturnValue({
        ...mockAnnotationStore,
        annotations: [],
      });

      render(
        <AnnotationPanel
          open={true}
          onOpenChange={vi.fn()}
          resourceId="resource-1"
        />
      );

      expect(screen.getByText('No annotations yet')).toBeInTheDocument();
      expect(
        screen.getByText(/select text in the editor to create your first annotation/i)
      ).toBeInTheDocument();
    });

    it('should render loading state', () => {
      vi.mocked(useAnnotationStore).mockReturnValue({
        ...mockAnnotationStore,
        isLoading: true,
      });

      render(
        <AnnotationPanel
          open={true}
          onOpenChange={vi.fn()}
          resourceId="resource-1"
        />
      );

      expect(screen.getByText('Loading annotations...')).toBeInTheDocument();
    });
  });

  // ==========================================================================
  // Annotation List Tests
  // ==========================================================================

  describe('Annotation List', () => {
    it('should render all annotations', () => {
      render(
        <AnnotationPanel
          open={true}
          onOpenChange={vi.fn()}
          resourceId="resource-1"
        />
      );

      expect(screen.getByText('"const x = 1"')).toBeInTheDocument();
      expect(screen.getByText('"function foo"')).toBeInTheDocument();
      expect(screen.getByText('"return value"')).toBeInTheDocument();
    });

    it('should render annotation notes', () => {
      render(
        <AnnotationPanel
          open={true}
          onOpenChange={vi.fn()}
          resourceId="resource-1"
        />
      );

      expect(screen.getByText('This is a variable declaration')).toBeInTheDocument();
      expect(screen.getByText('Main function')).toBeInTheDocument();
    });

    it('should render annotation tags', () => {
      render(
        <AnnotationPanel
          open={true}
          onOpenChange={vi.fn()}
          resourceId="resource-1"
        />
      );

      expect(screen.getByText('variable')).toBeInTheDocument();
      expect(screen.getByText('const')).toBeInTheDocument();
      expect(screen.getByText('function')).toBeInTheDocument();
      expect(screen.getByText('important')).toBeInTheDocument();
    });

    it('should render annotation dates', () => {
      render(
        <AnnotationPanel
          open={true}
          onOpenChange={vi.fn()}
          resourceId="resource-1"
        />
      );

      // Dates are formatted, so we just check they exist
      const dates = screen.getAllByText(/\d{1,2}\/\d{1,2}\/\d{4}/);
      expect(dates.length).toBeGreaterThan(0);
    });

    it('should render color indicators', () => {
      const { container } = render(
        <AnnotationPanel
          open={true}
          onOpenChange={vi.fn()}
          resourceId="resource-1"
        />
      );

      // Check for color indicators with inline styles
      const colorIndicators = container.querySelectorAll('[style*="background-color"]');
      expect(colorIndicators.length).toBeGreaterThan(0);
    });
  });

  // ==========================================================================
  // Interaction Tests
  // ==========================================================================

  describe('Interactions', () => {
    it('should fetch annotations when panel opens', () => {
      const { rerender } = render(
        <AnnotationPanel
          open={false}
          onOpenChange={vi.fn()}
          resourceId="resource-1"
        />
      );

      expect(mockAnnotationStore.fetchAnnotations).not.toHaveBeenCalled();

      rerender(
        <AnnotationPanel
          open={true}
          onOpenChange={vi.fn()}
          resourceId="resource-1"
        />
      );

      expect(mockAnnotationStore.fetchAnnotations).toHaveBeenCalledWith('resource-1');
    });

    it('should select annotation on click', async () => {
      render(
        <AnnotationPanel
          open={true}
          onOpenChange={vi.fn()}
          resourceId="resource-1"
        />
      );

      const annotation = screen.getByText('"const x = 1"');
      fireEvent.click(annotation);

      await waitFor(() => {
        expect(mockAnnotationStore.selectAnnotation).toHaveBeenCalledWith('ann-1');
      });
    });

    it('should update cursor position on annotation click', async () => {
      render(
        <AnnotationPanel
          open={true}
          onOpenChange={vi.fn()}
          resourceId="resource-1"
        />
      );

      const annotation = screen.getByText('"const x = 1"');
      fireEvent.click(annotation);

      await waitFor(() => {
        expect(mockEditorStore.updateCursorPosition).toHaveBeenCalled();
      });
    });

    it('should switch to create mode on create button click', async () => {
      render(
        <AnnotationPanel
          open={true}
          onOpenChange={vi.fn()}
          resourceId="resource-1"
        />
      );

      const createButton = screen.getByRole('button', {
        name: /create new annotation/i,
      });
      fireEvent.click(createButton);

      await waitFor(() => {
        expect(screen.getByText('Create Annotation')).toBeInTheDocument();
      });
    });

    it('should switch to edit mode on edit button click', async () => {
      render(
        <AnnotationPanel
          open={true}
          onOpenChange={vi.fn()}
          resourceId="resource-1"
        />
      );

      // Find and click edit button (first one)
      const editButtons = screen.getAllByRole('button');
      const editButton = editButtons.find((btn) =>
        btn.querySelector('svg')?.classList.contains('lucide-edit')
      );
      
      if (editButton) {
        fireEvent.click(editButton);

        await waitFor(() => {
          expect(screen.getByText('Edit Annotation')).toBeInTheDocument();
        });
      }
    });
  });

  // ==========================================================================
  // Create/Edit Form Tests
  // ==========================================================================

  describe('Create/Edit Form', () => {
    it('should render form fields in create mode', async () => {
      render(
        <AnnotationPanel
          open={true}
          onOpenChange={vi.fn()}
          resourceId="resource-1"
        />
      );

      const createButton = screen.getByRole('button', {
        name: /create new annotation/i,
      });
      fireEvent.click(createButton);

      await waitFor(() => {
        expect(screen.getByLabelText('Note')).toBeInTheDocument();
        expect(screen.getByLabelText(/tags/i)).toBeInTheDocument();
        expect(screen.getByLabelText('Color')).toBeInTheDocument();
      });
    });

    it('should allow entering note text', async () => {
      const user = userEvent.setup();
      
      render(
        <AnnotationPanel
          open={true}
          onOpenChange={vi.fn()}
          resourceId="resource-1"
        />
      );

      const createButton = screen.getByRole('button', {
        name: /create new annotation/i,
      });
      fireEvent.click(createButton);

      await waitFor(() => {
        expect(screen.getByLabelText('Note')).toBeInTheDocument();
      });

      const noteInput = screen.getByLabelText('Note') as HTMLTextAreaElement;
      await user.type(noteInput, 'Test note');

      expect(noteInput.value).toBe('Test note');
    });

    it('should allow entering tags', async () => {
      const user = userEvent.setup();
      
      render(
        <AnnotationPanel
          open={true}
          onOpenChange={vi.fn()}
          resourceId="resource-1"
        />
      );

      const createButton = screen.getByRole('button', {
        name: /create new annotation/i,
      });
      fireEvent.click(createButton);

      await waitFor(() => {
        expect(screen.getByLabelText(/tags/i)).toBeInTheDocument();
      });

      const tagsInput = screen.getByLabelText(/tags/i) as HTMLInputElement;
      await user.type(tagsInput, 'tag1, tag2');

      expect(tagsInput.value).toBe('tag1, tag2');
    });

    it('should allow selecting color', async () => {
      render(
        <AnnotationPanel
          open={true}
          onOpenChange={vi.fn()}
          resourceId="resource-1"
        />
      );

      const createButton = screen.getByRole('button', {
        name: /create new annotation/i,
      });
      fireEvent.click(createButton);

      await waitFor(() => {
        expect(screen.getByLabelText('Color')).toBeInTheDocument();
      });

      // Find color buttons
      const colorButtons = screen.getAllByRole('button', {
        name: /select color/i,
      });
      expect(colorButtons.length).toBeGreaterThan(0);

      // Click second color
      fireEvent.click(colorButtons[1]);

      // Color should be selected (visual feedback tested via className)
      expect(colorButtons[1]).toHaveClass('scale-110');
    });

    it('should create annotation on save', async () => {
      const user = userEvent.setup();
      
      render(
        <AnnotationPanel
          open={true}
          onOpenChange={vi.fn()}
          resourceId="resource-1"
        />
      );

      const createButton = screen.getByRole('button', {
        name: /create new annotation/i,
      });
      fireEvent.click(createButton);

      await waitFor(() => {
        expect(screen.getByLabelText('Note')).toBeInTheDocument();
      });

      // Fill form
      const noteInput = screen.getByLabelText('Note');
      await user.type(noteInput, 'Test note');

      const tagsInput = screen.getByLabelText(/tags/i);
      await user.type(tagsInput, 'tag1, tag2');

      // Save
      const saveButton = screen.getByRole('button', { name: /save/i });
      fireEvent.click(saveButton);

      await waitFor(() => {
        expect(mockAnnotationStore.createAnnotation).toHaveBeenCalledWith(
          'resource-1',
          expect.objectContaining({
            note: 'Test note',
            tags: ['tag1', 'tag2'],
          })
        );
      });
    });

    it('should update annotation on save in edit mode', async () => {
      const user = userEvent.setup();
      
      vi.mocked(useAnnotationStore).mockReturnValue({
        ...mockAnnotationStore,
        selectedAnnotation: mockAnnotations[0],
      });

      render(
        <AnnotationPanel
          open={true}
          onOpenChange={vi.fn()}
          resourceId="resource-1"
        />
      );

      // Click edit button
      const editButtons = screen.getAllByRole('button');
      const editButton = editButtons.find((btn) =>
        btn.querySelector('svg')?.classList.contains('lucide-edit')
      );
      
      if (editButton) {
        fireEvent.click(editButton);

        await waitFor(() => {
          expect(screen.getByText('Edit Annotation')).toBeInTheDocument();
        });

        // Update note
        const noteInput = screen.getByLabelText('Note') as HTMLTextAreaElement;
        await user.clear(noteInput);
        await user.type(noteInput, 'Updated note');

        // Save
        const saveButton = screen.getByRole('button', { name: /save/i });
        fireEvent.click(saveButton);

        await waitFor(() => {
          expect(mockAnnotationStore.updateAnnotation).toHaveBeenCalledWith(
            'ann-1',
            expect.objectContaining({
              note: 'Updated note',
            })
          );
        });
      }
    });

    it('should cancel and return to list view', async () => {
      render(
        <AnnotationPanel
          open={true}
          onOpenChange={vi.fn()}
          resourceId="resource-1"
        />
      );

      const createButton = screen.getByRole('button', {
        name: /create new annotation/i,
      });
      fireEvent.click(createButton);

      await waitFor(() => {
        expect(screen.getByText('Create Annotation')).toBeInTheDocument();
      });

      const cancelButton = screen.getByRole('button', { name: /cancel/i });
      fireEvent.click(cancelButton);

      await waitFor(() => {
        expect(screen.getByText('Annotations')).toBeInTheDocument();
        expect(screen.queryByText('Create Annotation')).not.toBeInTheDocument();
      });
    });
  });

  // ==========================================================================
  // Delete Tests
  // ==========================================================================

  describe('Delete', () => {
    it('should show delete button for each annotation', () => {
      render(
        <AnnotationPanel
          open={true}
          onOpenChange={vi.fn()}
          resourceId="resource-1"
        />
      );

      const deleteButtons = screen.getAllByRole('button').filter((btn) =>
        btn.querySelector('svg')?.classList.contains('lucide-trash')
      );

      expect(deleteButtons.length).toBe(mockAnnotations.length);
    });

    it('should show confirmation dialog on delete', async () => {
      const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(false);

      render(
        <AnnotationPanel
          open={true}
          onOpenChange={vi.fn()}
          resourceId="resource-1"
        />
      );

      const deleteButtons = screen.getAllByRole('button').filter((btn) =>
        btn.querySelector('svg')?.classList.contains('lucide-trash')
      );

      fireEvent.click(deleteButtons[0]);

      expect(confirmSpy).toHaveBeenCalledWith(
        'Are you sure you want to delete this annotation?'
      );

      confirmSpy.mockRestore();
    });

    it('should delete annotation on confirmation', async () => {
      const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true);

      render(
        <AnnotationPanel
          open={true}
          onOpenChange={vi.fn()}
          resourceId="resource-1"
        />
      );

      const deleteButtons = screen.getAllByRole('button').filter((btn) =>
        btn.querySelector('svg')?.classList.contains('lucide-trash')
      );

      fireEvent.click(deleteButtons[0]);

      await waitFor(() => {
        expect(mockAnnotationStore.deleteAnnotation).toHaveBeenCalledWith('ann-1');
      });

      confirmSpy.mockRestore();
    });

    it('should not delete annotation on cancel', async () => {
      const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(false);

      render(
        <AnnotationPanel
          open={true}
          onOpenChange={vi.fn()}
          resourceId="resource-1"
        />
      );

      const deleteButtons = screen.getAllByRole('button').filter((btn) =>
        btn.querySelector('svg')?.classList.contains('lucide-trash')
      );

      fireEvent.click(deleteButtons[0]);

      await waitFor(() => {
        expect(mockAnnotationStore.deleteAnnotation).not.toHaveBeenCalled();
      });

      confirmSpy.mockRestore();
    });
  });

  // ==========================================================================
  // Search Tests
  // ==========================================================================

  describe('Search', () => {
    it('should show search input when annotations exist', () => {
      render(
        <AnnotationPanel
          open={true}
          onOpenChange={vi.fn()}
          resourceId="resource-1"
        />
      );

      expect(
        screen.getByPlaceholderText('Search annotations...')
      ).toBeInTheDocument();
    });

    it('should not show search input when no annotations', () => {
      vi.mocked(useAnnotationStore).mockReturnValue({
        ...mockAnnotationStore,
        annotations: [],
      });

      render(
        <AnnotationPanel
          open={true}
          onOpenChange={vi.fn()}
          resourceId="resource-1"
        />
      );

      expect(
        screen.queryByPlaceholderText('Search annotations...')
      ).not.toBeInTheDocument();
    });

    it('should filter annotations by highlighted text', async () => {
      const user = userEvent.setup();
      
      render(
        <AnnotationPanel
          open={true}
          onOpenChange={vi.fn()}
          resourceId="resource-1"
        />
      );

      const searchInput = screen.getByPlaceholderText('Search annotations...');
      await user.type(searchInput, 'const');

      // Should show only matching annotation
      expect(screen.getByText('"const x = 1"')).toBeInTheDocument();
      expect(screen.queryByText('"function foo"')).not.toBeInTheDocument();
      expect(screen.queryByText('"return value"')).not.toBeInTheDocument();
    });

    it('should filter annotations by note', async () => {
      const user = userEvent.setup();
      
      render(
        <AnnotationPanel
          open={true}
          onOpenChange={vi.fn()}
          resourceId="resource-1"
        />
      );

      const searchInput = screen.getByPlaceholderText('Search annotations...');
      await user.type(searchInput, 'variable');

      // Should show only matching annotation
      expect(screen.getByText('"const x = 1"')).toBeInTheDocument();
      expect(screen.queryByText('"function foo"')).not.toBeInTheDocument();
    });

    it('should filter annotations by tags', async () => {
      const user = userEvent.setup();
      
      render(
        <AnnotationPanel
          open={true}
          onOpenChange={vi.fn()}
          resourceId="resource-1"
        />
      );

      const searchInput = screen.getByPlaceholderText('Search annotations...');
      await user.type(searchInput, 'important');

      // Should show only matching annotation
      expect(screen.getByText('"function foo"')).toBeInTheDocument();
      expect(screen.queryByText('"const x = 1"')).not.toBeInTheDocument();
    });

    it('should show empty state when no matches', async () => {
      const user = userEvent.setup();
      
      render(
        <AnnotationPanel
          open={true}
          onOpenChange={vi.fn()}
          resourceId="resource-1"
        />
      );

      const searchInput = screen.getByPlaceholderText('Search annotations...');
      await user.type(searchInput, 'nonexistent');

      expect(screen.getByText('No matching annotations')).toBeInTheDocument();
      expect(screen.getByText('Try a different search term')).toBeInTheDocument();
    });

    it('should be case-insensitive', async () => {
      const user = userEvent.setup();
      
      render(
        <AnnotationPanel
          open={true}
          onOpenChange={vi.fn()}
          resourceId="resource-1"
        />
      );

      const searchInput = screen.getByPlaceholderText('Search annotations...');
      await user.type(searchInput, 'CONST');

      // Should still match lowercase "const"
      expect(screen.getByText('"const x = 1"')).toBeInTheDocument();
    });

    it('should clear filter when search is cleared', async () => {
      const user = userEvent.setup();
      
      render(
        <AnnotationPanel
          open={true}
          onOpenChange={vi.fn()}
          resourceId="resource-1"
        />
      );

      const searchInput = screen.getByPlaceholderText(
        'Search annotations...'
      ) as HTMLInputElement;
      
      await user.type(searchInput, 'const');
      expect(screen.queryByText('"function foo"')).not.toBeInTheDocument();

      await user.clear(searchInput);
      
      // All annotations should be visible again
      expect(screen.getByText('"const x = 1"')).toBeInTheDocument();
      expect(screen.getByText('"function foo"')).toBeInTheDocument();
      expect(screen.getByText('"return value"')).toBeInTheDocument();
    });
  });
});
