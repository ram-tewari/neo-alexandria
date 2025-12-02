/**
 * Tests for DensityToggle component
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { DensityToggle } from './DensityToggle';

describe('DensityToggle', () => {
  it('renders all density options', () => {
    const onChange = vi.fn();
    render(<DensityToggle value="comfortable" onChange={onChange} />);
    
    expect(screen.getByText('Compact')).toBeInTheDocument();
    expect(screen.getByText('Comfortable')).toBeInTheDocument();
    expect(screen.getByText('Spacious')).toBeInTheDocument();
  });

  it('highlights the active density', () => {
    const onChange = vi.fn();
    render(<DensityToggle value="compact" onChange={onChange} />);
    
    const compactButton = screen.getByText('Compact');
    expect(compactButton).toHaveAttribute('aria-pressed', 'true');
  });

  it('calls onChange when a density is clicked', () => {
    const onChange = vi.fn();
    render(<DensityToggle value="comfortable" onChange={onChange} />);
    
    const spaciousButton = screen.getByText('Spacious');
    fireEvent.click(spaciousButton);
    
    expect(onChange).toHaveBeenCalledWith('spacious');
  });

  it('applies custom className', () => {
    const onChange = vi.fn();
    const { container } = render(
      <DensityToggle value="comfortable" onChange={onChange} className="custom-class" />
    );
    
    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper).toHaveClass('custom-class');
  });
});
