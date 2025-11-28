/**
 * Unit Tests for ThemeToggle Component
 * Requirements: 5.3, 12.1, 13.1, 13.4
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ThemeToggle } from '../ThemeToggle';
import { ThemeProvider } from '../../../contexts/ThemeContext';

describe('ThemeToggle', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('should render with default props', () => {
    render(
      <ThemeProvider>
        <ThemeToggle />
      </ThemeProvider>
    );

    const button = screen.getByRole('button');
    expect(button).toBeInTheDocument();
  });

  it('should have proper ARIA labels', () => {
    render(
      <ThemeProvider defaultTheme="light">
        <ThemeToggle />
      </ThemeProvider>
    );

    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('aria-label', 'Switch to dark mode');
  });

  it('should toggle theme when clicked', async () => {
    const user = userEvent.setup();
    
    render(
      <ThemeProvider defaultTheme="light">
        <ThemeToggle />
      </ThemeProvider>
    );

    const button = screen.getByRole('button');
    
    // Initial state
    expect(button).toHaveAttribute('aria-label', 'Switch to dark mode');
    
    // Click to toggle
    await user.click(button);
    
    // Should switch to dark mode
    expect(button).toHaveAttribute('aria-label', 'Switch to light mode');
  });

  it('should show label when showLabel is true', () => {
    render(
      <ThemeProvider defaultTheme="light">
        <ThemeToggle showLabel />
      </ThemeProvider>
    );

    expect(screen.getByText('Light')).toBeInTheDocument();
  });

  it('should apply custom className', () => {
    render(
      <ThemeProvider>
        <ThemeToggle className="custom-class" />
      </ThemeProvider>
    );

    const button = screen.getByRole('button');
    expect(button).toHaveClass('custom-class');
  });

  it('should apply size variants', () => {
    const { rerender } = render(
      <ThemeProvider>
        <ThemeToggle size="sm" />
      </ThemeProvider>
    );

    let button = screen.getByRole('button');
    expect(button).toHaveClass('theme-toggle--sm');

    rerender(
      <ThemeProvider>
        <ThemeToggle size="lg" />
      </ThemeProvider>
    );

    button = screen.getByRole('button');
    expect(button).toHaveClass('theme-toggle--lg');
  });

  it('should have proper button type', () => {
    render(
      <ThemeProvider>
        <ThemeToggle />
      </ThemeProvider>
    );

    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('type', 'button');
  });
});
