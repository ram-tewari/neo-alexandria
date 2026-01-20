/**
 * Unit tests for StatusBadge component
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { StatusBadge } from './StatusBadge';
import { ResourceStatus } from '@/core/types/resource';

describe('StatusBadge', () => {
  describe('Status rendering', () => {
    it('should render pending status with yellow color', () => {
      render(<StatusBadge status={ResourceStatus.PENDING} />);

      const badge = screen.getByText('Pending').closest('[aria-label]');
      expect(badge).toBeInTheDocument();
      expect(badge).toHaveClass('bg-yellow-100');
      expect(badge).toHaveClass('text-yellow-800');
    });

    it('should render processing status with blue color', () => {
      render(<StatusBadge status={ResourceStatus.PROCESSING} />);

      const badge = screen.getByText('Processing').closest('[aria-label]');
      expect(badge).toBeInTheDocument();
      expect(badge).toHaveClass('bg-blue-100');
      expect(badge).toHaveClass('text-blue-800');
    });

    it('should render completed status with green color', () => {
      render(<StatusBadge status={ResourceStatus.COMPLETED} />);

      const badge = screen.getByText('Completed').closest('[aria-label]');
      expect(badge).toBeInTheDocument();
      expect(badge).toHaveClass('bg-green-100');
      expect(badge).toHaveClass('text-green-800');
    });

    it('should render failed status with red color', () => {
      render(<StatusBadge status={ResourceStatus.FAILED} />);

      const badge = screen.getByText('Failed').closest('[aria-label]');
      expect(badge).toBeInTheDocument();
      expect(badge).toHaveClass('bg-red-100');
      expect(badge).toHaveClass('text-red-800');
    });
  });

  describe('Icons', () => {
    it('should render Clock icon for pending status', () => {
      const { container } = render(<StatusBadge status={ResourceStatus.PENDING} />);

      // Check for icon by looking for svg element
      const icon = container.querySelector('svg');
      expect(icon).toBeInTheDocument();
      expect(icon).toHaveClass('h-3');
      expect(icon).toHaveClass('w-3');
    });

    it('should render Loader2 icon with spinning animation for processing status', () => {
      const { container } = render(<StatusBadge status={ResourceStatus.PROCESSING} />);

      const icon = container.querySelector('svg');
      expect(icon).toBeInTheDocument();
      expect(icon).toHaveClass('animate-spin');
    });

    it('should render CheckCircle2 icon for completed status', () => {
      const { container } = render(<StatusBadge status={ResourceStatus.COMPLETED} />);

      const icon = container.querySelector('svg');
      expect(icon).toBeInTheDocument();
      expect(icon).toHaveClass('h-3');
      expect(icon).toHaveClass('w-3');
    });

    it('should render XCircle icon for failed status', () => {
      const { container } = render(<StatusBadge status={ResourceStatus.FAILED} />);

      const icon = container.querySelector('svg');
      expect(icon).toBeInTheDocument();
      expect(icon).toHaveClass('h-3');
      expect(icon).toHaveClass('w-3');
    });
  });

  describe('Accessibility', () => {
    it('should have aria-label for pending status', () => {
      const { container } = render(<StatusBadge status={ResourceStatus.PENDING} />);

      const badge = container.querySelector('[aria-label]');
      expect(badge).toHaveAttribute('aria-label', 'Status: pending');
    });

    it('should have aria-label for processing status', () => {
      const { container } = render(<StatusBadge status={ResourceStatus.PROCESSING} />);

      const badge = container.querySelector('[aria-label]');
      expect(badge).toHaveAttribute('aria-label', 'Status: processing');
    });

    it('should have aria-label for completed status', () => {
      const { container } = render(<StatusBadge status={ResourceStatus.COMPLETED} />);

      const badge = container.querySelector('[aria-label]');
      expect(badge).toHaveAttribute('aria-label', 'Status: completed');
    });

    it('should have aria-label for failed status', () => {
      const { container } = render(<StatusBadge status={ResourceStatus.FAILED} />);

      const badge = container.querySelector('[aria-label]');
      expect(badge).toHaveAttribute('aria-label', 'Status: failed');
    });
  });

  describe('Custom className', () => {
    it('should accept and apply custom className', () => {
      const { container } = render(
        <StatusBadge status={ResourceStatus.COMPLETED} className="custom-class" />
      );

      const badge = container.querySelector('.custom-class');
      expect(badge).toBeInTheDocument();
      expect(badge).toHaveClass('bg-green-100'); // Should still have status class
    });
  });

  describe('Animation', () => {
    it('should have spinning animation only for processing status', () => {
      const { container: processingContainer } = render(
        <StatusBadge status={ResourceStatus.PROCESSING} />
      );
      const processingIcon = processingContainer.querySelector('svg');
      expect(processingIcon).toHaveClass('animate-spin');

      const { container: pendingContainer } = render(
        <StatusBadge status={ResourceStatus.PENDING} />
      );
      const pendingIcon = pendingContainer.querySelector('svg');
      expect(pendingIcon).not.toHaveClass('animate-spin');

      const { container: completedContainer } = render(
        <StatusBadge status={ResourceStatus.COMPLETED} />
      );
      const completedIcon = completedContainer.querySelector('svg');
      expect(completedIcon).not.toHaveClass('animate-spin');

      const { container: failedContainer } = render(
        <StatusBadge status={ResourceStatus.FAILED} />
      );
      const failedIcon = failedContainer.querySelector('svg');
      expect(failedIcon).not.toHaveClass('animate-spin');
    });
  });
});
