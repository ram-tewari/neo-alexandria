import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MetadataPanel } from '../MetadataPanel';
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

describe('MetadataPanel', () => {
  const mockMetadata = {
    title: 'Test Paper',
    authors: ['John Doe', 'Jane Smith'],
    abstract: 'This is a test abstract',
    keywords: ['test', 'paper'],
    publication_date: '2024-01-01',
    doi: '10.1234/test',
    journal: 'Test Journal',
    volume: '1',
    issue: '2',
    pages: '1-10',
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders loading state', () => {
    (useScholarlyAssets as any).mockReturnValue({
      metadata: undefined,
      isLoadingMetadata: true,
    });

    render(<MetadataPanel resourceId="test-resource" />);

    // Should show skeleton loaders
    expect(document.querySelector('.space-y-4')).toBeInTheDocument();
  });

  it('renders empty state when no metadata', () => {
    (useScholarlyAssets as any).mockReturnValue({
      metadata: undefined,
      isLoadingMetadata: false,
    });

    render(<MetadataPanel resourceId="test-resource" />);

    expect(screen.getByText('No metadata available for this document.')).toBeInTheDocument();
  });

  it('renders metadata fields', () => {
    (useScholarlyAssets as any).mockReturnValue({
      metadata: mockMetadata,
      isLoadingMetadata: false,
    });

    render(<MetadataPanel resourceId="test-resource" />);

    expect(screen.getByText('Test Paper')).toBeInTheDocument();
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    expect(screen.getByText('This is a test abstract')).toBeInTheDocument();
  });

  it('calculates completeness correctly', () => {
    (useScholarlyAssets as any).mockReturnValue({
      metadata: mockMetadata,
      isLoadingMetadata: false,
    });

    render(<MetadataPanel resourceId="test-resource" />);

    // Should show 100% completeness
    expect(screen.getByText('100%')).toBeInTheDocument();
  });

  it('shows missing field indicators', () => {
    const incompleteMetadata = {
      ...mockMetadata,
      title: '',
      authors: [],
    };

    (useScholarlyAssets as any).mockReturnValue({
      metadata: incompleteMetadata,
      isLoadingMetadata: false,
    });

    render(<MetadataPanel resourceId="test-resource" />);

    // Should show "Not provided" for missing fields
    const notProvided = screen.getAllByText('Not provided');
    expect(notProvided.length).toBeGreaterThan(0);
  });

  it('enables edit mode when edit button clicked', () => {
    (useScholarlyAssets as any).mockReturnValue({
      metadata: mockMetadata,
      isLoadingMetadata: false,
    });

    const mockSave = vi.fn();
    render(<MetadataPanel resourceId="test-resource" onSaveMetadata={mockSave} />);

    const editButton = screen.getByTitle('Edit metadata');
    fireEvent.click(editButton);

    // Should show save and cancel buttons (check by icon presence)
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBeGreaterThan(1); // Should have cancel and save buttons
  });

  it('disables edit button when no save callback', () => {
    (useScholarlyAssets as any).mockReturnValue({
      metadata: mockMetadata,
      isLoadingMetadata: false,
    });

    render(<MetadataPanel resourceId="test-resource" />);

    const editButton = screen.getByTitle('Edit metadata');
    expect(editButton).toBeDisabled();
  });

  it('allows editing title', () => {
    (useScholarlyAssets as any).mockReturnValue({
      metadata: mockMetadata,
      isLoadingMetadata: false,
    });

    const mockSave = vi.fn();
    render(<MetadataPanel resourceId="test-resource" onSaveMetadata={mockSave} />);

    const editButton = screen.getByTitle('Edit metadata');
    fireEvent.click(editButton);

    const titleInput = screen.getByDisplayValue('Test Paper');
    expect(titleInput).toBeInTheDocument();
    
    fireEvent.change(titleInput, { target: { value: 'Updated Title' } });
    expect(titleInput).toHaveValue('Updated Title');
  });

  it('cancels editing when cancel button clicked', () => {
    (useScholarlyAssets as any).mockReturnValue({
      metadata: mockMetadata,
      isLoadingMetadata: false,
    });

    const mockSave = vi.fn();
    render(<MetadataPanel resourceId="test-resource" onSaveMetadata={mockSave} />);

    const editButton = screen.getByTitle('Edit metadata');
    fireEvent.click(editButton);

    // Find cancel button (X icon)
    const buttons = screen.getAllByRole('button');
    const cancelButton = buttons.find(btn => btn.querySelector('svg'));
    if (cancelButton) {
      fireEvent.click(cancelButton);
    }

    // Should show edit button again
    expect(screen.getByTitle('Edit metadata')).toBeInTheDocument();
  });

  it('renders keywords as badges', () => {
    (useScholarlyAssets as any).mockReturnValue({
      metadata: mockMetadata,
      isLoadingMetadata: false,
    });

    render(<MetadataPanel resourceId="test-resource" />);

    expect(screen.getByText('test')).toBeInTheDocument();
    expect(screen.getByText('paper')).toBeInTheDocument();
  });

  it('renders authors as badges', () => {
    (useScholarlyAssets as any).mockReturnValue({
      metadata: mockMetadata,
      isLoadingMetadata: false,
    });

    render(<MetadataPanel resourceId="test-resource" />);

    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    (useScholarlyAssets as any).mockReturnValue({
      metadata: mockMetadata,
      isLoadingMetadata: false,
    });

    const { container } = render(
      <MetadataPanel resourceId="test-resource" className="custom-class" />
    );

    const panel = container.querySelector('.metadata-panel');
    expect(panel).toHaveClass('custom-class');
  });
});
