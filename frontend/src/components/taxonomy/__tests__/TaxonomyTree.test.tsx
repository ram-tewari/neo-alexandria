import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { TaxonomyTree } from '../TaxonomyTree';
import { TaxonomyNode } from '@/types/taxonomy';

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

const mockNodes: TaxonomyNode[] = [
  {
    id: '1',
    name: 'Computer Science',
    children: [
      {
        id: '2',
        name: 'Machine Learning',
        children: [],
        resourceCount: 25,
        depth: 1,
        path: ['Computer Science', 'Machine Learning'],
      },
    ],
    resourceCount: 50,
    depth: 0,
    path: ['Computer Science'],
  },
];

describe('TaxonomyTree', () => {
  it('renders taxonomy nodes', () => {
    render(<TaxonomyTree nodes={mockNodes} />, { wrapper });
    
    expect(screen.getByText('Computer Science')).toBeInTheDocument();
    expect(screen.getByText('50')).toBeInTheDocument();
  });

  it('displays empty state when no nodes', () => {
    render(<TaxonomyTree nodes={[]} />, { wrapper });
    
    expect(screen.getByText(/No categories yet/i)).toBeInTheDocument();
  });

  it('shows add root button', () => {
    render(<TaxonomyTree nodes={[]} />, { wrapper });
    
    expect(screen.getByText('Add Root')).toBeInTheDocument();
  });
});
