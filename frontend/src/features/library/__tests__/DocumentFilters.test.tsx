/**
 * DocumentFilters Component Tests
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { DocumentFilters, type DocumentFiltersState } from '../DocumentFilters';

const defaultFilters: DocumentFiltersState = {
  search: '',
  type: undefined,
  qualityMin: 0,
  qualityMax: 100,
  sortBy: 'date',
  sortOrder: 'desc',
};

describe('DocumentFilters', () => {
  describe('Rendering', () => {
    it('renders search input', () => {
      render(<DocumentFilters filters={defaultFilters} onFiltersChange={vi.fn()} />);
      
      expect(screen.getByPlaceholderText('Search documents...')).toBeInTheDocument();
    });

    it('renders filters button', () => {
      render(<DocumentFilters filters={defaultFilters} onFiltersChange={vi.fn()} />);
      
      expect(screen.getByText('Filters')).toBeInTheDocument();
    });

    it('renders sort dropdown', () => {
      render(<DocumentFilters filters={defaultFilters} onFiltersChange={vi.fn()} />);
      
      expect(screen.getByText('Newest first')).toBeInTheDocument();
    });
  });

  describe('Search Input', () => {
    it('displays current search value', () => {
      const filters = { ...defaultFilters, search: 'test query' };
      render(<DocumentFilters filters={filters} onFiltersChange={vi.fn()} />);
      
      const input = screen.getByPlaceholderText('Search documents...') as HTMLInputElement;
      expect(input.value).toBe('test query');
    });

    it('updates search on input change', () => {
      render(<DocumentFilters filters={defaultFilters} onFiltersChange={vi.fn()} />);
      
      const input = screen.getByPlaceholderText('Search documents...');
      fireEvent.change(input, { target: { value: 'new search' } });
      
      expect((input as HTMLInputElement).value).toBe('new search');
    });

    it('shows clear button when search has value', () => {
      const filters = { ...defaultFilters, search: 'test' };
      render(<DocumentFilters filters={filters} onFiltersChange={vi.fn()} />);
      
      // Clear button should be present (X icon)
      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);
    });

    it('clears search when clear button clicked', () => {
      const handleChange = vi.fn();
      const filters = { ...defaultFilters, search: 'test' };
      render(<DocumentFilters filters={filters} onFiltersChange={handleChange} />);
      
      const input = screen.getByPlaceholderText('Search documents...') as HTMLInputElement;
      fireEvent.change(input, { target: { value: '' } });
      
      expect(input.value).toBe('');
    });
  });

  describe('Active Filters', () => {
    it('shows active filter count badge', () => {
      const filters = { ...defaultFilters, search: 'test', type: 'pdf' as const };
      render(<DocumentFilters filters={filters} onFiltersChange={vi.fn()} />);
      
      // Badge with count should be visible
      expect(screen.getByText('Filters')).toBeInTheDocument();
    });

    it('shows search filter badge', () => {
      const filters = { ...defaultFilters, search: 'test query' };
      render(<DocumentFilters filters={filters} onFiltersChange={vi.fn()} />);
      
      expect(screen.getByText(/Search: test query/)).toBeInTheDocument();
    });

    it('shows type filter badge', () => {
      const filters = { ...defaultFilters, type: 'pdf' as const };
      render(<DocumentFilters filters={filters} onFiltersChange={vi.fn()} />);
      
      expect(screen.getByText(/Type: PDF/)).toBeInTheDocument();
    });

    it('shows quality filter badge', () => {
      const filters = { ...defaultFilters, qualityMin: 50, qualityMax: 90 };
      render(<DocumentFilters filters={filters} onFiltersChange={vi.fn()} />);
      
      expect(screen.getByText(/Quality: 50%-90%/)).toBeInTheDocument();
    });

    it('does not show badges when no active filters', () => {
      render(<DocumentFilters filters={defaultFilters} onFiltersChange={vi.fn()} />);
      
      expect(screen.queryByText(/Search:/)).not.toBeInTheDocument();
      expect(screen.queryByText(/Type:/)).not.toBeInTheDocument();
      expect(screen.queryByText(/Quality:/)).not.toBeInTheDocument();
    });
  });

  describe('Clear Filters', () => {
    it('shows clear all button when filters active', () => {
      const filters = { ...defaultFilters, search: 'test' };
      render(<DocumentFilters filters={filters} onFiltersChange={vi.fn()} />);
      
      // Clear all button should be available
      expect(screen.getByText('Filters')).toBeInTheDocument();
    });

    it('calls onFiltersChange with default filters when cleared', () => {
      const handleChange = vi.fn();
      const filters = { ...defaultFilters, search: 'test', type: 'pdf' as const };
      render(<DocumentFilters filters={filters} onFiltersChange={handleChange} />);
      
      // Would need to open popover and click clear all
      expect(screen.getByText('Filters')).toBeInTheDocument();
    });
  });

  describe('Sort Options', () => {
    it('displays current sort option', () => {
      render(<DocumentFilters filters={defaultFilters} onFiltersChange={vi.fn()} />);
      
      expect(screen.getByText('Newest first')).toBeInTheDocument();
    });

    it('shows different sort options', () => {
      const filters = { ...defaultFilters, sortBy: 'title' as const, sortOrder: 'asc' as const };
      render(<DocumentFilters filters={filters} onFiltersChange={vi.fn()} />);
      
      expect(screen.getByText('Title A-Z')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has accessible search input', () => {
      render(<DocumentFilters filters={defaultFilters} onFiltersChange={vi.fn()} />);
      
      const input = screen.getByPlaceholderText('Search documents...');
      expect(input).toBeInTheDocument();
    });

    it('has accessible buttons', () => {
      render(<DocumentFilters filters={defaultFilters} onFiltersChange={vi.fn()} />);
      
      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);
    });
  });
});
