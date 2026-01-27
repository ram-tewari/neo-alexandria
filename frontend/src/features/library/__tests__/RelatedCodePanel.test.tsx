import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { RelatedCodePanel } from '../RelatedCodePanel';
import { useAutoLinking } from '@/lib/hooks/useAutoLinking';

// Mock the auto-linking hook
vi.mock('@/lib/hooks/useAutoLinking', () => ({
  useAutoLinking: vi.fn(),
}));

describe('RelatedCodePanel', () => {
  const mockRelatedCode = [
    {
      resource: {
        id: 'code-1',
        title: 'utils.py',
        description: 'Utility functions for data processing',
        type: 'code',
      },
      similarity: 0.85,
      relationship_type: 'semantic' as const,
    },
    {
      resource: {
        id: 'code-2',
        title: 'parser.ts',
        description: 'AST parser implementation',
        type: 'code',
      },
      similarity: 0.72,
      relationship_type: 'code_reference' as const,
    },
    {
      resource: {
        id: 'code-3',
        title: 'main.cpp',
        description: 'Main entry point',
        type: 'code',
      },
      similarity: 0.45,
      relationship_type: 'citation' as const,
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders loading state', () => {
    (useAutoLinking as any).mockReturnValue({
      relatedCode: [],
      isLoadingCode: true,
      codeError: null,
      hasRelatedCode: false,
      refreshSuggestions: vi.fn(),
    });

    render(<RelatedCodePanel resourceId="test-resource" />);

    expect(screen.getByText('Related Code')).toBeInTheDocument();
    // Should show skeleton loaders
    const skeletons = document.querySelectorAll('.animate-pulse');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it('renders error state', () => {
    (useAutoLinking as any).mockReturnValue({
      relatedCode: [],
      isLoadingCode: false,
      codeError: new Error('Failed to load'),
      hasRelatedCode: false,
      refreshSuggestions: vi.fn(),
    });

    render(<RelatedCodePanel resourceId="test-resource" />);

    expect(screen.getByText('Related Code')).toBeInTheDocument();
    expect(screen.getByText(/Failed to load related code files/i)).toBeInTheDocument();
  });

  it('renders empty state when no related code', () => {
    (useAutoLinking as any).mockReturnValue({
      relatedCode: [],
      isLoadingCode: false,
      codeError: null,
      hasRelatedCode: false,
      refreshSuggestions: vi.fn(),
    });

    render(<RelatedCodePanel resourceId="test-resource" />);

    expect(screen.getByText('Related Code')).toBeInTheDocument();
    expect(screen.getByText('No related code files found')).toBeInTheDocument();
    expect(screen.getByText('Try refreshing suggestions')).toBeInTheDocument();
  });

  it('renders related code list', () => {
    (useAutoLinking as any).mockReturnValue({
      relatedCode: mockRelatedCode,
      isLoadingCode: false,
      codeError: null,
      hasRelatedCode: true,
      refreshSuggestions: vi.fn(),
    });

    render(<RelatedCodePanel resourceId="test-resource" />);

    expect(screen.getByText('Related Code')).toBeInTheDocument();
    expect(screen.getByText('utils.py')).toBeInTheDocument();
    expect(screen.getByText('parser.ts')).toBeInTheDocument();
    expect(screen.getByText('main.cpp')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument(); // Badge count
  });

  it('displays similarity scores', () => {
    (useAutoLinking as any).mockReturnValue({
      relatedCode: mockRelatedCode,
      isLoadingCode: false,
      codeError: null,
      hasRelatedCode: true,
      refreshSuggestions: vi.fn(),
    });

    render(<RelatedCodePanel resourceId="test-resource" />);

    expect(screen.getByText('85% match')).toBeInTheDocument();
    expect(screen.getByText('72% match')).toBeInTheDocument();
    expect(screen.getByText('45% match')).toBeInTheDocument();
  });

  it('displays relationship types', () => {
    (useAutoLinking as any).mockReturnValue({
      relatedCode: mockRelatedCode,
      isLoadingCode: false,
      codeError: null,
      hasRelatedCode: true,
      refreshSuggestions: vi.fn(),
    });

    render(<RelatedCodePanel resourceId="test-resource" />);

    expect(screen.getByText('Semantic')).toBeInTheDocument();
    expect(screen.getByText('Reference')).toBeInTheDocument();
    expect(screen.getByText('Citation')).toBeInTheDocument();
  });

  it('calls onCodeFileClick when code item is clicked', () => {
    const mockOnClick = vi.fn();
    (useAutoLinking as any).mockReturnValue({
      relatedCode: mockRelatedCode,
      isLoadingCode: false,
      codeError: null,
      hasRelatedCode: true,
      refreshSuggestions: vi.fn(),
    });

    render(<RelatedCodePanel resourceId="test-resource" onCodeFileClick={mockOnClick} />);

    const codeItem = screen.getByText('utils.py').closest('div[class*="cursor-pointer"]');
    if (codeItem) {
      fireEvent.click(codeItem);
      expect(mockOnClick).toHaveBeenCalledWith('code-1');
    }
  });

  it('calls refreshSuggestions when refresh button is clicked', async () => {
    const mockRefresh = vi.fn().mockResolvedValue(undefined);
    (useAutoLinking as any).mockReturnValue({
      relatedCode: mockRelatedCode,
      isLoadingCode: false,
      codeError: null,
      hasRelatedCode: true,
      refreshSuggestions: mockRefresh,
    });

    render(<RelatedCodePanel resourceId="test-resource" />);

    const refreshButton = screen.getByTitle('Refresh suggestions');
    fireEvent.click(refreshButton);

    expect(mockRefresh).toHaveBeenCalled();
  });

  it('shows refresh animation when refreshing', async () => {
    const mockRefresh = vi.fn().mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
    (useAutoLinking as any).mockReturnValue({
      relatedCode: mockRelatedCode,
      isLoadingCode: false,
      codeError: null,
      hasRelatedCode: true,
      refreshSuggestions: mockRefresh,
    });

    render(<RelatedCodePanel resourceId="test-resource" />);

    const refreshButton = screen.getByTitle('Refresh suggestions');
    fireEvent.click(refreshButton);

    // Check for spin animation class
    const icon = refreshButton.querySelector('svg');
    expect(icon?.classList.contains('animate-spin')).toBe(true);
  });

  it('displays descriptions when available', () => {
    (useAutoLinking as any).mockReturnValue({
      relatedCode: mockRelatedCode,
      isLoadingCode: false,
      codeError: null,
      hasRelatedCode: true,
      refreshSuggestions: vi.fn(),
    });

    render(<RelatedCodePanel resourceId="test-resource" />);

    expect(screen.getByText('Utility functions for data processing')).toBeInTheDocument();
    expect(screen.getByText('AST parser implementation')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    (useAutoLinking as any).mockReturnValue({
      relatedCode: mockRelatedCode,
      isLoadingCode: false,
      codeError: null,
      hasRelatedCode: true,
      refreshSuggestions: vi.fn(),
    });

    const { container } = render(
      <RelatedCodePanel resourceId="test-resource" className="custom-class" />
    );

    const panel = container.querySelector('.related-code-panel');
    expect(panel).toHaveClass('custom-class');
  });
});
