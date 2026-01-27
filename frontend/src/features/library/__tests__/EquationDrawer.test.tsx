import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { EquationDrawer } from '../EquationDrawer';
import { useScholarlyAssets } from '@/lib/hooks/useScholarlyAssets';

// Mock the scholarly assets hook
vi.mock('@/lib/hooks/useScholarlyAssets', () => ({
  useScholarlyAssets: vi.fn(),
}));

// Mock react-katex
vi.mock('react-katex', () => ({
  InlineMath: ({ math }: { math: string }) => <span data-testid="inline-math">{math}</span>,
  BlockMath: ({ math }: { math: string }) => <div data-testid="block-math">{math}</div>,
}));

// Mock toast
vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: vi.fn(),
  }),
}));

describe('EquationDrawer', () => {
  const mockEquations = [
    {
      id: 'eq-1',
      latex: 'E = mc^2',
      equation_number: 'Equation 1',
      page_number: 1,
    },
    {
      id: 'eq-2',
      latex: 'a^2 + b^2 = c^2',
      equation_number: 'Equation 2',
      page_number: 2,
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders loading state', () => {
    (useScholarlyAssets as any).mockReturnValue({
      equations: [],
      isLoadingEquations: true,
      hasEquations: false,
    });

    render(<EquationDrawer resourceId="test-resource" />);

    // Should show skeleton loaders
    expect(document.querySelector('.space-y-4')).toBeInTheDocument();
  });

  it('renders empty state when no equations', () => {
    (useScholarlyAssets as any).mockReturnValue({
      equations: [],
      isLoadingEquations: false,
      hasEquations: false,
    });

    render(<EquationDrawer resourceId="test-resource" />);

    expect(screen.getByText('No equations found in this document.')).toBeInTheDocument();
  });

  it('renders equations list', () => {
    (useScholarlyAssets as any).mockReturnValue({
      equations: mockEquations,
      isLoadingEquations: false,
      hasEquations: true,
    });

    render(<EquationDrawer resourceId="test-resource" />);

    expect(screen.getByText('Equations (2)')).toBeInTheDocument();
    expect(screen.getByText('Equation 1')).toBeInTheDocument();
    expect(screen.getByText('Equation 2')).toBeInTheDocument();
  });

  it('renders equation LaTeX', () => {
    (useScholarlyAssets as any).mockReturnValue({
      equations: mockEquations,
      isLoadingEquations: false,
      hasEquations: true,
    });

    render(<EquationDrawer resourceId="test-resource" />);

    const blockMaths = screen.getAllByTestId('block-math');
    expect(blockMaths).toHaveLength(2);
    expect(blockMaths[0]).toHaveTextContent('E = mc^2');
    expect(blockMaths[1]).toHaveTextContent('a^2 + b^2 = c^2');
  });

  it('filters equations by search query', () => {
    (useScholarlyAssets as any).mockReturnValue({
      equations: mockEquations,
      isLoadingEquations: false,
      hasEquations: true,
    });

    render(<EquationDrawer resourceId="test-resource" />);

    const searchInput = screen.getByPlaceholderText('Search equations...');
    fireEvent.change(searchInput, { target: { value: 'mc' } });

    // Should only show first equation
    expect(screen.getByText('Equation 1')).toBeInTheDocument();
    expect(screen.queryByText('Equation 2')).not.toBeInTheDocument();
  });

  it('shows no results message when search has no matches', () => {
    (useScholarlyAssets as any).mockReturnValue({
      equations: mockEquations,
      isLoadingEquations: false,
      hasEquations: true,
    });

    render(<EquationDrawer resourceId="test-resource" />);

    const searchInput = screen.getByPlaceholderText('Search equations...');
    fireEvent.change(searchInput, { target: { value: 'xyz' } });

    expect(screen.getByText('No equations match your search.')).toBeInTheDocument();
  });

  it('renders copy LaTeX button', () => {
    (useScholarlyAssets as any).mockReturnValue({
      equations: mockEquations,
      isLoadingEquations: false,
      hasEquations: true,
    });

    render(<EquationDrawer resourceId="test-resource" />);

    const copyButtons = screen.getAllByText('Copy LaTeX');
    expect(copyButtons).toHaveLength(2);
  });

  it('renders jump to PDF button when callback provided', () => {
    (useScholarlyAssets as any).mockReturnValue({
      equations: mockEquations,
      isLoadingEquations: false,
      hasEquations: true,
    });

    const mockJump = vi.fn();
    render(<EquationDrawer resourceId="test-resource" onJumpToEquation={mockJump} />);

    const jumpButtons = screen.getAllByText('Jump to PDF');
    expect(jumpButtons).toHaveLength(2);
  });

  it('calls onJumpToEquation when jump button clicked', () => {
    (useScholarlyAssets as any).mockReturnValue({
      equations: mockEquations,
      isLoadingEquations: false,
      hasEquations: true,
    });

    const mockJump = vi.fn();
    render(<EquationDrawer resourceId="test-resource" onJumpToEquation={mockJump} />);

    const jumpButtons = screen.getAllByText('Jump to PDF');
    fireEvent.click(jumpButtons[0]);

    expect(mockJump).toHaveBeenCalledWith('eq-1', 1);
  });

  it('renders export button', () => {
    (useScholarlyAssets as any).mockReturnValue({
      equations: mockEquations,
      isLoadingEquations: false,
      hasEquations: true,
    });

    render(<EquationDrawer resourceId="test-resource" />);

    const exportButton = screen.getByTitle('Export all equations');
    expect(exportButton).toBeInTheDocument();
  });

  it('applies custom className', () => {
    (useScholarlyAssets as any).mockReturnValue({
      equations: mockEquations,
      isLoadingEquations: false,
      hasEquations: true,
    });

    const { container } = render(
      <EquationDrawer resourceId="test-resource" className="custom-class" />
    );

    const drawer = container.querySelector('.equation-drawer');
    expect(drawer).toHaveClass('custom-class');
  });
});
