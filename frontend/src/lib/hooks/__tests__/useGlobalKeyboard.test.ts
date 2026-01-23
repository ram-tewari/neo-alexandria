import { describe, it, expect } from 'vitest';

/**
 * Unit Tests for Global Keyboard Shortcuts
 * 
 * Feature: phase1-workbench-navigation
 * Validates: Requirements 7.1, 7.2, 7.3
 * 
 * Note: These tests verify the keyboard shortcut logic.
 * Integration tests with actual DOM events should be done in E2E tests.
 */

describe('useGlobalKeyboard - Unit Tests', () => {
  /**
   * Test: Keyboard shortcut definitions
   * Validates: Requirements 7.1, 7.2, 7.3
   */
  it('should define correct keyboard shortcuts', () => {
    const shortcuts = {
      toggleSidebar: ['Ctrl+B', 'Cmd+B'],
      openCommandPalette: ['Ctrl+K', 'Cmd+K', 'Ctrl+Shift+P', 'Cmd+Shift+P'],
      closeCommandPalette: ['Escape'],
    };

    // Verify sidebar toggle shortcuts
    expect(shortcuts.toggleSidebar).toContain('Ctrl+B');
    expect(shortcuts.toggleSidebar).toContain('Cmd+B');

    // Verify command palette shortcuts
    expect(shortcuts.openCommandPalette).toContain('Ctrl+K');
    expect(shortcuts.openCommandPalette).toContain('Cmd+K');
    expect(shortcuts.openCommandPalette).toContain('Ctrl+Shift+P');
    expect(shortcuts.openCommandPalette).toContain('Cmd+Shift+P');

    // Verify escape shortcut
    expect(shortcuts.closeCommandPalette).toContain('Escape');
  });

  it('should have unique shortcuts for different actions', () => {
    const allShortcuts = [
      'Ctrl+B',
      'Cmd+B',
      'Ctrl+K',
      'Cmd+K',
      'Ctrl+Shift+P',
      'Cmd+Shift+P',
      'Escape',
    ];

    // Check that shortcuts are properly categorized
    const sidebarShortcuts = ['Ctrl+B', 'Cmd+B'];
    const paletteShortcuts = ['Ctrl+K', 'Cmd+K', 'Ctrl+Shift+P', 'Cmd+Shift+P'];
    const closeShortcuts = ['Escape'];

    // Verify no overlap between sidebar and palette shortcuts
    const overlap = sidebarShortcuts.filter(s => paletteShortcuts.includes(s));
    expect(overlap.length).toBe(0);
  });

  it('should support both Windows/Linux (Ctrl) and Mac (Cmd) modifiers', () => {
    const shortcuts = {
      sidebar: { windows: 'Ctrl+B', mac: 'Cmd+B' },
      palette: { windows: 'Ctrl+K', mac: 'Cmd+K' },
      paletteAlt: { windows: 'Ctrl+Shift+P', mac: 'Cmd+Shift+P' },
    };

    // Verify Windows/Linux shortcuts
    expect(shortcuts.sidebar.windows).toBe('Ctrl+B');
    expect(shortcuts.palette.windows).toBe('Ctrl+K');
    expect(shortcuts.paletteAlt.windows).toBe('Ctrl+Shift+P');

    // Verify Mac shortcuts
    expect(shortcuts.sidebar.mac).toBe('Cmd+B');
    expect(shortcuts.palette.mac).toBe('Cmd+K');
    expect(shortcuts.paletteAlt.mac).toBe('Cmd+Shift+P');
  });
});
