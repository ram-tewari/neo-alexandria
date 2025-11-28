import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { DiscoveryPanel } from '../DiscoveryPanel';
import * as graphHooks from '@/hooks/useGraph';

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

describe('DiscoveryPanel', () => {
  it('displays source and target nodes', () => {
    vi.spyOn(graphHooks, 'useFindPaths').mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
    } as any);
    vi.spyOn(graphHooks, 'useGenerateHypotheses').mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
    } as any);
    vi.spyOn(graphHooks, 'useValidateHypothesis').mockReturnValue({
      mutate: vi.fn(),
    } as any);

    render(
      <DiscoveryPanel sourceNode="node-1" targetNode="node-2" />,
      { wrapper }
    );

    expect(screen.getByText('node-1')).toBeInTheDocument();
    expect(screen.getByText('node-2')).toBeInTheDocument();
  });

  it('shows empty state when no nodes selected', () => {
    vi.spyOn(graphHooks, 'useFindPaths').mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
    } as any);
    vi.spyOn(graphHooks, 'useGenerateHypotheses').mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
    } as any);
    vi.spyOn(graphHooks, 'useValidateHypothesis').mockReturnValue({
      mutate: vi.fn(),
    } as any);

    render(
      <DiscoveryPanel sourceNode="" targetNode="" />,
      { wrapper }
    );

    expect(screen.getByText(/Select source and target nodes/i)).toBeInTheDocument();
  });

  it('disables buttons when nodes not selected', () => {
    vi.spyOn(graphHooks, 'useFindPaths').mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
    } as any);
    vi.spyOn(graphHooks, 'useGenerateHypotheses').mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
    } as any);
    vi.spyOn(graphHooks, 'useValidateHypothesis').mockReturnValue({
      mutate: vi.fn(),
    } as any);

    render(
      <DiscoveryPanel sourceNode="" targetNode="" />,
      { wrapper }
    );

    const findPathsButton = screen.getByText('Find Paths');
    const hypothesesButton = screen.getByText('Hypotheses');

    expect(findPathsButton).toBeDisabled();
    expect(hypothesesButton).toBeDisabled();
  });

  it('calls findPaths when button is clicked', () => {
    const mutateMock = vi.fn();
    vi.spyOn(graphHooks, 'useFindPaths').mockReturnValue({
      mutate: mutateMock,
      isPending: false,
    } as any);
    vi.spyOn(graphHooks, 'useGenerateHypotheses').mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
    } as any);
    vi.spyOn(graphHooks, 'useValidateHypothesis').mockReturnValue({
      mutate: vi.fn(),
    } as any);

    render(
      <DiscoveryPanel sourceNode="node-1" targetNode="node-2" />,
      { wrapper }
    );

    const findPathsButton = screen.getByText('Find Paths');
    fireEvent.click(findPathsButton);

    expect(mutateMock).toHaveBeenCalledWith({
      sourceNodeId: 'node-1',
      targetNodeId: 'node-2',
      maxDepth: 3,
      minScore: 0.5,
    });
  });

  it('displays discovery paths when available', () => {
    vi.spyOn(graphHooks, 'useFindPaths').mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
      data: [
        {
          nodes: ['node-1', 'node-2', 'node-3'],
          edges: [],
          score: 0.85,
        },
      ],
    } as any);
    vi.spyOn(graphHooks, 'useGenerateHypotheses').mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
    } as any);
    vi.spyOn(graphHooks, 'useValidateHypothesis').mockReturnValue({
      mutate: vi.fn(),
    } as any);

    render(
      <DiscoveryPanel sourceNode="node-1" targetNode="node-2" />,
      { wrapper }
    );

    expect(screen.getByText(/Discovery Paths/i)).toBeInTheDocument();
    expect(screen.getByText('85% confidence')).toBeInTheDocument();
  });

  it('displays hypotheses when available', () => {
    vi.spyOn(graphHooks, 'useFindPaths').mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
    } as any);
    vi.spyOn(graphHooks, 'useGenerateHypotheses').mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
      data: [
        {
          id: 'hyp-1',
          description: 'Test hypothesis',
          plausibility: 0.75,
          evidence: ['Evidence 1', 'Evidence 2'],
          status: 'pending' as const,
          createdAt: new Date(),
        },
      ],
    } as any);
    vi.spyOn(graphHooks, 'useValidateHypothesis').mockReturnValue({
      mutate: vi.fn(),
    } as any);

    render(
      <DiscoveryPanel sourceNode="node-1" targetNode="node-2" />,
      { wrapper }
    );

    expect(screen.getAllByText(/Hypotheses/i).length).toBeGreaterThan(0);
    expect(screen.getByText('Test hypothesis')).toBeInTheDocument();
    expect(screen.getByText('75%')).toBeInTheDocument();
  });

  it('shows validate and reject buttons for pending hypotheses', () => {
    vi.spyOn(graphHooks, 'useFindPaths').mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
    } as any);
    vi.spyOn(graphHooks, 'useGenerateHypotheses').mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
      data: [
        {
          id: 'hyp-1',
          description: 'Test hypothesis',
          plausibility: 0.75,
          evidence: [],
          status: 'pending' as const,
          createdAt: new Date(),
        },
      ],
    } as any);
    vi.spyOn(graphHooks, 'useValidateHypothesis').mockReturnValue({
      mutate: vi.fn(),
    } as any);

    render(
      <DiscoveryPanel sourceNode="node-1" targetNode="node-2" />,
      { wrapper }
    );

    expect(screen.getByText('Validate')).toBeInTheDocument();
    expect(screen.getByText('Reject')).toBeInTheDocument();
  });
});
