import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { TableDrawer } from '../TableDrawer';
import { useScholarlyAssets } from '@/lib/hooks/useScholarlyAssets';

// Mock the scholarly assets hook
vi.mock('@/lib/hooks/useScholarlyAssets', () => ({
  useScholarlyAssets: vi.fn(),
}));

// Mock toast
vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: vi.fn(),
  }),
}));

describe('TableDrawer', () => {
  const mockTables = [
    {
      id: 'table-1',
      table_number: 'Table 1',
      caption: 'Test Results',
      page_number: 1,
      data: [
        ['Header 1', 'Header 2'],
        ['Value 1', 'Value 2'],
        ['Value 3', 'Value 4'],
      ],
    },
    {
      id: 'table-2',
      table_number: 'Table 2',
      caption: 'Performance Metrics',
      page_number: 2,
      data: [
        ['Metric', 'Score'],
        ['Accuracy', '95%'],
      ],
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders loading state', () => {
    (useScholarlyAssets as any).mockReturnValue({
      tables: [],
      isLoadingTables: true,
      hasTables: false,
    });

    render(<TableDrawer resourceId="test-resource" />);

    // Should show skeleton loaders
    expect(document.querySelector('.space-y-4')).toBeInTheDocument();
  });

  it('renders empty state when no tables', () => {
    (useScholarlyAssets as any).mockReturnValue({
      tables: [],
      isLoadingTables: false,
      hasTables: false,
    });

    render(<TableDrawer resourceId="test-resource" />);

    expect(screen.getByText('No tables found in this document.')).toBeInTheDocument();
  });

  it('renders tables list', () => {
    (useScholarlyAssets as any).mockReturnValue({
      tables: mockTables,
      isLoadingTables: false,
      hasTables: true,
    });

    render(<TableDrawer resourceId="test-resource" />);

    expect(screen.getByText('Tables (2)')).toBeInTheDocument();
    expect(screen.getByText('Table 1')).toBeInTheDocument();
    expect(screen.getByText('Table 2')).toBeInTheDocument();
  });

  it('renders table captions', () => {
    (useScholarlyAssets as any).mockReturnValue({
      tables: mockTables,
      isLoadingTables: false,
      hasTables: true,
    });

    render(<TableDrawer resourceId="test-resource" />);

    expect(screen.getByText('Test Results')).toBeInTheDocument();
    expect(screen.getByText('Performance Metrics')).toBeInTheDocument();
  });

  it('renders table data', () => {
    (useScholarlyAssets as any).mockReturnValue({
      tables: mockTables,
      isLoadingTables: false,
      hasTables: true,
    });

    render(<TableDrawer resourceId="test-resource" />);

    expect(screen.getByText('Header 1')).toBeInTheDocument();
    expect(screen.getByText('Header 2')).toBeInTheDocument();
    expect(screen.getByText('Value 1')).toBeInTheDocument();
    expect(screen.getByText('Value 2')).toBeInTheDocument();
  });

  it('filters tables by search query', () => {
    (useScholarlyAssets as any).mockReturnValue({
      tables: mockTables,
      isLoadingTables: false,
      hasTables: true,
    });

    render(<TableDrawer resourceId="test-resource" />);

    const searchInput = screen.getByPlaceholderText('Search tables...');
    fireEvent.change(searchInput, { target: { value: 'Performance' } });

    // Should only show second table
    expect(screen.queryByText('Table 1')).not.toBeInTheDocument();
    expect(screen.getByText('Table 2')).toBeInTheDocument();
  });

  it('shows no results message when search has no matches', () => {
    (useScholarlyAssets as any).mockReturnValue({
      tables: mockTables,
      isLoadingTables: false,
      hasTables: true,
    });

    render(<TableDrawer resourceId="test-resource" />);

    const searchInput = screen.getByPlaceholderText('Search tables...');
    fireEvent.change(searchInput, { target: { value: 'xyz' } });

    expect(screen.getByText('No tables match your search.')).toBeInTheDocument();
  });

  it('renders copy buttons for different formats', () => {
    (useScholarlyAssets as any).mockReturnValue({
      tables: mockTables,
      isLoadingTables: false,
      hasTables: true,
    });

    render(<TableDrawer resourceId="test-resource" />);

    const csvButtons = screen.getAllByText('Copy CSV');
    const jsonButtons = screen.getAllByText('Copy JSON');
    const mdButtons = screen.getAllByText('Copy MD');

    expect(csvButtons).toHaveLength(2);
    expect(jsonButtons).toHaveLength(2);
    expect(mdButtons).toHaveLength(2);
  });

  it('renders jump to PDF button when callback provided', () => {
    (useScholarlyAssets as any).mockReturnValue({
      tables: mockTables,
      isLoadingTables: false,
      hasTables: true,
    });

    const mockJump = vi.fn();
    render(<TableDrawer resourceId="test-resource" onJumpToTable={mockJump} />);

    const jumpButtons = screen.getAllByText('Jump to PDF');
    expect(jumpButtons).toHaveLength(2);
  });

  it('calls onJumpToTable when jump button clicked', () => {
    (useScholarlyAssets as any).mockReturnValue({
      tables: mockTables,
      isLoadingTables: false,
      hasTables: true,
    });

    const mockJump = vi.fn();
    render(<TableDrawer resourceId="test-resource" onJumpToTable={mockJump} />);

    const jumpButtons = screen.getAllByText('Jump to PDF');
    fireEvent.click(jumpButtons[0]);

    expect(mockJump).toHaveBeenCalledWith('table-1', 1);
  });

  it('renders export button', () => {
    (useScholarlyAssets as any).mockReturnValue({
      tables: mockTables,
      isLoadingTables: false,
      hasTables: true,
    });

    render(<TableDrawer resourceId="test-resource" />);

    const exportButton = screen.getByTitle('Export all tables');
    expect(exportButton).toBeInTheDocument();
  });

  it('applies custom className', () => {
    (useScholarlyAssets as any).mockReturnValue({
      tables: mockTables,
      isLoadingTables: false,
      hasTables: true,
    });

    const { container } = render(
      <TableDrawer resourceId="test-resource" className="custom-class" />
    );

    const drawer = container.querySelector('.table-drawer');
    expect(drawer).toHaveClass('custom-class');
  });
});
