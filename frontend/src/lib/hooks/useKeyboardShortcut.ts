/**
 * useKeyboardShortcut hook for global keyboard shortcuts
 * Supports modifier keys (Cmd/Ctrl, Shift, Alt) with automatic platform detection
 */

import { useEffect, useCallback, useRef } from 'react';

/**
 * Modifier keys configuration
 */
export interface KeyboardModifiers {
  ctrl?: boolean;  // Ctrl key (Windows/Linux)
  meta?: boolean;  // Cmd key (Mac)
  shift?: boolean; // Shift key
  alt?: boolean;   // Alt/Option key
}

/**
 * Options for keyboard shortcut behavior
 */
export interface KeyboardShortcutOptions {
  /** Whether the shortcut is enabled (default: true) */
  enabled?: boolean;
  /** Whether to prevent default browser behavior (default: true) */
  preventDefault?: boolean;
  /** Target element to attach listener (default: window) */
  target?: HTMLElement | Window;
}

/**
 * Detects if the user is on a Mac
 */
const isMac = typeof window !== 'undefined' && navigator.platform.toUpperCase().indexOf('MAC') >= 0;

/**
 * Custom hook for registering global keyboard shortcuts
 * Automatically handles Cmd (Mac) vs Ctrl (Windows/Linux) detection
 * 
 * @param key - The key to listen for (e.g., 'k', 'Enter', 'Escape')
 * @param callback - Function to call when shortcut is triggered
 * @param modifiers - Modifier keys that must be pressed
 * @param options - Additional options for shortcut behavior
 * 
 * @example
 * // Open command palette with Cmd+K (Mac) or Ctrl+K (Windows/Linux)
 * useKeyboardShortcut('k', openCommandPalette, { meta: true, ctrl: true });
 * 
 * @example
 * // Save with Cmd+S / Ctrl+S
 * useKeyboardShortcut('s', handleSave, { meta: true, ctrl: true });
 * 
 * @example
 * // Delete with Shift+Delete
 * useKeyboardShortcut('Delete', handleDelete, { shift: true });
 */
export function useKeyboardShortcut(
  key: string,
  callback: (event: KeyboardEvent) => void,
  modifiers: KeyboardModifiers = {},
  options: KeyboardShortcutOptions = {}
): void {
  const {
    enabled = true,
    preventDefault = true,
    target = typeof window !== 'undefined' ? window : undefined,
  } = options;

  // Use ref to avoid recreating handler on every render
  const callbackRef = useRef(callback);
  
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      // Check if the key matches
      if (event.key.toLowerCase() !== key.toLowerCase()) {
        return;
      }

      // Check modifier keys
      const ctrlRequired = modifiers.ctrl ?? false;
      const metaRequired = modifiers.meta ?? false;
      const shiftRequired = modifiers.shift ?? false;
      const altRequired = modifiers.alt ?? false;

      // Handle Cmd (Mac) vs Ctrl (Windows/Linux) automatically
      // If both meta and ctrl are specified, match either based on platform
      const modifierMatch =
        (ctrlRequired && metaRequired
          ? isMac
            ? event.metaKey
            : event.ctrlKey
          : (!ctrlRequired || event.ctrlKey === ctrlRequired) &&
            (!metaRequired || event.metaKey === metaRequired)) &&
        (!shiftRequired || event.shiftKey === shiftRequired) &&
        (!altRequired || event.altKey === altRequired);

      if (!modifierMatch) {
        return;
      }

      // Prevent default browser behavior if requested
      if (preventDefault) {
        event.preventDefault();
      }

      // Call the callback
      callbackRef.current(event);
    },
    [key, modifiers, preventDefault]
  );

  useEffect(() => {
    // Don't attach listener if disabled or no target
    if (!enabled || !target) {
      return;
    }

    // Attach event listener
    target.addEventListener('keydown', handleKeyDown as EventListener);

    // Cleanup on unmount
    return () => {
      target.removeEventListener('keydown', handleKeyDown as EventListener);
    };
  }, [enabled, target, handleKeyDown]);
}
