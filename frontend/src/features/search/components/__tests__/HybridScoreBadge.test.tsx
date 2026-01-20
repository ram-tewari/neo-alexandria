/**
 * HybridScoreBadge Component Tests
 */

import { render, screen } from '@testing-library/react';
import { HybridScoreBadge } from '../HybridScoreBadge';
import { describe, it, expect } from 'vitest';

describe('HybridScoreBadge', () => {
  it('should display score as percentage', () => {
    render(<HybridScoreBadge score={0.85} />);
    expect(screen.getByText('85%')).toBeInTheDocument();
  });

  it('should round score to nearest integer', () => {
    render(<HybridScoreBadge score={0.847} />);
    expect(screen.getByText('85%')).toBeInTheDocument();
  });

  it('should apply green color for high scores (>80%)', () => {
    const { container } = render(<HybridScoreBadge score={0.85} />);
    const badge = container.querySelector('.bg-green-100');
    expect(badge).toBeInTheDocument();
  });

  it('should apply yellow color for medium scores (60-80%)', () => {
    const { container } = render(<HybridScoreBadge score={0.7} />);
    const badge = container.querySelector('.bg-yellow-100');
    expect(badge).toBeInTheDocument();
  });

  it('should apply gray color for low scores (<60%)', () => {
    const { container } = render(<HybridScoreBadge score={0.5} />);
    const badge = container.querySelector('.bg-gray-100');
    expect(badge).toBeInTheDocument();
  });

  it('should render without breakdown', () => {
    render(<HybridScoreBadge score={0.75} />);
    expect(screen.getByText('75%')).toBeInTheDocument();
  });

  it('should show breakdown on hover when provided', () => {
    const breakdown = {
      semantic_score: 0.8,
      keyword_score: 0.6,
    };
    
    const { container } = render(<HybridScoreBadge score={0.75} breakdown={breakdown} />);
    
    // Hover tooltip should exist in DOM
    expect(container.querySelector('.group')).toBeInTheDocument();
    expect(screen.getByText('Score Breakdown')).toBeInTheDocument();
  });

  it('should display semantic score in breakdown', () => {
    const breakdown = {
      semantic_score: 0.85,
      keyword_score: 0.6,
    };
    
    render(<HybridScoreBadge score={0.75} breakdown={breakdown} />);
    expect(screen.getByText('85%')).toBeInTheDocument();
  });

  it('should display keyword score in breakdown', () => {
    const breakdown = {
      semantic_score: 0.8,
      keyword_score: 0.65,
    };
    
    render(<HybridScoreBadge score={0.75} breakdown={breakdown} />);
    expect(screen.getByText('65%')).toBeInTheDocument();
  });

  it('should handle missing breakdown values', () => {
    const breakdown = {
      semantic_score: 0.8,
    };
    
    render(<HybridScoreBadge score={0.75} breakdown={breakdown} />);
    expect(screen.getByText('Score Breakdown')).toBeInTheDocument();
  });

  it('should display composite score in breakdown', () => {
    const breakdown = {
      semantic_score: 0.8,
      keyword_score: 0.6,
    };
    
    render(<HybridScoreBadge score={0.75} breakdown={breakdown} />);
    expect(screen.getByText('Composite Score')).toBeInTheDocument();
  });
});
