/**
 * SearchInput Component Tests
 */

import { render, screen, fireEvent } from '@testing-library/react';
import { SearchInput } from '../SearchInput';
import { describe, it, expect, vi } from 'vitest';

describe('SearchInput', () => {
  const defaultProps = {
    value: '',
    onChange: vi.fn(),
    onClear: vi.fn(),
    isLoading: false,
  };

  it('should render with placeholder', () => {
    render(<SearchInput {...defaultProps} />);
    expect(screen.getByPlaceholderText('Search knowledge base...')).toBeInTheDocument();
  });

  it('should render with custom placeholder', () => {
    render(<SearchInput {...defaultProps} placeholder="Custom placeholder" />);
    expect(screen.getByPlaceholderText('Custom placeholder')).toBeInTheDocument();
  });

  it('should display current value', () => {
    render(<SearchInput {...defaultProps} value="test query" />);
    expect(screen.getByDisplayValue('test query')).toBeInTheDocument();
  });

  it('should call onChange when typing', () => {
    const onChange = vi.fn();
    render(<SearchInput {...defaultProps} onChange={onChange} />);
    
    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'new query' } });
    
    expect(onChange).toHaveBeenCalledWith('new query');
  });

  it('should show clear button when value exists', () => {
    render(<SearchInput {...defaultProps} value="test" />);
    expect(screen.getByLabelText('Clear search')).toBeInTheDocument();
  });

  it('should not show clear button when value is empty', () => {
    render(<SearchInput {...defaultProps} value="" />);
    expect(screen.queryByLabelText('Clear search')).not.toBeInTheDocument();
  });

  it('should call onClear when clear button clicked', () => {
    const onClear = vi.fn();
    render(<SearchInput {...defaultProps} value="test" onClear={onClear} />);
    
    const clearButton = screen.getByLabelText('Clear search');
    fireEvent.click(clearButton);
    
    expect(onClear).toHaveBeenCalled();
  });

  it('should show loading spinner when isLoading is true', () => {
    render(<SearchInput {...defaultProps} isLoading={true} />);
    expect(document.querySelector('.animate-spin')).toBeInTheDocument();
  });

  it('should not show loading spinner when isLoading is false', () => {
    render(<SearchInput {...defaultProps} isLoading={false} />);
    expect(document.querySelector('.animate-spin')).not.toBeInTheDocument();
  });

  it('should have search icon', () => {
    render(<SearchInput {...defaultProps} />);
    // Search icon should be present
    const input = screen.getByRole('textbox');
    expect(input.parentElement?.querySelector('svg')).toBeInTheDocument();
  });

  it('should have proper ARIA label', () => {
    render(<SearchInput {...defaultProps} />);
    expect(screen.getByLabelText('Search knowledge base')).toBeInTheDocument();
  });

  it('should auto-focus on mount', () => {
    render(<SearchInput {...defaultProps} />);
    const input = screen.getByRole('textbox');
    expect(document.activeElement).toBe(input);
  });
});
