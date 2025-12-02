import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { GraphTab } from './GraphTab';
import { AnnotationsTab } from './AnnotationsTab';

describe('Placeholder Tabs', () => {
  describe('GraphTab', () => {
    it('renders placeholder content', () => {
      render(<GraphTab resourceId="test-id" />);
      
      expect(screen.getByText('Knowledge Graph')).toBeInTheDocument();
      expect(screen.getByText(/knowledge graph visualization/i)).toBeInTheDocument();
      expect(screen.getByText('Coming soon in a future update')).toBeInTheDocument();
    });

    it('displays feature list', () => {
      render(<GraphTab resourceId="test-id" />);
      
      expect(screen.getByText('Interactive graph visualization')).toBeInTheDocument();
      expect(screen.getByText('Citation network analysis')).toBeInTheDocument();
      expect(screen.getByText('Semantic relationship mapping')).toBeInTheDocument();
    });

    it('has proper ARIA attributes', () => {
      render(<GraphTab resourceId="test-id" />);
      
      const tabPanel = screen.getByRole('tabpanel');
      expect(tabPanel).toHaveAttribute('id', 'panel-graph');
      expect(tabPanel).toHaveAttribute('aria-labelledby', 'tab-graph');
    });
  });

  describe('AnnotationsTab', () => {
    it('renders placeholder content', () => {
      render(<AnnotationsTab resourceId="test-id" />);
      
      expect(screen.getByText('Annotations & Notes')).toBeInTheDocument();
      expect(screen.getByText(/Organize your thoughts and insights/i)).toBeInTheDocument();
      expect(screen.getByText('Coming soon in a future update')).toBeInTheDocument();
    });

    it('displays feature list', () => {
      render(<AnnotationsTab resourceId="test-id" />);
      
      expect(screen.getByText('Highlight important passages')).toBeInTheDocument();
      expect(screen.getByText('Add personal notes and comments')).toBeInTheDocument();
      expect(screen.getByText('Search and filter annotations')).toBeInTheDocument();
    });

    it('has proper ARIA attributes', () => {
      render(<AnnotationsTab resourceId="test-id" />);
      
      const tabPanel = screen.getByRole('tabpanel');
      expect(tabPanel).toHaveAttribute('id', 'panel-annotations');
      expect(tabPanel).toHaveAttribute('aria-labelledby', 'tab-annotations');
    });
  });
});
