import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { UserProfile } from '../UserProfile';
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

const mockPreferences = {
  interests: ['Machine Learning', 'AI'],
  diversity: 0.6,
  novelty: 0.7,
  recency: 0.5,
  domains: ['Computer Science'],
};

const mockMetrics = {
  clickThroughRate: 0.35,
  diversityScore: 0.72,
  noveltyScore: 0.68,
  userSatisfaction: 0.85,
  totalRecommendations: 150,
  totalClicks: 52,
};

describe('UserProfile', () => {
  it('displays loading state', () => {
    vi.spyOn(recommendationHooks, 'useUserPreferences').mockReturnValue({
      data: undefined,
      isLoading: true,
    } as any);

    render(<UserProfile />, { wrapper });
    
    // Check for loading skeleton with pulse animation
    const skeletons = document.querySelectorAll('.animate-pulse');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it('displays user preferences', () => {
    vi.spyOn(recommendationHooks, 'useUserPreferences').mockReturnValue({
      data: mockPreferences,
      isLoading: false,
    } as any);
    vi.spyOn(recommendationHooks, 'useRecommendationMetrics').mockReturnValue({
      data: mockMetrics,
    } as any);

    render(<UserProfile />, { wrapper });
    
    expect(screen.getByText('Machine Learning')).toBeInTheDocument();
    expect(screen.getByText('AI')).toBeInTheDocument();
    expect(screen.getByText('Computer Science')).toBeInTheDocument();
  });

  it('displays preference sliders with correct values', () => {
    vi.spyOn(recommendationHooks, 'useUserPreferences').mockReturnValue({
      data: mockPreferences,
      isLoading: false,
    } as any);

    render(<UserProfile />, { wrapper });
    
    expect(screen.getByText('60%')).toBeInTheDocument(); // Diversity
    expect(screen.getByText('70%')).toBeInTheDocument(); // Novelty
    expect(screen.getByText('50%')).toBeInTheDocument(); // Recency
  });

  it('allows adding new interests', async () => {
    vi.spyOn(recommendationHooks, 'useUserPreferences').mockReturnValue({
      data: mockPreferences,
      isLoading: false,
    } as any);

    render(<UserProfile />, { wrapper });
    
    const input = screen.getByPlaceholderText('Add an interest...');
    const addButton = screen.getByLabelText('Add interest');
    
    fireEvent.change(input, { target: { value: 'Deep Learning' } });
    fireEvent.click(addButton);
    
    await waitFor(() => {
      expect(screen.getByText('Deep Learning')).toBeInTheDocument();
    });
  });

  it('allows removing interests', async () => {
    vi.spyOn(recommendationHooks, 'useUserPreferences').mockReturnValue({
      data: mockPreferences,
      isLoading: false,
    } as any);

    render(<UserProfile />, { wrapper });
    
    const removeButton = screen.getByLabelText('Remove Machine Learning');
    fireEvent.click(removeButton);
    
    await waitFor(() => {
      expect(screen.queryByText('Machine Learning')).not.toBeInTheDocument();
    });
  });

  it('allows adjusting preference sliders', async () => {
    vi.spyOn(recommendationHooks, 'useUserPreferences').mockReturnValue({
      data: mockPreferences,
      isLoading: false,
    } as any);

    render(<UserProfile />, { wrapper });
    
    const diversitySlider = screen.getAllByRole('slider')[0];
    fireEvent.change(diversitySlider, { target: { value: '0.8' } });
    
    await waitFor(() => {
      expect(screen.getByText('80%')).toBeInTheDocument();
    });
  });

  it('displays performance metrics', () => {
    vi.spyOn(recommendationHooks, 'useUserPreferences').mockReturnValue({
      data: mockPreferences,
      isLoading: false,
    } as any);
    vi.spyOn(recommendationHooks, 'useRecommendationMetrics').mockReturnValue({
      data: mockMetrics,
    } as any);

    render(<UserProfile />, { wrapper });
    
    expect(screen.getByText('35%')).toBeInTheDocument(); // CTR
    expect(screen.getByText('72%')).toBeInTheDocument(); // Diversity
    expect(screen.getByText('68%')).toBeInTheDocument(); // Novelty
    expect(screen.getByText('150')).toBeInTheDocument(); // Total recommendations
    expect(screen.getByText('52')).toBeInTheDocument(); // Total clicks
    expect(screen.getByText('85%')).toBeInTheDocument(); // Satisfaction
  });

  it('calls onClose when cancel button is clicked', () => {
    const onClose = vi.fn();
    vi.spyOn(recommendationHooks, 'useUserPreferences').mockReturnValue({
      data: mockPreferences,
      isLoading: false,
    } as any);

    render(<UserProfile onClose={onClose} />, { wrapper });
    
    const cancelButton = screen.getByText('Cancel');
    fireEvent.click(cancelButton);
    
    expect(onClose).toHaveBeenCalled();
  });

  it('saves preferences when save button is clicked', async () => {
    const mutateMock = vi.fn();
    vi.spyOn(recommendationHooks, 'useUserPreferences').mockReturnValue({
      data: mockPreferences,
      isLoading: false,
    } as any);
    vi.spyOn(recommendationHooks, 'useUpdatePreferences').mockReturnValue({
      mutate: mutateMock,
      isPending: false,
    } as any);

    render(<UserProfile />, { wrapper });
    
    const saveButton = screen.getByText('Save Preferences');
    fireEvent.click(saveButton);
    
    expect(mutateMock).toHaveBeenCalled();
  });
});
