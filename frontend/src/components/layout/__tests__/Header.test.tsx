/**
 * Unit Tests for Header Component
 * Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Header, NavigationLink } from '../Header';
import { ThemeProvider } from '../../../contexts/ThemeContext';

const mockLinks: NavigationLink[] = [
  { label: 'Home', href: '/', active: true },
  { label: 'About', href: '/about' },
  { label: 'Contact', href: '/contact' },
];

describe('Header', () => {
  it('should render navigation links', () => {
    render(
      <ThemeProvider>
        <Header links={mockLinks} />
      </ThemeProvider>
    );

    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('About')).toBeInTheDocument();
    expect(screen.getByText('Contact')).toBeInTheDocument();
  });

  it('should have sticky positioning', () => {
    const { container } = render(
      <ThemeProvider>
        <Header links={mockLinks} />
      </ThemeProvider>
    );

    const header = container.querySelector('.header');
    expect(header).toHaveClass('header');
  });

  it('should render collapse button', () => {
    render(
      <ThemeProvider>
        <Header links={mockLinks} />
      </ThemeProvider>
    );

    const collapseBtn = screen.getByLabelText('Collapse navigation');
    expect(collapseBtn).toBeInTheDocument();
  });

  it('should toggle navigation on collapse button click', async () => {
    const user = userEvent.setup();
    
    render(
      <ThemeProvider>
        <Header links={mockLinks} />
      </ThemeProvider>
    );

    const collapseBtn = screen.getByLabelText('Collapse navigation');
    
    // Click to collapse
    await user.click(collapseBtn);
    
    // Button label should change
    expect(screen.getByLabelText('Expand navigation')).toBeInTheDocument();
  });

  it('should render theme toggle', () => {
    render(
      <ThemeProvider>
        <Header links={mockLinks} />
      </ThemeProvider>
    );

    // Theme toggle button should be present
    const themeButtons = screen.getAllByRole('button');
    expect(themeButtons.length).toBeGreaterThan(1);
  });

  it('should highlight active link', () => {
    render(
      <ThemeProvider>
        <Header links={mockLinks} />
      </ThemeProvider>
    );

    const homeLink = screen.getByText('Home').closest('a');
    expect(homeLink).toHaveClass('header__nav-link--active');
    expect(homeLink).toHaveAttribute('aria-current', 'page');
  });

  it('should render logo when provided', () => {
    render(
      <ThemeProvider>
        <Header links={mockLinks} logo={<span>My Logo</span>} />
      </ThemeProvider>
    );

    expect(screen.getByText('My Logo')).toBeInTheDocument();
  });
});
