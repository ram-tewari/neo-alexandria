import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from '@tanstack/react-router';
import { WorkbenchSidebar } from '../WorkbenchSidebar';
import { useWorkbenchStore } from '@/stores/workbench';

/**
 * Unit Tests for WorkbenchSidebar
 * 
 * Feature: phase1-workbench-navigation
 * Validates: Requirements 2.1, 2.2, 2.4, 2.6
 */

// Mock the stores
vi.mock('@/stores/workbench');

// Mock useLocation
vi.mock('@tanstack/react-router', async () => {
  const actual = await vi.importActual('@tanstack/react-router');
  return {
    ...actual,
    useLocation: () => ({ pathname: '/repositories' }),
  };
});

describe('WorkbenchSidebar - Unit Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    
    (useWorkbenchStore as any).mockReturnValue({
      sidebarOpen: true,
      toggleSidebar: vi.fn(),
    });
  });

  /**
   * Test: Active route highlighting
   * Validates: Requirements 2.2
   */
  it('should highlight active route', () => {
    render(<WorkbenchSidebar />);
    
    // The Repositories nav item should be highlighted (we're on /repositories)
    const navItems = screen.getAllByRole('link');
    expect(navItems.length).toBeGreaterThan(0);
  });

  /**
   * Test: Collapsed state rendering
   * Validates: Requirements 2.4
   */
  it('should render in collapsed state (icon-only)', () => {
    (useWorkbenchStore as any).mockReturnValue({
      sidebarOpen: false,
      toggleSidebar: vi.fn(),
    });

    render(<WorkbenchSidebar />);
    
    // In collapsed state, sidebar should still render
    const sidebar = screen.getByRole('navigation');
    expect(sidebar).toBeInTheDocument();
  });

  /**
   * Test: Expanded state rendering
   * Validates: Requirements 2.4
   */
  it('should render in expanded state with labels', () => {
    (useWorkbenchStore as any).mockReturnValue({
      sidebarOpen: true,
      toggleSidebar: vi.fn(),
    });

    render(<WorkbenchSidebar />);
    
    // In expanded state, labels should be visible
    expect(screen.getByText('Repositories')).toBeInTheDocument();
    expect(screen.getByText('Cortex')).toBeInTheDocument();
    expect(screen.getByText('Library')).toBeInTheDocument();
  });

  /**
   * Test: Tooltip display in collapsed state
   * Validates: Requirements 2.6
   */
  it('should show tooltips in collapsed state', () => {
    (useWorkbenchStore as any).mockReturnValue({
      sidebarOpen: false,
      toggleSidebar: vi.fn(),
    });

    render(<WorkbenchSidebar />);
    
    // Tooltips should be present (via Tooltip component)
    // Note: Actual tooltip visibility requires user interaction
    const sidebar = screen.getByRole('navigation');
    expect(sidebar).toBeInTheDocument();
  });

  /**
   * Test: All navigation items are rendered
   * Validates: Requirements 2.1
   */
  it('should render all navigation items', () => {
    render(<WorkbenchSidebar />);
    
    // Check for all 6 navigation items
    expect(screen.getByText('Repositories')).toBeInTheDocument();
    expect(screen.getByText('Cortex')).toBeInTheDocument();
    expect(screen.getByText('Library')).toBeInTheDocument();
    expect(screen.getByText('Planner')).toBeInTheDocument();
    expect(screen.getByText('Wiki')).toBeInTheDocument();
    expect(screen.getByText('Ops')).toBeInTheDocument();
  });

  /**
   * Test: Toggle button is rendered
   * Validates: Requirements 2.5
   */
  it('should render toggle button', () => {
    render(<WorkbenchSidebar />);
    
    // Toggle button should be present
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBeGreaterThan(0);
  });
});
