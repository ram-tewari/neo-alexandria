import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RecommendationFeed } from '../RecommendationFeed';
import * as recommendationHooks from '@/hooks/useRecommendations';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>
    {children}
  </QueryClientProvider>
);

const mockRecommendations = [
  {
    resource: {
      id: '1',
      title: 'Fresh Paper',
      authors: ['Author'],
      abstract: 'Abstract',
      type: 'pdf' as const,
      qualityScore: 85,
      classification: ['ML'],
      createdAt: new Date(),
    },
    score: 0.9,
    category: 'fresh' as const,
    explanation: 'Fresh content',
    reasons: ['New'],
  },
  {
    resource: {
      id: '2',
      title: 'Similar Paper',
      authors: ['Author'],
      abstract: 'Abstract',
      type: 'pdf' as const,
      qualityScore: 80,
      classification: ['AI'],
      createdAt: new Date(),
    },
    score: 0.85,
    category: 'similar' as const,
    explanation: 'Similar content',
    reasons: ['Similar'],
  },
];

describe('RecommendationFeed', () => {
  it('displays loading state', () => {
    vi.spyOn(recommendationHooks, 'useRecommendations').mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
    } as any);

    render(<RecommendationFeed />, { wrapper });
    
    // Should show loading skeleton cards
    const skeletons = document.querySelectorAll('.animate-pulse');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it('displays recommendations when loaded', () => {
    vi.spyOn(recommendationHooks, 'useRecommendations').mockReturnValue({
      data: mockRecommendations,
      isLoading: false,
      error: null,
    } as any);

    render(<RecommendationFeed />, { wrapper });
    
    expect(screen.getByText('Fresh Paper')).toBeInTheDocument();
    expect(screen.getByText('Similar Paper')).toBeInTheDocument();
  });

  it('displays error state', () => {
    vi.spyOn(recommendationHooks, 'useRecommendations').mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error('Failed to load'),
    } as any);

    render(<RecommendationFeed />, { wrapper });
    
    expect(screen.getByText('Failed to load recommendations')).toBeInTheDocument();
    expect(screen.getByText('Try Again')).toBeInTheDocument();
  });

  it('displays empty state when no recommendations', () => {
    vi.spyOn(recommendationHooks, 'useRecommendations').mockReturnValue({
      data: [],
      isLoading: false,
      error: null,
    } as any);

    render(<RecommendationFeed />, { wrapper });
    
    expect(screen.getByText('No recommendations yet')).toBeInTheDocument();
  });

  it('filters recommendations by category', async () => {
    vi.spyOn(recommendationHooks, 'useRecommendations').mockReturnValue({
      data: mockRecommendations,
      isLoading: false,
      error: null,
    } as any);

    render(<RecommendationFeed />, { wrapper });
    
    // Get the button from the filter section (not the heading)
    const buttons = screen.getAllByText('Fresh Finds');
    const freshButton = buttons[0]; // First one is the filter button
    fireEvent.click(freshButton);
    
    await waitFor(() => {
      expect(freshButton).toHaveClass('bg-primary-600');
    });
  });

  it('calls onPreferencesClick when settings button is clicked', () => {
    const onPreferencesClick = vi.fn();
    vi.spyOn(recommendationHooks, 'useRecommendations').mockReturnValue({
      data: mockRecommendations,
      isLoading: false,
      error: null,
    } as any);

    render(<RecommendationFeed onPreferencesClick={onPreferencesClick} />, { wrapper });
    
    const settingsButton = screen.getByLabelText('Preferences');
    fireEvent.click(settingsButton);
    
    expect(onPreferencesClick).toHaveBeenCalled();
  });

  it('groups recommendations by category in all view', () => {
    vi.spyOn(recommendationHooks, 'useRecommendations').mockReturnValue({
      data: mockRecommendations,
      isLoading: false,
      error: null,
    } as any);

    render(<RecommendationFeed />, { wrapper });
    
    // Check for category headings (not buttons)
    expect(screen.getAllByText('Fresh Finds').length).toBeGreaterThan(1);
    expect(screen.getAllByText('Similar to Recent').length).toBeGreaterThan(0);
  });
});
