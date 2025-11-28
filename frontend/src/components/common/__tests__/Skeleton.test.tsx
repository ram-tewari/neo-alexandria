import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { Skeleton, SkeletonCard, SkeletonList } from '../Skeleton';

describe('Skeleton', () => {
  it('renders with default props', () => {
    const { container } = render(<Skeleton />);
    expect(container.firstChild).toHaveClass('animate-pulse');
  });

  it('renders with different variants', () => {
    const { container: textContainer } = render(<Skeleton variant="text" />);
    expect(textContainer.firstChild).toHaveClass('rounded');

    const { container: circularContainer } = render(<Skeleton variant="circular" />);
    expect(circularContainer.firstChild).toHaveClass('rounded-full');

    const { container: cardContainer } = render(<Skeleton variant="card" />);
    expect(cardContainer.firstChild).toHaveClass('rounded-lg');
  });

  it('applies custom width and height', () => {
    const { container } = render(<Skeleton width={200} height={100} />);
    const element = container.firstChild as HTMLElement;
    expect(element.style.width).toBe('200px');
    expect(element.style.height).toBe('100px');
  });

  it('supports different animation types', () => {
    const { container: pulseContainer } = render(<Skeleton animation="pulse" />);
    expect(pulseContainer.firstChild).toHaveClass('animate-pulse');

    const { container: noneContainer } = render(<Skeleton animation="none" />);
    expect(noneContainer.firstChild).not.toHaveClass('animate-pulse');
  });
});

describe('SkeletonCard', () => {
  it('renders card skeleton structure', () => {
    const { container } = render(<SkeletonCard />);
    expect(container.querySelector('.bg-white')).toBeInTheDocument();
  });
});

describe('SkeletonList', () => {
  it('renders specified number of skeleton items', () => {
    const { container } = render(<SkeletonList count={3} />);
    const items = container.querySelectorAll('.bg-white');
    expect(items).toHaveLength(3);
  });

  it('renders default 5 items when count not specified', () => {
    const { container } = render(<SkeletonList />);
    const items = container.querySelectorAll('.bg-white');
    expect(items).toHaveLength(5);
  });
});
