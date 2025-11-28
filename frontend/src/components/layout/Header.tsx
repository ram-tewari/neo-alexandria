/**
 * Header/Navbar Component
 * Sticky navigation header with collapse functionality
 * Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronUp, ChevronDown } from 'lucide-react';
import { ThemeToggle } from '../theme/ThemeToggle';
import { useTheme } from '../../contexts/ThemeContext';
import './Header.css';

export interface NavigationLink {
  label: string;
  href: string;
  icon?: React.ReactNode;
  active?: boolean;
}

export interface HeaderProps {
  links: NavigationLink[];
  logo?: React.ReactNode;
  className?: string;
}

export function Header({ links, logo, className = '' }: HeaderProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const { theme } = useTheme();

  // Detect scroll for sticky header styling
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const toggleCollapse = () => {
    setIsCollapsed(!isCollapsed);
  };

  return (
    <motion.header
      className={`header ${isScrolled ? 'header--scrolled' : ''} ${className}`}
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
    >
      <div className="header__container">
        {/* Logo */}
        {logo && <div className="header__logo">{logo}</div>}

        {/* Collapse Button */}
        <button
          onClick={toggleCollapse}
          className="header__collapse-btn"
          aria-label={isCollapsed ? 'Expand navigation' : 'Collapse navigation'}
          aria-expanded={!isCollapsed}
          type="button"
        >
          <motion.div
            animate={{ rotate: isCollapsed ? 180 : 0 }}
            transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
          >
            {isCollapsed ? (
              <ChevronDown size={20} aria-hidden="true" />
            ) : (
              <ChevronUp size={20} aria-hidden="true" />
            )}
          </motion.div>
        </button>

        {/* Navigation */}
        <AnimatePresence initial={false}>
          {!isCollapsed && (
            <motion.nav
              className="header__nav"
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
            >
              <ul className="header__nav-list">
                {links.map((link, index) => (
                  <li key={index} className="header__nav-item">
                    <a
                      href={link.href}
                      className={`header__nav-link ${link.active ? 'header__nav-link--active' : ''}`}
                      aria-current={link.active ? 'page' : undefined}
                    >
                      {link.icon && (
                        <span className="header__nav-icon">{link.icon}</span>
                      )}
                      <span className="header__nav-label">{link.label}</span>
                    </a>
                  </li>
                ))}
              </ul>
            </motion.nav>
          )}
        </AnimatePresence>

        {/* Theme Toggle */}
        <div className="header__theme-toggle">
          <ThemeToggle size="sm" />
        </div>
      </div>
    </motion.header>
  );
}
