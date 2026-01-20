import { useEffect, useRef } from 'react';

interface UseSidebarKeyboardNavOptions {
  enabled?: boolean;
  onEscape?: () => void;
}

export function useSidebarKeyboardNav({ enabled = true, onEscape }: UseSidebarKeyboardNavOptions = {}) {
  const sidebarRef = useRef<HTMLElement>(null);

  useEffect(() => {
    if (!enabled) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;
      const sidebar = sidebarRef.current;
      
      if (!sidebar || !sidebar.contains(target)) return;

      // Get all focusable elements in the sidebar
      const focusableElements = sidebar.querySelectorAll<HTMLElement>(
        'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])'
      );
      const focusableArray = Array.from(focusableElements);
      const currentIndex = focusableArray.indexOf(target);

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          if (currentIndex < focusableArray.length - 1) {
            focusableArray[currentIndex + 1]?.focus();
          }
          break;

        case 'ArrowUp':
          e.preventDefault();
          if (currentIndex > 0) {
            focusableArray[currentIndex - 1]?.focus();
          }
          break;

        case 'Home':
          e.preventDefault();
          focusableArray[0]?.focus();
          break;

        case 'End':
          e.preventDefault();
          focusableArray[focusableArray.length - 1]?.focus();
          break;

        case 'Escape':
          e.preventDefault();
          onEscape?.();
          break;

        case 'Enter':
        case ' ':
          // Let the default behavior handle activation
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [enabled, onEscape]);

  return sidebarRef;
}
