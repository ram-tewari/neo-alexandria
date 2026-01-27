import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { RelatedPapersPanel } from '../RelatedPapersPanel';
import { useAutoLinking } from '@/lib/hooks/useAutoLinking';

// Mock the auto-linking hook
vi.mock('@/lib/hooks/useAutoLinking', () => ({
  useAutoLinking: vi.fn(),
}));

describe('RelatedPapersPanel', () => {
  const mockRelatedPapers = [
    {
      resource: {
        id: 'paper-1',
        title: 'Deep Learning for NLP',
        description: 'A comprehensive survey of deep learning techniques',
        type: 'pdf',
      },
      similarity: 0.92,
      relationship_type: 'citation' as const,
    },
    {
      resource: {
        id: 'paper-2',
        title: 'Transformer Architecture',
        description: 'Attention is all you need',
        type: 'pdf',
      },
      similarity: 0.78,
      relationship_type: 'semantic' as const,
    },
    {
      resource: {
        id: 'paper-3',
        title: 'BERT: Pre-training',
        description: 'Bidirectional encoder representations',
        type: 'pdf',
      },
      similarity: 0.55,
      relationship_type: 'code_reference' as const,
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders loading state', () => {
    (useAutoLinking as any).mockReturnValue({
      relatedPapers: [],
      isLoadingPapers: true,
      papersError: null,
      hasRelatedPapers: false,
      refreshSuggestions: vi.fn(),
    });

    render(<RelatedPapersPanel resourceId="test-resource" />);

    expect(screen.getByText('Related Papers')).toBeInTheDocument();
    // Should show skeleton loaders
    const skeletons = document.querySelectorAll('.animate-pulse');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it('renders error state', () => {
    (useAutoLinking as any).mockReturnValue({
      relatedPapers: [],
      isLoadingPapers: false,
      papersError: new Error('Failed to load'),
      hasRelatedPapers: false,
      refreshSuggestions: vi.fn(),
    });

    render(<RelatedPapersPanel resourceId="test-resource" />);

    expect(screen.getByText('Related Papers')).toBeInTheDocument();
    expect(screen.getByText(/Failed to load related papers/i)).toBeInTheDocument();
  });

  it('renders empty state when no related papers', () => {
    (useAutoLinking as any).mockReturnValue({
      relatedPapers: [],
      isLoadingPapers: false,
      papersError: null,
      hasRelatedPapers: false,
      refreshSuggestions: vi.fn(),
    });

    render(<RelatedPapersPanel resourceId="test-resource" />);

    expect(screen.getByText('Related Papers')).toBeInTheDocument();
    expect(screen.getByText('No related papers found')).toBeInTheDocument();
    expect(screen.getByText('Try refreshing suggestions')).toBeInTheDocument();
  });

  it('renders related papers list', () => {
    (useAutoLinking as any).mockReturnValue({
      relatedPapers: mockRelatedPapers,
      isLoadingPapers: false,
      papersError: null,
      hasRelatedPapers: true,
      refreshSuggestions: vi.fn(),
    });

    render(<RelatedPapersPanel resourceId="test-resource" />);

    expect(screen.getByText('Related Papers')).toBeInTheDocument();
    expect(screen.getByText('Deep Learning for NLP')).toBeInTheDocument();
    expect(screen.getByText('Transformer Architecture')).toBeInTheDocument();
    expect(screen.getByText('BERT: Pre-training')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument(); // Badge count
  });

  it('displays similarity scores', () => {
    (useAutoLinking as any).mockReturnValue({
      relatedPapers: mockRelatedPapers,
      isLoadingPapers: false,
      papersError: null,
      hasRelatedPapers: true,
      refreshSuggestions: vi.fn(),
    });

    render(<RelatedPapersPanel resourceId="test-resource" />);

    expect(screen.getByText('92% match')).toBeInTheDocument();
    expect(screen.getByText('78% match')).toBeInTheDocument();
    expect(screen.getByText('55% match')).toBeInTheDocument();
  });

  it('displays relationship types', () => {
    (useAutoLinking as any).mockReturnValue({
      relatedPapers: mockRelatedPapers,
      isLoadingPapers: false,
      papersError: null,
      hasRelatedPapers: true,
      refreshSuggestions: vi.fn(),
    });

    render(<RelatedPapersPanel resourceId="test-resource" />);

    expect(screen.getByText('Citation')).toBeInTheDocument();
    expect(screen.getByText('Semantic')).toBeInTheDocument();
    expect(screen.getByText('Reference')).toBeInTheDocument();
  });

  it('shows citation relationship indicator', () => {
    (useAutoLinking as any).mockReturnValue({
      relatedPapers: mockRelatedPapers,
      isLoadingPapers: false,
      papersError: null,
      hasRelatedPapers: true,
      refreshSuggestions: vi.fn(),
    });

    render(<RelatedPapersPanel resourceId="test-resource" />);

    expect(screen.getByText('Citation relationship detected')).toBeInTheDocument();
  });

  it('calls onPaperClick when paper item is clicked', () => {
    const mockOnClick = vi.fn();
    (useAutoLinking as any).mockReturnValue({
      relatedPapers: mockRelatedPapers,
      isLoadingPapers: false,
      papersError: null,
      hasRelatedPapers: true,
      refreshSuggestions: vi.fn(),
    });

    render(<RelatedPapersPanel resourceId="test-resource" onPaperClick={mockOnClick} />);

    const paperItem = screen.getByText('Deep Learning for NLP').closest('div[class*="cursor-pointer"]');
    if (paperItem) {
      fireEvent.click(paperItem);
      expect(mockOnClick).toHaveBeenCalledWith('paper-1');
    }
  });

  it('calls refreshSuggestions when refresh button is clicked', async () => {
    const mockRefresh = vi.fn().mockResolvedValue(undefined);
    (useAutoLinking as any).mockReturnValue({
      relatedPapers: mockRelatedPapers,
      isLoadingPapers: false,
      papersError: null,
      hasRelatedPapers: true,
      refreshSuggestions: mockRefresh,
    });

    render(<RelatedPapersPanel resourceId="test-resource" />);

    const refreshButton = screen.getByTitle('Refresh suggestions');
    fireEvent.click(refreshButton);

    expect(mockRefresh).toHaveBeenCalled();
  });

  it('shows refresh animation when refreshing', async () => {
    const mockRefresh = vi.fn().mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
    (useAutoLinking as any).mockReturnValue({
      relatedPapers: mockRelatedPapers,
      isLoadingPapers: false,
      papersError: null,
      hasRelatedPapers: true,
      refreshSuggestions: mockRefresh,
    });

    render(<RelatedPapersPanel resourceId="test-resource" />);

    const refreshButton = screen.getByTitle('Refresh suggestions');
    fireEvent.click(refreshButton);

    // Check for spin animation class
    const icon = refreshButton.querySelector('svg');
    expect(icon?.classList.contains('animate-spin')).toBe(true);
  });

  it('displays descriptions when available', () => {
    (useAutoLinking as any).mockReturnValue({
      relatedPapers: mockRelatedPapers,
      isLoadingPapers: false,
      papersError: null,
      hasRelatedPapers: true,
      refreshSuggestions: vi.fn(),
    });

    render(<RelatedPapersPanel resourceId="test-resource" />);

    expect(screen.getByText('A comprehensive survey of deep learning techniques')).toBeInTheDocument();
    expect(screen.getByText('Attention is all you need')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    (useAutoLinking as any).mockReturnValue({
      relatedPapers: mockRelatedPapers,
      isLoadingPapers: false,
      papersError: null,
      hasRelatedPapers: true,
      refreshSuggestions: vi.fn(),
    });

    const { container } = render(
      <RelatedPapersPanel resourceId="test-resource" className="custom-class" />
    );

    const panel = container.querySelector('.related-papers-panel');
    expect(panel).toHaveClass('custom-class');
  });
});
