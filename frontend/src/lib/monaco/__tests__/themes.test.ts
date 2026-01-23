/**
 * Tests for Monaco Editor theme configuration
 */

import { describe, it, expect, vi } from 'vitest';
import { registerThemes, getMonacoTheme, lightTheme, darkTheme } from '../themes';

describe('Monaco Themes', () => {
  describe('lightTheme', () => {
    it('should have correct base theme', () => {
      expect(lightTheme.base).toBe('vs');
    });

    it('should inherit from base theme', () => {
      expect(lightTheme.inherit).toBe(true);
    });

    it('should define syntax highlighting rules', () => {
      expect(lightTheme.rules).toBeDefined();
      expect(lightTheme.rules.length).toBeGreaterThan(0);
    });

    it('should define editor colors', () => {
      expect(lightTheme.colors).toBeDefined();
      expect(lightTheme.colors['editor.background']).toBe('#ffffff');
      expect(lightTheme.colors['editor.foreground']).toBe('#24292e');
    });
  });

  describe('darkTheme', () => {
    it('should have correct base theme', () => {
      expect(darkTheme.base).toBe('vs-dark');
    });

    it('should inherit from base theme', () => {
      expect(darkTheme.inherit).toBe(true);
    });

    it('should define syntax highlighting rules', () => {
      expect(darkTheme.rules).toBeDefined();
      expect(darkTheme.rules.length).toBeGreaterThan(0);
    });

    it('should define editor colors', () => {
      expect(darkTheme.colors).toBeDefined();
      expect(darkTheme.colors['editor.background']).toBe('#0d1117');
      expect(darkTheme.colors['editor.foreground']).toBe('#c9d1d9');
    });
  });

  describe('registerThemes', () => {
    it('should register both light and dark themes', () => {
      const mockMonaco = {
        editor: {
          defineTheme: vi.fn(),
        },
      };

      registerThemes(mockMonaco as any);

      expect(mockMonaco.editor.defineTheme).toHaveBeenCalledTimes(2);
      expect(mockMonaco.editor.defineTheme).toHaveBeenCalledWith('pharos-light', lightTheme);
      expect(mockMonaco.editor.defineTheme).toHaveBeenCalledWith('pharos-dark', darkTheme);
    });
  });

  describe('getMonacoTheme', () => {
    it('should return pharos-light for light theme', () => {
      expect(getMonacoTheme('light')).toBe('pharos-light');
    });

    it('should return pharos-dark for dark theme', () => {
      expect(getMonacoTheme('dark')).toBe('pharos-dark');
    });
  });
});
