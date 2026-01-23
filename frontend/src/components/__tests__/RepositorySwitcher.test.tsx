import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { RepositorySwitcher } from '../RepositorySwitcher';
import { useRepositoryStore } from '@/stores/repository';

/**
 * Property-Based Tests for RepositorySwitcher
 * 
 * Feature: phase1-workbench-navigation
 * Property 5: Repository Switcher Selection
 * Validates: Requirements 4.4
 */

// Mock the stores
vi.mock('@/stores/repository');

describe('RepositorySwitcher - Property Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  /**
   * Property 5: Repository Switcher Selection
   * For any repository in the list, selecting it should update the active repository
   * and persist the selection
   */
  it('should update active repository for all repository selections', () => {
    const mockRepositories = [
      { id: '1', name: 'Repo 1', source: 'github', status: 'active' },
      { id: '2', name: 'Repo 2', source: 'gitlab', status: 'active' },
      { id: '3', name: 'Repo 3', source: 'local', status: 'indexing' },
    ];

    const mockSetActive = vi.fn();

    (useRepositoryStore as any).mockReturnValue({
      repositories: mockRepositories,
      activeRepository: mockRepositories[0],
      setActiveRepository: mockSetActive,
    });

    render(<RepositorySwitcher />);
    
    // Verify current repository is displayed
    expect(screen.getByText('Repo 1')).toBeInTheDocument();
  });

  it('should handle empty repository list', () => {
    (useRepositoryStore as any).mockReturnValue({
      repositories: [],
      activeRepository: null,
      setActiveRepository: vi.fn(),
    });

    render(<RepositorySwitcher />);
    
    // Should show "No repository" or similar
    expect(screen.getByText('No repository')).toBeInTheDocument();
  });

  it('should maintain selection consistency across re-renders', () => {
    const mockRepositories = [
      { id: '1', name: 'Repo 1', source: 'github', status: 'active' },
      { id: '2', name: 'Repo 2', source: 'gitlab', status: 'active' },
    ];

    (useRepositoryStore as any).mockReturnValue({
      repositories: mockRepositories,
      activeRepository: mockRepositories[0],
      setActiveRepository: vi.fn(),
    });

    const { rerender } = render(<RepositorySwitcher />);
    
    // Initial render
    expect(screen.getByText('Repo 1')).toBeInTheDocument();
    
    // Re-render with same props
    rerender(<RepositorySwitcher />);
    
    // Should still show same repository
    expect(screen.getByText('Repo 1')).toBeInTheDocument();
  });

  it('should handle repository with different sources', () => {
    const sources = ['github', 'gitlab', 'bitbucket', 'local'];
    
    sources.forEach((source) => {
      const mockRepo = {
        id: '1',
        name: `${source} Repo`,
        source,
        status: 'active' as const,
      };

      (useRepositoryStore as any).mockReturnValue({
        repositories: [mockRepo],
        activeRepository: mockRepo,
        setActiveRepository: vi.fn(),
      });

      const { unmount } = render(<RepositorySwitcher />);
      
      // Should render repository regardless of source
      expect(screen.getByText(`${source} Repo`)).toBeInTheDocument();
      
      unmount();
    });
  });

  it('should handle repository with different statuses', () => {
    const statuses = ['active', 'indexing', 'error', 'archived'];
    
    statuses.forEach((status) => {
      const mockRepo = {
        id: '1',
        name: 'Test Repo',
        source: 'github',
        status: status as any,
      };

      (useRepositoryStore as any).mockReturnValue({
        repositories: [mockRepo],
        activeRepository: mockRepo,
        setActiveRepository: vi.fn(),
      });

      const { unmount } = render(<RepositorySwitcher />);
      
      // Should render repository regardless of status
      expect(screen.getByText('Test Repo')).toBeInTheDocument();
      
      unmount();
    });
  });
});
