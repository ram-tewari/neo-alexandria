/**
 * SkipToContent component
 * Provides keyboard users a way to skip navigation and jump to main content
 */

import React from 'react';

/**
 * Skip to content link for accessibility
 */
export const SkipToContent: React.FC = () => {
  return (
    <a
      href="#main-content"
      className="skip-to-content"
      style={{
        position: 'absolute',
        top: '-40px',
        left: 0,
        background: 'var(--background)',
        color: 'var(--text-primary)',
        padding: '8px 16px',
        zIndex: 100,
        textDecoration: 'none',
        borderRadius: '0 0 4px 0',
        border: '2px solid var(--primary)',
        fontWeight: 500,
      }}
      onFocus={(e) => {
        e.currentTarget.style.top = '0';
      }}
      onBlur={(e) => {
        e.currentTarget.style.top = '-40px';
      }}
    >
      Skip to main content
    </a>
  );
};
