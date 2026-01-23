import { useEffect } from 'react';
import { useWorkbenchStore } from '../../stores/workbench';
import { useCommandPaletteStore } from '../../stores/command';

/**
 * Global keyboard shortcut handler
 * 
 * Registers global keyboard shortcuts that work throughout the application:
 * - Cmd/Ctrl + B: Toggle sidebar
 * - Cmd/Ctrl + K: Open command palette
 * - Cmd/Ctrl + Shift + P: Open command palette
 */
export function useGlobalKeyboard() {
  const { toggleSidebar } = useWorkbenchStore();
  const { toggle: toggleCommandPalette } = useCommandPaletteStore();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
      const modKey = isMac ? e.metaKey : e.ctrlKey;

      // Cmd/Ctrl + B: Toggle sidebar
      if (e.key === 'b' && modKey && !e.shiftKey) {
        e.preventDefault();
        toggleSidebar();
        return;
      }

      // Cmd/Ctrl + K: Open command palette
      if (e.key === 'k' && modKey && !e.shiftKey) {
        e.preventDefault();
        toggleCommandPalette();
        return;
      }

      // Cmd/Ctrl + Shift + P: Open command palette
      if (e.key === 'p' && modKey && e.shiftKey) {
        e.preventDefault();
        toggleCommandPalette();
        return;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [toggleSidebar, toggleCommandPalette]);
}
