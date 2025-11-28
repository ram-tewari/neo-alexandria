import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AnnotationNotebook } from '../AnnotationNotebook';
import * as annotationHooks from '@/hooks/useAnnotations';
import { Annotation } from '@/types/annotation';

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

const mockAnnotations: Annotation[] = [
  {
    id: '1',
    resourceId: 'resource-1',
    userId: 'user-1',
    type: 'highlight',
    text: 'Important text',
    note: 'This is important',
    tags: ['key-concept'],
    color: '#fef08a',
    position: { start: 0, end: 14 },
    createdAt: new Date('2024-01-01'),
    updatedAt: new Date('2024-01-01'),
  },
  {
    id: '2',
    resourceId: 'resource-2',
    userId: 'user-1',
    type: 'note',
    text: 'Another text',
    note: 'My note',
    tags: [],
    color: '#bbf7d0',
    position: { start: 0, end: 12 },
    createdAt: new Date('2024-01-02'),
    updatedAt: new Date('2024-01-02'),
  },
];

describe('AnnotationNotebook', () => {
  it('displays loading state', () => {
    vi.spyOn(annotationHooks, 'useAllAnnotations').mockReturnValue({
      data: undefined,
      isLoading: true,
    } as any);

    render(<AnnotationNotebook />, { wrapper });

    const skeletons = document.querySelectorAll('.animate-pulse');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it('displays annotations when loaded', () => {
    vi.spyOn(annotationHooks, 'useAllAnnotations').mockReturnValue({
      data: mockAnnotations,
      isLoading: false,
    } as any);

    render(<AnnotationNotebook />, { wrapper });

    expect(screen.getByText('"Important text"')).toBeInTheDocument();
    expect(screen.getByText('"Another text"')).toBeInTheDocument();
  });

  it('displays annotation count', () => {
    vi.spyOn(annotationHooks, 'useAllAnnotations').mockReturnValue({
      data: mockAnnotations,
      isLoading: false,
    } as any);

    render(<AnnotationNotebook />, { wrapper });

    expect(screen.getByText('2 annotations')).toBeInTheDocument();
  });

  it('displays empty state when no annotations', () => {
    vi.spyOn(annotationHooks, 'useAllAnnotations').mockReturnValue({
      data: [],
      isLoading: false,
    } as any);

    render(<AnnotationNotebook />, { wrapper });

    expect(screen.getByText('No annotations yet')).toBeInTheDocument();
  });

  it('allows searching annotations', () => {
    vi.spyOn(annotationHooks, 'useAllAnnotations').mockReturnValue({
      data: mockAnnotations,
      isLoading: false,
    } as any);

    render(<AnnotationNotebook />, { wrapper });

    const searchInput = screen.getByPlaceholderText('Search annotations...');
    fireEvent.change(searchInput, { target: { value: 'important' } });

    expect(searchInput).toHaveValue('important');
  });

  it('toggles filter panel', () => {
    vi.spyOn(annotationHooks, 'useAllAnnotations').mockReturnValue({
      data: mockAnnotations,
      isLoading: false,
    } as any);

    render(<AnnotationNotebook />, { wrapper });

    const filterButton = screen.getByRole('button', { name: '' });
    fireEvent.click(filterButton);

    expect(screen.getByText('Colors')).toBeInTheDocument();
    expect(screen.getByText('Group By')).toBeInTheDocument();
  });

  it('displays tags for annotations', () => {
    vi.spyOn(annotationHooks, 'useAllAnnotations').mockReturnValue({
      data: mockAnnotations,
      isLoading: false,
    } as any);

    render(<AnnotationNotebook />, { wrapper });

    expect(screen.getByText('key-concept')).toBeInTheDocument();
  });

  it('displays notes for annotations', () => {
    vi.spyOn(annotationHooks, 'useAllAnnotations').mockReturnValue({
      data: mockAnnotations,
      isLoading: false,
    } as any);

    render(<AnnotationNotebook />, { wrapper });

    expect(screen.getByText('This is important')).toBeInTheDocument();
    expect(screen.getByText('My note')).toBeInTheDocument();
  });

  it('calls onAnnotationClick when annotation is clicked', () => {
    const onAnnotationClick = vi.fn();
    vi.spyOn(annotationHooks, 'useAllAnnotations').mockReturnValue({
      data: mockAnnotations,
      isLoading: false,
    } as any);

    render(<AnnotationNotebook onAnnotationClick={onAnnotationClick} />, { wrapper });

    // Find the annotation card and click it
    const annotationCards = screen.getAllByText('"Important text"');
    const annotationCard = annotationCards[0].closest('[style*="border"]');
    if (annotationCard) {
      fireEvent.click(annotationCard);
      expect(onAnnotationClick).toHaveBeenCalled();
    }
  });
});
