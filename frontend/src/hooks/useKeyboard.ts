import { useEffect } from 'react';

export const useKeyboard = (
  key: string,
  callback: () => void,
  options: {
    ctrl?: boolean;
    meta?: boolean;
    shift?: boolean;
    alt?: boolean;
  } = {}
) => {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const matchesKey = e.key.toLowerCase() === key.toLowerCase();
      const matchesCtrl = options.ctrl ? e.ctrlKey : !e.ctrlKey;
      const matchesMeta = options.meta ? e.metaKey : !e.metaKey;
      const matchesShift = options.shift ? e.shiftKey : !e.shiftKey;
      const matchesAlt = options.alt ? e.altKey : !e.altKey;

      if (matchesKey && matchesCtrl && matchesMeta && matchesShift && matchesAlt) {
        e.preventDefault();
        callback();
      }
    };

    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [key, callback, options]);
};

export const useCommandPalette = (callback: () => void) => {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      // Cmd+K on Mac, Ctrl+K on Windows/Linux
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        callback();
      }
    };

    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [callback]);
};
