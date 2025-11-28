import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { QualityDashboard } from '../QualityDashboard';
import * as qualityHooks from '@/hooks/useQuality';

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

const mockMetrics = {
  totalResources: 150,
  averageQuality: 0.75,
  qualityDistribution: {
    bins: [
      { min: 0, max: 0.2, count: 5 },
      { min: 0.2, max: 0.4, count: 15 },
      { min: 0.4, max: 0.6, count: 30 },
      { min: 0.6, max: 0.8, count: 60 },
      { min: 0.8, max: 1.0, count: 40 },
    ],
    mean: 0.75,
    median: 0.78,
    stdDev: 0.15,
    total: 150,
  },
  topDimensions: [
    { name: 'Completeness', score: 0.85 },
    { name: 'Accuracy', score: 0.82 },
    { name: 'Consistency', score: 0.80 },
  ],
  bottomDimensions: [
    { name: 'Timeliness', score: 0.65 },
    { name: 'Relevance', score: 0.68 },
    { name: 'Accessibility', score: 0.70 },
  ],
  recentTrends: [],
  outlierCount: 12,
};

const mockDistribution = {
  bins: [
    { min: 0, max: 0.2, count: 5 },
    { min: 0.2, max: 0.4, count: 15 },
    { min: 0.4, max: 0.6, count: 30 },
    { min: 0.6, max: 0.8, count: 60 },
    { min: 0.8, max: 1.0, count: 40 },
  ],
  mean: 0.75,
  median: 0.78,
  stdDev: 0.15,
  total: 150,
};

const mockOutliers = [
  {
    resourceId: '1',
    title: 'Low Quality Resource',
    score: 0.35,
    issues: [],
    suggestions: ['Add complete metadata', 'Improve abstract quality'],
  },
];

describe('QualityDashboard', () => {
  it('displays loading state', () => {
    vi.spyOn(qualityHooks, 'useQualityMetrics').mockReturnValue({
      data: undefined,
      isLoading: true,
    } as any);
    vi.spyOn(qualityHooks, 'useQualityDistribution').mockReturnValue({
      data: undefined,
      isLoading: true,
    } as any);
    vi.spyOn(qualityHooks, 'useQualityOutliers').mockReturnValue({
      data: [],
      isLoading: true,
    } as any);
    vi.spyOn(qualityHooks, 'useRecalculateScores').mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
    } as any);

    render(<QualityDashboard />, { wrapper });

    expect(screen.getByText('Loading quality metrics...')).toBeInTheDocument();
  });

  it('displays quality metrics', () => {
    vi.spyOn(qualityHooks, 'useQualityMetrics').mockReturnValue({
      data: mockMetrics,
      isLoading: false,
    } as any);
    vi.spyOn(qualityHooks, 'useQualityDistribution').mockReturnValue({
      data: mockDistribution,
      isLoading: false,
    } as any);
    vi.spyOn(qualityHooks, 'useQualityOutliers').mockReturnValue({
      data: mockOutliers,
      isLoading: false,
    } as any);
    vi.spyOn(qualityHooks, 'useRecalculateScores').mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
    } as any);

    render(<QualityDashboard />, { wrapper });

    expect(screen.getByText('150')).toBeInTheDocument(); // Total resources
    expect(screen.getByText('75%')).toBeInTheDocument(); // Average quality
    expect(screen.getByText('78%')).toBeInTheDocument(); // Median
    expect(screen.getByText('12')).toBeInTheDocument(); // Outliers
  });

  it('displays quality distribution chart', () => {
    vi.spyOn(qualityHooks, 'useQualityMetrics').mockReturnValue({
      data: mockMetrics,
      isLoading: false,
    } as any);
    vi.spyOn(qualityHooks, 'useQualityDistribution').mockReturnValue({
      data: mockDistribution,
      isLoading: false,
    } as any);
    vi.spyOn(qualityHooks, 'useQualityOutliers').mockReturnValue({
      data: mockOutliers,
      isLoading: false,
    } as any);
    vi.spyOn(qualityHooks, 'useRecalculateScores').mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
    } as any);

    render(<QualityDashboard />, { wrapper });

    expect(screen.getByText('Quality Distribution')).toBeInTheDocument();
  });

  it('displays top and bottom dimensions', () => {
    vi.spyOn(qualityHooks, 'useQualityMetrics').mockReturnValue({
      data: mockMetrics,
      isLoading: false,
    } as any);
    vi.spyOn(qualityHooks, 'useQualityDistribution').mockReturnValue({
      data: mockDistribution,
      isLoading: false,
    } as any);
    vi.spyOn(qualityHooks, 'useQualityOutliers').mockReturnValue({
      data: mockOutliers,
      isLoading: false,
    } as any);
    vi.spyOn(qualityHooks, 'useRecalculateScores').mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
    } as any);

    render(<QualityDashboard />, { wrapper });

    expect(screen.getByText('Top Dimensions')).toBeInTheDocument();
    expect(screen.getByText('Needs Improvement')).toBeInTheDocument();
    expect(screen.getByText('Completeness')).toBeInTheDocument();
    expect(screen.getByText('Timeliness')).toBeInTheDocument();
  });

  it('displays outliers', () => {
    vi.spyOn(qualityHooks, 'useQualityMetrics').mockReturnValue({
      data: mockMetrics,
      isLoading: false,
    } as any);
    vi.spyOn(qualityHooks, 'useQualityDistribution').mockReturnValue({
      data: mockDistribution,
      isLoading: false,
    } as any);
    vi.spyOn(qualityHooks, 'useQualityOutliers').mockReturnValue({
      data: mockOutliers,
      isLoading: false,
    } as any);
    vi.spyOn(qualityHooks, 'useRecalculateScores').mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
    } as any);

    render(<QualityDashboard />, { wrapper });

    expect(screen.getByText('Quality Outliers')).toBeInTheDocument();
    expect(screen.getByText('Low Quality Resource')).toBeInTheDocument();
    expect(screen.getByText('• Add complete metadata')).toBeInTheDocument();
  });

  it('calls recalculate when button is clicked', () => {
    const mutateMock = vi.fn();
    vi.spyOn(qualityHooks, 'useQualityMetrics').mockReturnValue({
      data: mockMetrics,
      isLoading: false,
    } as any);
    vi.spyOn(qualityHooks, 'useQualityDistribution').mockReturnValue({
      data: mockDistribution,
      isLoading: false,
    } as any);
    vi.spyOn(qualityHooks, 'useQualityOutliers').mockReturnValue({
      data: mockOutliers,
      isLoading: false,
    } as any);
    vi.spyOn(qualityHooks, 'useRecalculateScores').mockReturnValue({
      mutate: mutateMock,
      isPending: false,
    } as any);

    render(<QualityDashboard />, { wrapper });

    const recalculateButton = screen.getByText('Recalculate');
    fireEvent.click(recalculateButton);

    expect(mutateMock).toHaveBeenCalled();
  });
});
