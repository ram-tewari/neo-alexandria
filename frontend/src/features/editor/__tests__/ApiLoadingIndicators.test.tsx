/**
 * Tests for API Loading Indicators
 * 
 * Validates that API loading indicators:
 * - Render correctly
 * - Show appropriate messages
 * - Have proper accessibility attributes
 * - Display loading spinners
 * 
 * Requirements: 5.5 - Loading states for API operations
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import {
  AnnotationsLoadingIndicator,
  ChunksLoadingIndicator,
  QualityLoadingIndicator,
  CombinedLoadingIndicator,
  InlineLoadingBadge,
  FloatingLoadingIndicator,
} from '../components/ApiLoadingIndicators';

describe('ApiLoadingIndicators', () => {
  describe('AnnotationsLoadingIndicator', () => {
    it('should render with loading message', () => {
      render(<AnnotationsLoadingIndicator />);
      
      expect(screen.getByText('Loading annotations...')).toBeInTheDocument();
    });

    it('should show loading spinner', () => {
      const { container } = render(<AnnotationsLoadingIndicator />);
      
      const spinner = container.querySelector('[class*="animate-spin"]');
      expect(spinner).toBeInTheDocument();
    });

    it('should have proper styling', () => {
      const { container } = render(<AnnotationsLoadingIndicator />);
      
      const alert = container.querySelector('[class*="border-blue"]');
      expect(alert).toBeInTheDocument();
    });
  });

  describe('ChunksLoadingIndicator', () => {
    it('should render with loading message', () => {
      render(<ChunksLoadingIndicator />);
      
      expect(screen.getByText('Loading semantic chunks...')).toBeInTheDocument();
    });

    it('should show loading spinner', () => {
      const { container } = render(<ChunksLoadingIndicator />);
      
      const spinner = container.querySelector('[class*="animate-spin"]');
      expect(spinner).toBeInTheDocument();
    });

    it('should have proper styling', () => {
      const { container } = render(<ChunksLoadingIndicator />);
      
      const alert = container.querySelector('[class*="border-purple"]');
      expect(alert).toBeInTheDocument();
    });
  });

  describe('QualityLoadingIndicator', () => {
    it('should render with loading message', () => {
      render(<QualityLoadingIndicator />);
      
      expect(screen.getByText('Loading quality data...')).toBeInTheDocument();
    });

    it('should show loading spinner', () => {
      const { container } = render(<QualityLoadingIndicator />);
      
      const spinner = container.querySelector('[class*="animate-spin"]');
      expect(spinner).toBeInTheDocument();
    });

    it('should have proper styling', () => {
      const { container } = render(<QualityLoadingIndicator />);
      
      const alert = container.querySelector('[class*="border-green"]');
      expect(alert).toBeInTheDocument();
    });
  });

  describe('CombinedLoadingIndicator', () => {
    it('should render single operation', () => {
      render(<CombinedLoadingIndicator operations={['annotations']} />);
      
      expect(screen.getByText('Loading annotations...')).toBeInTheDocument();
    });

    it('should render multiple operations', () => {
      render(<CombinedLoadingIndicator operations={['annotations', 'chunks']} />);
      
      expect(screen.getByText(/Loading annotations, semantic chunks\.\.\./)).toBeInTheDocument();
    });

    it('should render all operations', () => {
      render(<CombinedLoadingIndicator operations={['annotations', 'chunks', 'quality']} />);
      
      expect(screen.getByText(/Loading annotations, semantic chunks, quality data\.\.\./)).toBeInTheDocument();
    });

    it('should show loading spinner', () => {
      const { container } = render(<CombinedLoadingIndicator operations={['annotations']} />);
      
      const spinner = container.querySelector('[class*="animate-spin"]');
      expect(spinner).toBeInTheDocument();
    });
  });

  describe('InlineLoadingBadge', () => {
    it('should render with default text', () => {
      render(<InlineLoadingBadge />);
      
      expect(screen.getByText('Loading...')).toBeInTheDocument();
    });

    it('should render with custom text', () => {
      render(<InlineLoadingBadge text="Fetching..." />);
      
      expect(screen.getByText('Fetching...')).toBeInTheDocument();
    });

    it('should have proper accessibility attributes', () => {
      render(<InlineLoadingBadge text="Custom loading" />);
      
      const container = screen.getByRole('status');
      expect(container).toHaveAttribute('aria-live', 'polite');
      expect(container).toHaveAttribute('aria-label', 'Custom loading');
    });

    it('should render default variant', () => {
      const { container } = render(<InlineLoadingBadge />);
      
      const spinner = container.querySelector('[class*="animate-spin"]');
      expect(spinner).toHaveClass('h-4');
    });

    it('should render small variant', () => {
      const { container } = render(<InlineLoadingBadge variant="small" />);
      
      const spinner = container.querySelector('[class*="animate-spin"]');
      expect(spinner).toHaveClass('h-3');
    });

    it('should show loading spinner', () => {
      const { container } = render(<InlineLoadingBadge />);
      
      const spinner = container.querySelector('[class*="animate-spin"]');
      expect(spinner).toBeInTheDocument();
    });
  });

  describe('FloatingLoadingIndicator', () => {
    it('should not render when no operations', () => {
      const { container } = render(<FloatingLoadingIndicator operations={[]} />);
      
      expect(container.firstChild).toBeNull();
    });

    it('should render single operation', () => {
      render(
        <FloatingLoadingIndicator 
          operations={[{ name: 'annotations', label: 'Loading annotations' }]} 
        />
      );
      
      expect(screen.getByText('Loading annotations')).toBeInTheDocument();
    });

    it('should render multiple operations', () => {
      render(
        <FloatingLoadingIndicator 
          operations={[
            { name: 'annotations', label: 'Loading annotations' },
            { name: 'chunks', label: 'Loading chunks' },
          ]} 
        />
      );
      
      expect(screen.getByText('Loading annotations')).toBeInTheDocument();
      expect(screen.getByText('Loading chunks')).toBeInTheDocument();
    });

    it('should have proper accessibility attributes', () => {
      render(
        <FloatingLoadingIndicator 
          operations={[{ name: 'test', label: 'Test operation' }]} 
        />
      );
      
      const container = screen.getByRole('status');
      expect(container).toHaveAttribute('aria-live', 'polite');
      expect(container).toHaveAttribute('aria-label', 'Loading operations in progress');
    });

    it('should show loading spinners for each operation', () => {
      const { container } = render(
        <FloatingLoadingIndicator 
          operations={[
            { name: 'op1', label: 'Operation 1' },
            { name: 'op2', label: 'Operation 2' },
          ]} 
        />
      );
      
      const spinners = container.querySelectorAll('[class*="animate-spin"]');
      expect(spinners.length).toBe(2);
    });

    it('should be positioned fixed at bottom-right', () => {
      const { container } = render(
        <FloatingLoadingIndicator 
          operations={[{ name: 'test', label: 'Test' }]} 
        />
      );
      
      const floatingDiv = container.querySelector('[class*="fixed"]');
      expect(floatingDiv).toHaveClass('bottom-4');
      expect(floatingDiv).toHaveClass('right-4');
    });
  });
});
