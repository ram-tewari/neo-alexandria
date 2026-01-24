/**
 * Tests for Loading Skeleton Components
 * 
 * Validates that loading skeletons:
 * - Render correctly
 * - Have proper accessibility attributes
 * - Show appropriate loading messages
 * - Display correct number of skeleton elements
 * 
 * Requirements: 5.5 - Loading states for better UX
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import {
  MonacoEditorSkeleton,
  AnnotationPanelSkeleton,
  ChunkMetadataSkeleton,
  QualityBadgeLoadingIndicator,
  InlineLoadingSpinner,
  ApiOperationLoadingOverlay,
  FileTreeSkeleton,
  CardLoadingSkeleton,
  ButtonLoadingSpinner,
} from '../components/LoadingSkeletons';

describe('LoadingSkeletons', () => {
  describe('MonacoEditorSkeleton', () => {
    it('should render with loading message', () => {
      render(<MonacoEditorSkeleton />);
      
      expect(screen.getByText('Loading code editor...')).toBeInTheDocument();
      expect(screen.getByLabelText('Loading code editor')).toBeInTheDocument();
    });

    it('should have proper accessibility attributes', () => {
      render(<MonacoEditorSkeleton />);
      
      const container = screen.getByRole('status');
      expect(container).toHaveAttribute('aria-live', 'polite');
      expect(container).toHaveAttribute('aria-label', 'Loading code editor');
    });

    it('should render skeleton lines', () => {
      const { container } = render(<MonacoEditorSkeleton />);
      
      // Should have multiple skeleton elements for code lines
      const skeletons = container.querySelectorAll('[class*="animate-pulse"]');
      expect(skeletons.length).toBeGreaterThan(10);
    });

    it('should show loading spinner', () => {
      const { container } = render(<MonacoEditorSkeleton />);
      
      // Check for Loader2 icon (animate-spin class)
      const spinner = container.querySelector('[class*="animate-spin"]');
      expect(spinner).toBeInTheDocument();
    });
  });

  describe('AnnotationPanelSkeleton', () => {
    it('should render with loading message', () => {
      render(<AnnotationPanelSkeleton />);
      
      expect(screen.getByLabelText('Loading annotations')).toBeInTheDocument();
    });

    it('should have proper accessibility attributes', () => {
      render(<AnnotationPanelSkeleton />);
      
      const container = screen.getByRole('status');
      expect(container).toHaveAttribute('aria-live', 'polite');
    });

    it('should render multiple annotation card skeletons', () => {
      const { container } = render(<AnnotationPanelSkeleton />);
      
      // Should have skeleton elements for annotation cards
      const skeletons = container.querySelectorAll('[class*="animate-pulse"]');
      expect(skeletons.length).toBeGreaterThan(5);
    });
  });

  describe('ChunkMetadataSkeleton', () => {
    it('should render with loading message', () => {
      render(<ChunkMetadataSkeleton />);
      
      expect(screen.getByLabelText('Loading chunk metadata')).toBeInTheDocument();
    });

    it('should have proper accessibility attributes', () => {
      render(<ChunkMetadataSkeleton />);
      
      const container = screen.getByRole('status');
      expect(container).toHaveAttribute('aria-live', 'polite');
    });

    it('should render metadata field skeletons', () => {
      const { container } = render(<ChunkMetadataSkeleton />);
      
      const skeletons = container.querySelectorAll('[class*="animate-pulse"]');
      expect(skeletons.length).toBeGreaterThan(3);
    });
  });

  describe('QualityBadgeLoadingIndicator', () => {
    it('should render with loading message', () => {
      render(<QualityBadgeLoadingIndicator />);
      
      expect(screen.getByText('Loading quality data...')).toBeInTheDocument();
    });

    it('should have proper accessibility attributes', () => {
      render(<QualityBadgeLoadingIndicator />);
      
      const container = screen.getByRole('status');
      expect(container).toHaveAttribute('aria-live', 'polite');
      expect(container).toHaveAttribute('aria-label', 'Loading quality data');
    });

    it('should show loading spinner', () => {
      const { container } = render(<QualityBadgeLoadingIndicator />);
      
      const spinner = container.querySelector('[class*="animate-spin"]');
      expect(spinner).toBeInTheDocument();
    });
  });

  describe('InlineLoadingSpinner', () => {
    it('should render with default text', () => {
      render(<InlineLoadingSpinner />);
      
      // Use getAllByText since text appears twice (visible + sr-only)
      const elements = screen.getAllByText('Loading...');
      expect(elements.length).toBeGreaterThan(0);
    });

    it('should render with custom text', () => {
      render(<InlineLoadingSpinner text="Fetching data..." />);
      
      // Use getAllByText since text appears twice (visible + sr-only)
      const elements = screen.getAllByText('Fetching data...');
      expect(elements.length).toBeGreaterThan(0);
    });

    it('should have proper accessibility attributes', () => {
      render(<InlineLoadingSpinner text="Custom loading" />);
      
      const container = screen.getByRole('status');
      expect(container).toHaveAttribute('aria-live', 'polite');
      expect(container).toHaveAttribute('aria-label', 'Custom loading');
    });

    it('should render different sizes', () => {
      const { container: smallContainer } = render(<InlineLoadingSpinner size="sm" />);
      const { container: largeContainer } = render(<InlineLoadingSpinner size="lg" />);
      
      const smallSpinner = smallContainer.querySelector('[class*="animate-spin"]');
      const largeSpinner = largeContainer.querySelector('[class*="animate-spin"]');
      
      expect(smallSpinner).toHaveClass('h-4');
      expect(largeSpinner).toHaveClass('h-6');
    });
  });

  describe('ApiOperationLoadingOverlay', () => {
    it('should render with default operation text', () => {
      render(<ApiOperationLoadingOverlay />);
      
      expect(screen.getByText('Loading...')).toBeInTheDocument();
      expect(screen.getByText('Please wait')).toBeInTheDocument();
    });

    it('should render with custom operation text', () => {
      render(<ApiOperationLoadingOverlay operation="Saving annotation" />);
      
      expect(screen.getByText('Saving annotation...')).toBeInTheDocument();
    });

    it('should have proper accessibility attributes', () => {
      render(<ApiOperationLoadingOverlay operation="Fetching" />);
      
      const container = screen.getByRole('status');
      expect(container).toHaveAttribute('aria-live', 'polite');
      expect(container).toHaveAttribute('aria-label', 'Fetching...');
    });

    it('should show loading spinner', () => {
      const { container } = render(<ApiOperationLoadingOverlay />);
      
      const spinner = container.querySelector('[class*="animate-spin"]');
      expect(spinner).toBeInTheDocument();
    });

    it('should apply transparent background when specified', () => {
      const { container } = render(<ApiOperationLoadingOverlay transparent />);
      
      const overlay = container.querySelector('[class*="bg-background"]');
      expect(overlay).toHaveClass('bg-background/50');
    });
  });

  describe('FileTreeSkeleton', () => {
    it('should render with loading message', () => {
      render(<FileTreeSkeleton />);
      
      expect(screen.getByLabelText('Loading file tree')).toBeInTheDocument();
    });

    it('should have proper accessibility attributes', () => {
      render(<FileTreeSkeleton />);
      
      const container = screen.getByRole('status');
      expect(container).toHaveAttribute('aria-live', 'polite');
    });

    it('should render multiple file/folder skeletons', () => {
      const { container } = render(<FileTreeSkeleton />);
      
      const skeletons = container.querySelectorAll('[class*="animate-pulse"]');
      expect(skeletons.length).toBeGreaterThan(5);
    });
  });

  describe('CardLoadingSkeleton', () => {
    it('should render with default number of lines', () => {
      const { container } = render(<CardLoadingSkeleton />);
      
      const skeletons = container.querySelectorAll('[class*="animate-pulse"]');
      // Default is 3 lines + optional header
      expect(skeletons.length).toBeGreaterThanOrEqual(3);
    });

    it('should render custom number of lines', () => {
      const { container } = render(<CardLoadingSkeleton lines={5} />);
      
      const skeletons = container.querySelectorAll('[class*="animate-pulse"]');
      expect(skeletons.length).toBeGreaterThanOrEqual(5);
    });

    it('should show header when specified', () => {
      const { container } = render(<CardLoadingSkeleton showHeader />);
      
      const skeletons = container.querySelectorAll('[class*="animate-pulse"]');
      // Should have header skeleton + line skeletons
      expect(skeletons.length).toBeGreaterThan(3);
    });

    it('should hide header when specified', () => {
      const { container } = render(<CardLoadingSkeleton showHeader={false} lines={2} />);
      
      const skeletons = container.querySelectorAll('[class*="animate-pulse"]');
      // Should only have line skeletons, no header
      expect(skeletons.length).toBe(2);
    });

    it('should have proper accessibility attributes', () => {
      render(<CardLoadingSkeleton />);
      
      const container = screen.getByRole('status');
      expect(container).toHaveAttribute('aria-live', 'polite');
      expect(container).toHaveAttribute('aria-label', 'Loading content');
    });
  });

  describe('ButtonLoadingSpinner', () => {
    it('should render with default size', () => {
      const { container } = render(<ButtonLoadingSpinner />);
      
      const spinner = container.querySelector('[class*="animate-spin"]');
      expect(spinner).toBeInTheDocument();
      expect(spinner).toHaveClass('h-4');
    });

    it('should render different sizes', () => {
      const { container: xsContainer } = render(<ButtonLoadingSpinner size="xs" />);
      const { container: mdContainer } = render(<ButtonLoadingSpinner size="md" />);
      
      const xsSpinner = xsContainer.querySelector('[class*="animate-spin"]');
      const mdSpinner = mdContainer.querySelector('[class*="animate-spin"]');
      
      expect(xsSpinner).toHaveClass('h-3');
      expect(mdSpinner).toHaveClass('h-5');
    });

    it('should have aria-hidden attribute', () => {
      const { container } = render(<ButtonLoadingSpinner />);
      
      const spinner = container.querySelector('[class*="animate-spin"]');
      expect(spinner).toHaveAttribute('aria-hidden', 'true');
    });
  });
});
