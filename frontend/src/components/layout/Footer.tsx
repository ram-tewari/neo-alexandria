/**
 * Footer Component
 * Minimalist footer with themed links
 * Requirements: 9.1, 9.2, 9.3, 9.4, 9.5
 */

import React from 'react';
import { motion } from 'framer-motion';
import { useTheme } from '../../contexts/ThemeContext';
import './Footer.css';

export interface FooterLink {
  label: string;
  href: string;
  external?: boolean;
}

export interface FooterProps {
  links?: FooterLink[];
  copyright?: string;
  className?: string;
}

/**
 * Footer Component
 * Features:
 * - Minimalist design
 * - Themed interactive elements
 * - Smooth color transitions
 * - Responsive layout
 */
export function Footer({
  links = [],
  copyright = `© ${new Date().getFullYear()} Neo Alexandria. All rights reserved.`,
  className = '',
}: FooterProps) {
  const { theme } = useTheme();

  return (
    <footer className={`footer ${className}`} data-theme={theme}>
      <div className="footer__content">
        <p className="footer__copyright">
          {copyright}
        </p>
      </div>
    </footer>
  );
}
