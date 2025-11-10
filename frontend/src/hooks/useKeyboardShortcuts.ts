// Neo Alexandria 2.0 Frontend - Keyboard Shortcuts Hook
// Custom hook for managing keyboard shortcuts and navigation

import { useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

interface KeyboardShortcut {
  key: string;
  ctrl?: boolean;
  alt?: boolean;
  shift?: boolean;
  meta?: boolean;
  action: () => void;
  description: string;
}

/**
 * Hook for registering keyboard shortcuts
 */
export function useKeyboardShortcut(
  key: string,
  callback: () => void,
  options: {
    ctrl?: boolean;
    alt?: boolean;
    shift?: boolean;
    meta?: boolean;
    enabled?: boolean;
  } = {}
) {
  const { ctrl = false, alt = false, shift = false, meta = false, enabled = true } = options;

  useEffect(() => {
    if (!enabled) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      // Check if the key matches
      if (event.key.toLowerCase() !== key.toLowerCase()) return;

      // Check modifiers
      if (ctrl && !event.ctrlKey) return;
      if (alt && !event.altKey) return;
      if (shift && !event.shiftKey) return;
      if (meta && !event.metaKey) return;

      // Don't trigger if user is typing in an input
      const target = event.target as HTMLElement;
      if (
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.isContentEditable
      ) {
        return;
      }

      event.preventDefault();
      callback();
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [key, callback, ctrl, alt, shift, meta, enabled]);
}

/**
 * Hook for global keyboard shortcuts
 */
export function useGlobalKeyboardShortcuts(onShowHelp?: () => void) {
  const navigate = useNavigate();

  // Navigation shortcuts
  useKeyboardShortcut('h', () => navigate('/'), { alt: true });
  useKeyboardShortcut('l', () => navigate('/library'), { alt: true });
  useKeyboardShortcut('s', () => navigate('/search'), { alt: true });
  useKeyboardShortcut('g', () => navigate('/graph'), { alt: true });
  useKeyboardShortcut('c', () => navigate('/collections'), { alt: true });
  useKeyboardShortcut('p', () => navigate('/profile'), { alt: true });

  // Search shortcut (Ctrl/Cmd + K)
  useKeyboardShortcut(
    'k',
    () => {
      navigate('/search');
      // Focus search input after navigation
      setTimeout(() => {
        const searchInput = document.querySelector('input[type="search"]') as HTMLInputElement;
        searchInput?.focus();
      }, 100);
    },
    { ctrl: true }
  );

  // Help shortcut (?)
  useKeyboardShortcut('?', () => {
    if (onShowHelp) {
      onShowHelp();
    }
  });
}

/**
 * Hook for focus trap in modals and dialogs
 */
export function useFocusTrap(
  containerRef: React.RefObject<HTMLElement>,
  isActive: boolean
) {
  useEffect(() => {
    if (!isActive || !containerRef.current) return;

    const container = containerRef.current;
    const focusableElements = container.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    // Focus first element
    firstElement?.focus();

    const handleTab = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        // Shift + Tab
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement?.focus();
        }
      } else {
        // Tab
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement?.focus();
        }
      }
    };

    document.addEventListener('keydown', handleTab);
    return () => document.removeEventListener('keydown', handleTab);
  }, [containerRef, isActive]);
}

/**
 * Hook for escape key handling
 */
export function useEscapeKey(callback: () => void, enabled = true) {
  useEffect(() => {
    if (!enabled) return;

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        callback();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [callback, enabled]);
}

/**
 * Hook for arrow key navigation in lists
 */
export function useArrowKeyNavigation(
  itemsRef: React.RefObject<HTMLElement[]>,
  options: {
    enabled?: boolean;
    loop?: boolean;
    orientation?: 'vertical' | 'horizontal';
  } = {}
) {
  const { enabled = true, loop = true, orientation = 'vertical' } = options;

  useEffect(() => {
    if (!enabled || !itemsRef.current) return;

    const handleArrowKey = (e: KeyboardEvent) => {
      const items = itemsRef.current;
      if (!items || items.length === 0) return;

      const currentIndex = items.findIndex((item) => item === document.activeElement);
      if (currentIndex === -1) return;

      let nextIndex = currentIndex;

      if (orientation === 'vertical') {
        if (e.key === 'ArrowDown') {
          e.preventDefault();
          nextIndex = currentIndex + 1;
        } else if (e.key === 'ArrowUp') {
          e.preventDefault();
          nextIndex = currentIndex - 1;
        }
      } else {
        if (e.key === 'ArrowRight') {
          e.preventDefault();
          nextIndex = currentIndex + 1;
        } else if (e.key === 'ArrowLeft') {
          e.preventDefault();
          nextIndex = currentIndex - 1;
        }
      }

      // Handle looping
      if (loop) {
        if (nextIndex >= items.length) nextIndex = 0;
        if (nextIndex < 0) nextIndex = items.length - 1;
      } else {
        if (nextIndex >= items.length) nextIndex = items.length - 1;
        if (nextIndex < 0) nextIndex = 0;
      }

      items[nextIndex]?.focus();
    };

    document.addEventListener('keydown', handleArrowKey);
    return () => document.removeEventListener('keydown', handleArrowKey);
  }, [itemsRef, enabled, loop, orientation]);
}

/**
 * Get keyboard shortcuts help text
 */
export function getKeyboardShortcuts(): KeyboardShortcut[] {
  return [
    {
      key: 'Alt + H',
      action: () => {},
      description: 'Navigate to Home',
    },
    {
      key: 'Alt + L',
      action: () => {},
      description: 'Navigate to Library',
    },
    {
      key: 'Alt + S',
      action: () => {},
      description: 'Navigate to Search',
    },
    {
      key: 'Alt + G',
      action: () => {},
      description: 'Navigate to Knowledge Graph',
    },
    {
      key: 'Alt + C',
      action: () => {},
      description: 'Navigate to Collections',
    },
    {
      key: 'Alt + P',
      action: () => {},
      description: 'Navigate to Profile',
    },
    {
      key: 'Ctrl/Cmd + K',
      action: () => {},
      description: 'Quick search',
    },
    {
      key: '?',
      action: () => {},
      description: 'Show keyboard shortcuts',
    },
    {
      key: 'Escape',
      action: () => {},
      description: 'Close modal or dialog',
    },
    {
      key: 'Tab',
      action: () => {},
      description: 'Navigate forward',
    },
    {
      key: 'Shift + Tab',
      action: () => {},
      description: 'Navigate backward',
    },
  ];
}
