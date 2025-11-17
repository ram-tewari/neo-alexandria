/**
 * ViewModeSelector Tests
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ViewModeSelector } from '../ViewModeSelector';

describe('ViewModeSelector', () => {
  it('should render all view mode buttons', () => {
    const onChange = vi.fn();
    render(<ViewModeSelector currentMode="grid" onChange={onChange} />);
    
    expect(screen.getByText('Grid')).toBeInTheDocument();
    expect(screen.getByText('List')).toBeInTheDocument();
    expect(screen.getByText('Headlines')).toBeInTheDocument();
    expect(screen.getByText('Masonry')).toBeInTheDocument();
  });

  it('should highlight active mode', () => {
    const onChange = vi.fn();
    const { container } = render(<ViewModeSelector currentMode="list" onChange={onChange} />);
    
    const listButton = screen.getByText('List').closest('button');
    expect(listButton).toHaveClass('active');
  });

  it('should call onChange when clicking a mode', () => {
    const onChange = vi.fn();
    render(<ViewModeSelector currentMode="grid" onChange={onChange} />);
    
    fireEvent.click(screen.getByText('List'));
    expect(onChange).toHaveBeenCalledWith('list');
  });
});
