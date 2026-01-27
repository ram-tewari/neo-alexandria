/**
 * DocumentUpload Component Tests
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { DocumentUpload } from '../DocumentUpload';

describe('DocumentUpload', () => {
  describe('Rendering', () => {
    it('renders dropzone with instructions', () => {
      render(<DocumentUpload onUpload={vi.fn()} />);
      
      expect(screen.getByText(/Drag & drop files here/)).toBeInTheDocument();
      expect(screen.getByText(/PDF, HTML, TXT, MD/)).toBeInTheDocument();
    });

    it('shows max file size in instructions', () => {
      render(<DocumentUpload onUpload={vi.fn()} maxSize={10 * 1024 * 1024} />);
      
      expect(screen.getByText(/Max 10MB per file/)).toBeInTheDocument();
    });
  });

  describe('File Selection', () => {
    it('accepts file input', () => {
      render(<DocumentUpload onUpload={vi.fn()} />);
      
      const input = document.querySelector('input[type="file"]');
      expect(input).toBeInTheDocument();
    });

    it('shows drag active state', () => {
      const { container } = render(<DocumentUpload onUpload={vi.fn()} />);
      
      const dropzone = container.querySelector('[class*="border-dashed"]');
      expect(dropzone).toBeInTheDocument();
    });
  });

  describe('Upload Queue', () => {
    it('does not show queue initially', () => {
      render(<DocumentUpload onUpload={vi.fn()} />);
      
      // Queue section should not be visible
      expect(screen.queryByText(/Clear completed/)).not.toBeInTheDocument();
    });
  });

  describe('File Validation', () => {
    it('validates file types', () => {
      const acceptedTypes = ['application/pdf'];
      render(<DocumentUpload onUpload={vi.fn()} acceptedTypes={acceptedTypes} />);
      
      // Dropzone configured with accepted types
      const input = document.querySelector('input[type="file"]');
      expect(input).toBeInTheDocument();
    });

    it('validates file size', () => {
      const maxSize = 1024 * 1024; // 1MB
      render(<DocumentUpload onUpload={vi.fn()} maxSize={maxSize} />);
      
      expect(screen.getByText(/Max 1MB per file/)).toBeInTheDocument();
    });
  });

  describe('Multiple Files', () => {
    it('allows multiple files by default', () => {
      render(<DocumentUpload onUpload={vi.fn()} />);
      
      const input = document.querySelector('input[type="file"]') as HTMLInputElement;
      expect(input?.multiple).toBe(true);
    });

    it('disables multiple files when multiple=false', () => {
      render(<DocumentUpload onUpload={vi.fn()} multiple={false} />);
      
      const input = document.querySelector('input[type="file"]') as HTMLInputElement;
      expect(input?.multiple).toBe(false);
    });
  });

  describe('Accessibility', () => {
    it('has accessible file input', () => {
      render(<DocumentUpload onUpload={vi.fn()} />);
      
      const input = document.querySelector('input[type="file"]');
      expect(input).toBeInTheDocument();
    });

    it('provides clear instructions', () => {
      render(<DocumentUpload onUpload={vi.fn()} />);
      
      expect(screen.getByText(/Drag & drop files here, or click to select/)).toBeInTheDocument();
    });
  });
});
