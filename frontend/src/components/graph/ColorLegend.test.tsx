import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ColorLegend } from './ColorLegend';
import { ThemeProvider } from '../theme/ThemeProvider';

const mockVisibleCategories = new Set(['technology', 'science', 'arts']);
const mockOnToggleCategory = vi.fn();
const mockOnHoverCategory = vi.fn();

const renderWithTheme = (ui: React.ReactElement) => {
  return render(<ThemeProvider>{ui}</ThemeProvider>);
};

describe('ColorLegend', () => {
  it('should render legend title', () => {
    renderWithTheme(
      <ColorLegend
        visibleCategories={mockVisibleCategories}
        onToggleCategory={mockOnToggleCategory}
      />
    );
    
    expect(screen.getByText('Topic Categories')).toBeInTheDocument();
  });

  it('should render all topic categories except uncategorized', () => {
    renderWithTheme(
      <ColorLegend
        visibleCategories={mockVisibleCategories}
        onToggleCategory={mockOnToggleCategory}
      />
    );
    
    expect(screen.getByText('Technology')).toBeInTheDocument();
    expect(screen.getByText('Science')).toBeInTheDocument();
    expect(screen.getByText('Arts & Culture')).toBeInTheDocument();
    expect(screen.queryByText('Uncategorized')).not.toBeInTheDocument();
  });

  it('should call onToggleCategory when category is clicked', async () => {
    const user = userEvent.setup();
    
    renderWithTheme(
      <ColorLegend
        visibleCategories={mockVisibleCategories}
        onToggleCategory={mockOnToggleCategory}
      />
    );
    
    const technologyButton = screen.getByText('Technology').closest('button');
    await user.click(technologyButton!);
    
    expect(mockOnToggleCategory).toHaveBeenCalledWith('technology');
  });

  it('should call onHoverCategory when category is hovered', async () => {
    const user = userEvent.setup();
    
    renderWithTheme(
      <ColorLegend
        visibleCategories={mockVisibleCategories}
        onToggleCategory={mockOnToggleCategory}
        onHoverCategory={mockOnHoverCategory}
      />
    );
    
    const technologyButton = screen.getByText('Technology').closest('button');
    await user.hover(technologyButton!);
    
    expect(mockOnHoverCategory).toHaveBeenCalledWith('technology');
  });

  it('should show active state for visible categories', () => {
    renderWithTheme(
      <ColorLegend
        visibleCategories={mockVisibleCategories}
        onToggleCategory={mockOnToggleCategory}
      />
    );
    
    const technologyButton = screen.getByText('Technology').closest('button');
    expect(technologyButton).toHaveClass('active');
  });

  it('should show inactive state for hidden categories', () => {
    renderWithTheme(
      <ColorLegend
        visibleCategories={new Set(['technology'])}
        onToggleCategory={mockOnToggleCategory}
      />
    );
    
    const scienceButton = screen.getByText('Science').closest('button');
    expect(scienceButton).toHaveClass('inactive');
  });

  it('should render collapse toggle when collapsible is true', () => {
    renderWithTheme(
      <ColorLegend
        visibleCategories={mockVisibleCategories}
        onToggleCategory={mockOnToggleCategory}
        collapsible={true}
      />
    );
    
    const toggleButton = screen.getByLabelText(/collapse legend/i);
    expect(toggleButton).toBeInTheDocument();
  });

  it('should not render collapse toggle when collapsible is false', () => {
    renderWithTheme(
      <ColorLegend
        visibleCategories={mockVisibleCategories}
        onToggleCategory={mockOnToggleCategory}
        collapsible={false}
      />
    );
    
    const toggleButton = screen.queryByLabelText(/collapse legend/i);
    expect(toggleButton).not.toBeInTheDocument();
  });

  it('should toggle collapsed state when toggle button is clicked', async () => {
    const user = userEvent.setup();
    
    renderWithTheme(
      <ColorLegend
        visibleCategories={mockVisibleCategories}
        onToggleCategory={mockOnToggleCategory}
        collapsible={true}
      />
    );
    
    const toggleButton = screen.getByLabelText(/collapse legend/i);
    await user.click(toggleButton);
    
    // Content should be hidden
    expect(screen.queryByText('Technology')).not.toBeVisible();
  });

  it('should apply correct position class', () => {
    const { container } = renderWithTheme(
      <ColorLegend
        visibleCategories={mockVisibleCategories}
        onToggleCategory={mockOnToggleCategory}
        position="top-right"
      />
    );
    
    const legend = container.querySelector('.color-legend');
    expect(legend).toHaveClass('color-legend-top-right');
  });

  it('should have Show All button when not all categories are visible', () => {
    renderWithTheme(
      <ColorLegend
        visibleCategories={new Set(['technology'])}
        onToggleCategory={mockOnToggleCategory}
      />
    );
    
    expect(screen.getByText('Show All')).toBeInTheDocument();
  });
});
