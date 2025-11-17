/**
 * Command Palette Hook
 * 
 * Global keyboard shortcut handler for Cmd/Ctrl+K
 */

import { useEffect } from 'react';
import { useUIStore } from '@/store';

export const useCommandPalette = () => {
  const { openCommandPalette, closeCommandPalette, commandPaletteOpen } = useUIStore();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd+K or Ctrl+K to open command palette
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        if (commandPaletteOpen) {
          closeCommandPalette();
        } else {
          openCommandPalette();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [openCommandPalette, closeCommandPalette, commandPaletteOpen]);

  return {
    isOpen: commandPaletteOpen,
    open: openCommandPalette,
    close: closeCommandPalette,
  };
};
