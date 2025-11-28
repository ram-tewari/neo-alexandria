import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RecommendationCard } from '../RecommendationCard';
import { Recommendation } from '@/types/recommendation';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

const mockRecommendation: Recommendation = {
  resource: {
    id: '1',
    title: 'Test Paper',
    authors: ['Author One', 'Author Two'],
    abstract: 'This is a test abstract',
    type: 'pdf',
    qualityScore: 85,
    classification: ['Machine Learning', 'AI'],
    createdAt: new Date(),
  },
  score: 0.92,
  category: 'fresh',
  explanation: 'This matches your interests',
  reasons: ['Similar to recent reads', 'High quality score'],
};

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>
    {children}
  </QueryClientProvider>
);

describe('RecommendationCard', () => {
  it('displays recommendation information correctly', () => {
    render(<RecommendationCard recommendation={mockRecommendation} />, { wrapper });
    
    expect(screen.getByText('Test Paper')).toBeInTheDocument();
    expect(screen.getByText(/Author One, Author Two/)).toBeInTheDocument();
    expect(screen.getByText('This is a test abstract')).toBeInTheDocument();
    expect(screen.getByText('92% match')).toBeInTheDocument();
  });

  it('displays category badge with correct label', () => {
    render(<RecommendationCard recommendation={mockRecommendation} />, { wrapper });
    
    expect(screen.getByText('Fresh Find')).toBeInTheDocument();
  });

  it('displays classification tags', () => {
    render(<RecommendationCard recommendation={mockRecommendation} />, { wrapper });
    
    expect(screen.getByText('Machine Learning')).toBeInTheDocument();
    expect(screen.getByText('AI')).toBeInTheDocument();
  });

  it('shows explanation when button is clicked', () => {
    render(<RecommendationCard recommendation={mockRecommendation} />, { wrapper });
    
    const explainButton = screen.getByText('Why recommended?');
    fireEvent.click(explainButton);
    
    expect(screen.getByText('This matches your interests')).toBeInTheDocument();
    expect(screen.getByText(/Similar to recent reads/)).toBeInTheDocument();
  });

  it('calls onResourceClick when card is clicked', () => {
    const onResourceClick = vi.fn();
    render(
      <RecommendationCard
        recommendation={mockRecommendation}
        onResourceClick={onResourceClick}
      />,
      { wrapper }
    );
    
    const card = screen.getByText('Test Paper').closest('div')?.parentElement;
    if (card) {
      fireEvent.click(card);
      expect(onResourceClick).toHaveBeenCalledWith('1');
    }
  });

  it('handles like feedback', () => {
    render(<RecommendationCard recommendation={mockRecommendation} />, { wrapper });
    
    const likeButton = screen.getByLabelText('Like recommendation');
    fireEvent.click(likeButton);
    
    // Button should have active state
    expect(likeButton).toHaveClass('bg-green-100');
  });

  it('handles dislike feedback', () => {
    render(<RecommendationCard recommendation={mockRecommendation} />, { wrapper });
    
    const dislikeButton = screen.getByLabelText('Dislike recommendation');
    fireEvent.click(dislikeButton);
    
    // Button should have active state
    expect(dislikeButton).toHaveClass('bg-red-100');
  });

  it('truncates long author lists', () => {
    const manyAuthors = {
      ...mockRecommendation,
      resource: {
        ...mockRecommendation.resource,
        authors: ['A1', 'A2', 'A3', 'A4'],
      },
    };
    
    render(<RecommendationCard recommendation={manyAuthors} />, { wrapper });
    
    expect(screen.getByText(/A1, A2 \+2/)).toBeInTheDocument();
  });
});
