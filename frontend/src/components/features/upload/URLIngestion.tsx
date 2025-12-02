/**
 * URLIngestion Component
 * Form for adding resources via URL with validation
 */

import React, { useState, useCallback } from 'react';
import { Button } from '../../ui/Button/Button';
import { Input } from '../../ui/Input/Input';
import './URLIngestion.css';

interface URLIngestionProps {
  onURLSubmit: (url: string) => void;
  disabled?: boolean;
}

/**
 * Validate URL format
 */
const validateURL = (url: string): { valid: boolean; error?: string } => {
  // Check if empty
  if (!url.trim()) {
    return { valid: false, error: 'URL is required' };
  }

  // Basic URL format validation
  try {
    const urlObj = new URL(url);
    
    // Check protocol
    if (!['http:', 'https:'].includes(urlObj.protocol)) {
      return { valid: false, error: 'URL must use HTTP or HTTPS protocol' };
    }

    // Check for valid hostname
    if (!urlObj.hostname) {
      return { valid: false, error: 'Invalid URL format' };
    }

    return { valid: true };
  } catch {
    return { valid: false, error: 'Invalid URL format' };
  }
};

/**
 * Check if URL matches common scholarly patterns
 */
const getURLType = (url: string): string | null => {
  const lowerURL = url.toLowerCase();
  
  if (lowerURL.includes('doi.org/') || lowerURL.includes('dx.doi.org/')) {
    return 'DOI';
  }
  if (lowerURL.includes('arxiv.org/')) {
    return 'arXiv';
  }
  if (lowerURL.endsWith('.pdf')) {
    return 'PDF';
  }
  if (lowerURL.includes('scholar.google.com')) {
    return 'Google Scholar';
  }
  if (lowerURL.includes('pubmed.ncbi.nlm.nih.gov')) {
    return 'PubMed';
  }
  
  return null;
};

export const URLIngestion: React.FC<URLIngestionProps> = ({
  onURLSubmit,
  disabled = false,
}) => {
  const [url, setURL] = useState('');
  const [error, setError] = useState<string | undefined>();
  const [isSubmitting, setIsSubmitting] = useState(false);

  /**
   * Handle URL input change
   */
  const handleURLChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const newURL = e.target.value;
    setURL(newURL);
    
    // Clear error when user starts typing
    if (error) {
      setError(undefined);
    }
  }, [error]);

  /**
   * Handle form submission
   */
  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (disabled || isSubmitting) return;

    // Validate URL
    const validation = validateURL(url);
    if (!validation.valid) {
      setError(validation.error);
      return;
    }

    // Submit URL
    setIsSubmitting(true);
    try {
      onURLSubmit(url);
      
      // Clear form on success
      setURL('');
      setError(undefined);
    } catch (err) {
      setError('Failed to submit URL');
    } finally {
      setIsSubmitting(false);
    }
  }, [url, disabled, isSubmitting, onURLSubmit]);

  /**
   * Handle paste event - auto-detect and clean URL
   */
  const handlePaste = useCallback((e: React.ClipboardEvent<HTMLInputElement>) => {
    const pastedText = e.clipboardData.getData('text');
    const trimmedURL = pastedText.trim();
    
    // Auto-validate on paste
    if (trimmedURL) {
      const validation = validateURL(trimmedURL);
      if (!validation.valid) {
        setError(validation.error);
      }
    }
  }, []);

  const urlType = url ? getURLType(url) : null;

  return (
    <div className="url-ingestion">
      <form onSubmit={handleSubmit} className="url-ingestion__form">
        <div className="url-ingestion__input-group">
          <Input
            type="url"
            value={url}
            onChange={handleURLChange}
            onPaste={handlePaste}
            placeholder="https://example.com/paper.pdf or DOI link"
            disabled={disabled || isSubmitting}
            error={error}
            className="url-ingestion__input"
            aria-label="Resource URL"
            aria-describedby={error ? 'url-error' : urlType ? 'url-type' : undefined}
          />
          
          <Button
            type="submit"
            variant="primary"
            size="md"
            disabled={disabled || isSubmitting || !url.trim()}
            className="url-ingestion__submit"
          >
            {isSubmitting ? 'Adding...' : 'Add URL'}
          </Button>
        </div>

        {/* Error message */}
        {error && (
          <div id="url-error" className="url-ingestion__error" role="alert">
            {error}
          </div>
        )}

        {/* URL type indicator */}
        {!error && urlType && (
          <div id="url-type" className="url-ingestion__hint">
            Detected: {urlType} link
          </div>
        )}
      </form>

      {/* Help text */}
      <div className="url-ingestion__help">
        <p className="url-ingestion__help-text">
          Supported URL types:
        </p>
        <ul className="url-ingestion__help-list">
          <li>Direct PDF links</li>
          <li>DOI links (doi.org)</li>
          <li>arXiv papers</li>
          <li>PubMed articles</li>
          <li>Google Scholar links</li>
        </ul>
      </div>
    </div>
  );
};

export default URLIngestion;
