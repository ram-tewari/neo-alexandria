/**
 * UI Store Tests
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { useUIStore } from '../uiStore';

describe('UIStore', () => {
  beforeEach(() => {
    // Reset to initial state
    useUIStore.setState({
      sidebarCollapsed: false,
      commandPaletteOpen: false,
      theme: 'dark',
    });
  });

  describe('sidebar', () => {
    it('should toggle sidebar', () => {
      expect(useUIStore.getState().sidebarCollapsed).toBe(false);

      useUIStore.getState().toggleSidebar();
      expect(useUIStore.getState().sidebarCollapsed).toBe(true);

      useUIStore.getState().toggleSidebar();
      expect(useUIStore.getState().sidebarCollapsed).toBe(false);
    });

    it('should set sidebar collapsed state', () => {
      useUIStore.getState().setSidebarCollapsed(true);
      expect(useUIStore.getState().sidebarCollapsed).toBe(true);

      useUIStore.getState().setSidebarCollapsed(false);
      expect(useUIStore.getState().sidebarCollapsed).toBe(false);
    });
  });

  describe('command palette', () => {
    it('should open command palette', () => {
      useUIStore.getState().openCommandPalette();
      expect(useUIStore.getState().commandPaletteOpen).toBe(true);
    });

    it('should close command palette', () => {
      useUIStore.setState({ commandPaletteOpen: true });
      useUIStore.getState().closeCommandPalette();
      expect(useUIStore.getState().commandPaletteOpen).toBe(false);
    });

    it('should toggle command palette', () => {
      expect(useUIStore.getState().commandPaletteOpen).toBe(false);

      useUIStore.getState().toggleCommandPalette();
      expect(useUIStore.getState().commandPaletteOpen).toBe(true);

      useUIStore.getState().toggleCommandPalette();
      expect(useUIStore.getState().commandPaletteOpen).toBe(false);
    });
  });

  describe('theme', () => {
    it('should set theme', () => {
      useUIStore.getState().setTheme('light');
      expect(useUIStore.getState().theme).toBe('light');

      useUIStore.getState().setTheme('dark');
      expect(useUIStore.getState().theme).toBe('dark');
    });

    it('should toggle theme', () => {
      useUIStore.setState({ theme: 'dark' });
      useUIStore.getState().toggleTheme();
      expect(useUIStore.getState().theme).toBe('light');

      useUIStore.getState().toggleTheme();
      expect(useUIStore.getState().theme).toBe('dark');
    });

    it('should apply theme to document', () => {
      useUIStore.getState().setTheme('light');
      expect(document.documentElement.getAttribute('data-theme')).toBe('light');

      useUIStore.getState().setTheme('dark');
      expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
    });
  });
});
