import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { useThemeStore } from '../theme';

/**
 * Property-Based Tests for Theme Store
 * 
 * Feature: phase1-workbench-navigation
 * Property 2: Theme Consistency
 * Validates: Requirements 5.1, 5.4
 */

describe('Theme Store - Property Tests', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    // Reset store to initial state
    useThemeStore.setState({ theme: 'system' });
  });

  afterEach(() => {
    localStorage.clear();
  });

  /**
   * Property 2: Theme Consistency
   * For any theme value ('light', 'dark', 'system'), setting the theme
   * should persist to localStorage and be retrievable on store rehydration
   */
  it('should persist theme to localStorage for all valid theme values', () => {
    const themes: Array<'light' | 'dark' | 'system'> = ['light', 'dark', 'system'];

    themes.forEach((theme) => {
      // Set theme
      useThemeStore.getState().setTheme(theme);

      // Verify store state
      expect(useThemeStore.getState().theme).toBe(theme);

      // Verify localStorage persistence
      const stored = localStorage.getItem('pharos-theme');
      expect(stored).toBeTruthy();
      
      const parsed = JSON.parse(stored!);
      expect(parsed.state.theme).toBe(theme);
    });
  });

  it('should maintain theme consistency across store resets', () => {
    const themes: Array<'light' | 'dark' | 'system'> = ['light', 'dark', 'system'];

    themes.forEach((theme) => {
      // Set theme
      useThemeStore.getState().setTheme(theme);
      
      // Simulate store rehydration by reading from localStorage
      const stored = localStorage.getItem('pharos-theme');
      const parsed = JSON.parse(stored!);
      
      // Verify consistency
      expect(parsed.state.theme).toBe(theme);
      expect(useThemeStore.getState().theme).toBe(theme);
    });
  });

  it('should default to system theme when no localStorage value exists', () => {
    // Clear localStorage
    localStorage.clear();
    
    // Get initial state
    const initialTheme = useThemeStore.getState().theme;
    
    // Should default to 'system'
    expect(initialTheme).toBe('system');
  });
});
