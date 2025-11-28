import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ResourceCard } from '../ResourceCard';
import { Resource } from '@/types/resource';

const mockResource: Resource = {
  id: '1',
  title: 'Test Resource',
  authors: ['John Doe', 'Jane Smith'],
  abstract: 'This is a test abstract for the resource.',
  type: 'pdf',
  qualityScore: 85,
  qualityDimensions: [],
  classification: ['Machine Learning', 'AI'],
  tags: ['test'],
  metadata: {},
  createdAt: new Date('2024-01-01'),
  updatedAt: new Date('2024-01-01'),
};

describe('ResourceCard', () => {
  it('renders resource information correctly', () => {
    render(<ResourceCard resource={mockResource} />);

    expect(screen.getByText('Test Resource')).toBeInTheDocument();
    expect(screen.getByText(/John Doe/)).toBeInTheDocument();
    expect(screen.getByText(/This is a test abstract/)).toBeInTheDocument();
  });

  it('displays quality score badge', () => {
    render(<ResourceCard resource={mockResource} />);

    expect(screen.getByText('85')).toBeInTheDocument();
  });

  it('displays classification tags', () => {
    render(<ResourceCard resource={mockResource} />);

    expect(screen.getByText('Machine Learning')).toBeInTheDocument();
    expect(screen.getByText('AI')).toBeInTheDocument();
  });

  it('calls onClick when card is clicked', () => {
    const onClick = vi.fn();
    render(<ResourceCard resource={mockResource} onClick={onClick} />);

    const card = screen.getByRole('article');
    fireEvent.click(card);

    expect(onClick).toHaveBeenCalledWith('1');
  });

  it('renders checkbox when onSelect is provided', () => {
    const onSelect = vi.fn();
    render(<ResourceCard resource={mockResource} onSelect={onSelect} />);

    const checkbox = screen.getByRole('checkbox');
    expect(checkbox).toBeInTheDocument();
  });

  it('calls onSelect when checkbox is clicked', () => {
    const onSelect = vi.fn();
    render(<ResourceCard resource={mockResource} onSelect={onSelect} />);

    const checkbox = screen.getByRole('checkbox');
    fireEvent.click(checkbox);

    expect(onSelect).toHaveBeenCalledWith('1');
  });

  it('renders in list view', () => {
    const { container } = render(
      <ResourceCard resource={mockResource} view="list" />
    );

    expect(container.querySelector('.flex.gap-4')).toBeInTheDocument();
  });

  it('renders in compact view', () => {
    const { container } = render(
      <ResourceCard resource={mockResource} view="compact" />
    );

    expect(screen.getByText('Test Resource')).toBeInTheDocument();
    expect(screen.getByText(/John Doe \+1/)).toBeInTheDocument();
  });

  it('shows selected state', () => {
    const { container } = render(
      <ResourceCard resource={mockResource} isSelected={true} />
    );

    const card = container.firstChild as HTMLElement;
    expect(card.className).toContain('border-primary-500');
  });
});
