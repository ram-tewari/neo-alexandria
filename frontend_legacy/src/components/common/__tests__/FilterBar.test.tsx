/**
 * FilterBar Tests
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { FilterBar } from '../FilterBar';

describe('FilterBar', () => {
  it('should render search input', () => {
    render(<FilterBar />);
    expect(screen.getByPlaceholderText('Search resources...')).toBeInTheDocument();
  });

  it('should call onSearchChange when typing', async () => {
    const onSearchChange = vi.fn();
    render(<FilterBar onSearchChange={onSearchChange} />);
    
    const input = screen.getByPlaceholderText('Search resources...');
    fireEvent.change(input, { target: { value: 'test' } });
    
    // Wait for debounce
    await new Promise(resolve => setTimeout(resolve, 350));
    expect(onSearchChange).toHaveBeenCalledWith('test');
  });

  it('should show filter panel when clicking Filters button', () => {
    render(<FilterBar />);
    
    const filterButton = screen.getByText('Filters');
    fireEvent.click(filterButton);
    
    expect(screen.getByText('Status')).toBeInTheDocument();
  });

  it('should display active filter count', () => {
    render(<FilterBar filters={{ read_status: 'unread' }} />);
    expect(screen.getByText('1')).toBeInTheDocument();
  });
});
