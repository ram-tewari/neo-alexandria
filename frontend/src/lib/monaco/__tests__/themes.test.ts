/**
 * Tests for Monaco Editor theme configuration
 * 
 * Tests comprehensive syntax highlighting, theme switching,
 * gutter decoration styling, and language-specific enhancements.
 */

import { describe, it, expect, vi } from 'vitest';
import {
  registerThemes,
  getMonacoTheme,
  applyTheme,
  getGutterDecorationColors,
  getLanguageThemeRules,
  lightTheme,
  darkTheme,
} from '../themes';

describe('Monaco Themes', () => {
  describe('lightTheme', () => {
    it('should have correct base theme', () => {
      expect(lightTheme.base).toBe('vs');
    });

    it('should inherit from base theme', () => {
      expect(lightTheme.inherit).toBe(true);
    });

    it('should define comprehensive syntax highlighting rules', () => {
      expect(lightTheme.rules).toBeDefined();
      expect(lightTheme.rules.length).toBeGreaterThan(20); // Should have many rules
      
      // Check for key token types
      const tokenTypes = lightTheme.rules.map(rule => rule.token);
      expect(tokenTypes).toContain('comment');
      expect(tokenTypes).toContain('keyword');
      expect(tokenTypes).toContain('string');
      expect(tokenTypes).toContain('number');
      expect(tokenTypes).toContain('function');
      expect(tokenTypes).toContain('class');
      expect(tokenTypes).toContain('variable');
      expect(tokenTypes).toContain('constant');
      expect(tokenTypes).toContain('operator');
    });

    it('should define editor colors', () => {
      expect(lightTheme.colors).toBeDefined();
      expect(lightTheme.colors['editor.background']).toBe('#ffffff');
      expect(lightTheme.colors['editor.foreground']).toBe('#24292e');
    });

    it('should define gutter colors', () => {
      expect(lightTheme.colors['editorGutter.background']).toBe('#ffffff');
      expect(lightTheme.colors['editorGutter.modifiedBackground']).toBeDefined();
      expect(lightTheme.colors['editorGutter.addedBackground']).toBeDefined();
      expect(lightTheme.colors['editorGutter.deletedBackground']).toBeDefined();
    });

    it('should define selection colors', () => {
      expect(lightTheme.colors['editor.selectionBackground']).toBe('#c8e1ff');
      expect(lightTheme.colors['editor.selectionHighlightBackground']).toBeDefined();
    });

    it('should define widget colors for hover cards', () => {
      expect(lightTheme.colors['editorWidget.background']).toBeDefined();
      expect(lightTheme.colors['editorWidget.border']).toBeDefined();
      expect(lightTheme.colors['editorHoverWidget.background']).toBeDefined();
    });

    it('should have WCAG AA compliant contrast', () => {
      // Background is white (#ffffff), foreground should have sufficient contrast
      expect(lightTheme.colors['editor.background']).toBe('#ffffff');
      expect(lightTheme.colors['editor.foreground']).toBe('#24292e');
      // This combination has a contrast ratio > 4.5:1
    });
  });

  describe('darkTheme', () => {
    it('should have correct base theme', () => {
      expect(darkTheme.base).toBe('vs-dark');
    });

    it('should inherit from base theme', () => {
      expect(darkTheme.inherit).toBe(true);
    });

    it('should define comprehensive syntax highlighting rules', () => {
      expect(darkTheme.rules).toBeDefined();
      expect(darkTheme.rules.length).toBeGreaterThan(20); // Should have many rules
      
      // Check for key token types
      const tokenTypes = darkTheme.rules.map(rule => rule.token);
      expect(tokenTypes).toContain('comment');
      expect(tokenTypes).toContain('keyword');
      expect(tokenTypes).toContain('string');
      expect(tokenTypes).toContain('number');
      expect(tokenTypes).toContain('function');
      expect(tokenTypes).toContain('class');
      expect(tokenTypes).toContain('variable');
    });

    it('should define editor colors', () => {
      expect(darkTheme.colors).toBeDefined();
      expect(darkTheme.colors['editor.background']).toBe('#0d1117');
      expect(darkTheme.colors['editor.foreground']).toBe('#c9d1d9');
    });

    it('should define gutter colors', () => {
      expect(darkTheme.colors['editorGutter.background']).toBe('#0d1117');
      expect(darkTheme.colors['editorGutter.modifiedBackground']).toBeDefined();
      expect(darkTheme.colors['editorGutter.addedBackground']).toBeDefined();
      expect(darkTheme.colors['editorGutter.deletedBackground']).toBeDefined();
    });

    it('should define selection colors', () => {
      expect(darkTheme.colors['editor.selectionBackground']).toBe('#1f6feb');
      expect(darkTheme.colors['editor.selectionHighlightBackground']).toBeDefined();
    });

    it('should define widget colors for hover cards', () => {
      expect(darkTheme.colors['editorWidget.background']).toBeDefined();
      expect(darkTheme.colors['editorWidget.border']).toBeDefined();
      expect(darkTheme.colors['editorHoverWidget.background']).toBeDefined();
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

    it('should not throw if called multiple times', () => {
      const mockMonaco = {
        editor: {
          defineTheme: vi.fn(),
        },
      };

      expect(() => {
        registerThemes(mockMonaco as any);
        registerThemes(mockMonaco as any);
      }).not.toThrow();
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

  describe('applyTheme', () => {
    it('should apply light theme', () => {
      const mockMonaco = {
        editor: {
          setTheme: vi.fn(),
        },
      };

      applyTheme(mockMonaco as any, 'light');

      expect(mockMonaco.editor.setTheme).toHaveBeenCalledWith('pharos-light');
    });

    it('should apply dark theme', () => {
      const mockMonaco = {
        editor: {
          setTheme: vi.fn(),
        },
      };

      applyTheme(mockMonaco as any, 'dark');

      expect(mockMonaco.editor.setTheme).toHaveBeenCalledWith('pharos-dark');
    });

    it('should allow theme switching without reload', () => {
      const mockMonaco = {
        editor: {
          setTheme: vi.fn(),
        },
      };

      // Switch from light to dark
      applyTheme(mockMonaco as any, 'light');
      applyTheme(mockMonaco as any, 'dark');

      expect(mockMonaco.editor.setTheme).toHaveBeenCalledTimes(2);
      expect(mockMonaco.editor.setTheme).toHaveBeenNthCalledWith(1, 'pharos-light');
      expect(mockMonaco.editor.setTheme).toHaveBeenNthCalledWith(2, 'pharos-dark');
    });
  });

  describe('getGutterDecorationColors', () => {
    describe('light theme', () => {
      it('should return light theme colors', () => {
        const colors = getGutterDecorationColors('light');

        expect(colors).toBeDefined();
        expect(colors.chunkBorder).toBeDefined();
        expect(colors.chunkBackground).toBeDefined();
        expect(colors.qualityHigh).toBe('#22863a');
        expect(colors.qualityMedium).toBe('#e36209');
        expect(colors.qualityLow).toBe('#cb2431');
        expect(colors.annotationDefault).toBe('#005cc5');
      });

      it('should have chunk decoration colors', () => {
        const colors = getGutterDecorationColors('light');

        expect(colors.chunkBorder).toContain('rgba');
        expect(colors.chunkBackground).toContain('rgba');
        expect(colors.chunkHoverBorder).toBeDefined();
        expect(colors.chunkHoverBackground).toBeDefined();
        expect(colors.chunkSelectedBorder).toBe('#005cc5');
      });

      it('should have quality badge colors', () => {
        const colors = getGutterDecorationColors('light');

        expect(colors.qualityHigh).toBe('#22863a'); // Green
        expect(colors.qualityMedium).toBe('#e36209'); // Orange
        expect(colors.qualityLow).toBe('#cb2431'); // Red
      });

      it('should have annotation colors', () => {
        const colors = getGutterDecorationColors('light');

        expect(colors.annotationDefault).toBe('#005cc5');
        expect(colors.annotationHighlight).toContain('rgba');
        expect(colors.annotationBorder).toBe('#005cc5');
      });

      it('should have reference icon colors', () => {
        const colors = getGutterDecorationColors('light');

        expect(colors.referenceIcon).toBe('#6a737d');
        expect(colors.referenceIconHover).toBe('#24292e');
      });
    });

    describe('dark theme', () => {
      it('should return dark theme colors', () => {
        const colors = getGutterDecorationColors('dark');

        expect(colors).toBeDefined();
        expect(colors.chunkBorder).toBeDefined();
        expect(colors.chunkBackground).toBeDefined();
        expect(colors.qualityHigh).toBe('#7ee787');
        expect(colors.qualityMedium).toBe('#ffa657');
        expect(colors.qualityLow).toBe('#f85149');
        expect(colors.annotationDefault).toBe('#79c0ff');
      });

      it('should have chunk decoration colors', () => {
        const colors = getGutterDecorationColors('dark');

        expect(colors.chunkBorder).toContain('rgba');
        expect(colors.chunkBackground).toContain('rgba');
        expect(colors.chunkSelectedBorder).toBe('#79c0ff');
      });

      it('should have quality badge colors', () => {
        const colors = getGutterDecorationColors('dark');

        expect(colors.qualityHigh).toBe('#7ee787'); // Green
        expect(colors.qualityMedium).toBe('#ffa657'); // Orange
        expect(colors.qualityLow).toBe('#f85149'); // Red
      });

      it('should have annotation colors', () => {
        const colors = getGutterDecorationColors('dark');

        expect(colors.annotationDefault).toBe('#79c0ff');
        expect(colors.annotationHighlight).toContain('rgba');
        expect(colors.annotationBorder).toBe('#79c0ff');
      });

      it('should have reference icon colors', () => {
        const colors = getGutterDecorationColors('dark');

        expect(colors.referenceIcon).toBe('#8b949e');
        expect(colors.referenceIconHover).toBe('#c9d1d9');
      });
    });

    it('should have different colors for light and dark themes', () => {
      const lightColors = getGutterDecorationColors('light');
      const darkColors = getGutterDecorationColors('dark');

      expect(lightColors.qualityHigh).not.toBe(darkColors.qualityHigh);
      expect(lightColors.annotationDefault).not.toBe(darkColors.annotationDefault);
      expect(lightColors.chunkSelectedBorder).not.toBe(darkColors.chunkSelectedBorder);
    });
  });

  describe('getLanguageThemeRules', () => {
    it('should return empty array for unsupported languages', () => {
      const rules = getLanguageThemeRules('plaintext', 'light');
      expect(rules).toEqual([]);
    });

    describe('Python', () => {
      it('should return Python-specific rules for light theme', () => {
        const rules = getLanguageThemeRules('python', 'light');

        expect(rules.length).toBeGreaterThan(0);
        expect(rules.some(r => r.token === 'decorator')).toBe(true);
        expect(rules.some(r => r.token === 'self')).toBe(true);
        expect(rules.some(r => r.token === 'cls')).toBe(true);
      });

      it('should return Python-specific rules for dark theme', () => {
        const rules = getLanguageThemeRules('python', 'dark');

        expect(rules.length).toBeGreaterThan(0);
        expect(rules.some(r => r.token === 'decorator')).toBe(true);
      });

      it('should have different colors for light and dark themes', () => {
        const lightRules = getLanguageThemeRules('python', 'light');
        const darkRules = getLanguageThemeRules('python', 'dark');

        const lightDecorator = lightRules.find(r => r.token === 'decorator');
        const darkDecorator = darkRules.find(r => r.token === 'decorator');

        expect(lightDecorator?.foreground).not.toBe(darkDecorator?.foreground);
      });
    });

    describe('TypeScript/JavaScript', () => {
      it('should return TypeScript-specific rules', () => {
        const rules = getLanguageThemeRules('typescript', 'light');

        expect(rules.length).toBeGreaterThan(0);
        expect(rules.some(r => r.token === 'type.identifier')).toBe(true);
        expect(rules.some(r => r.token === 'interface.name')).toBe(true);
        expect(rules.some(r => r.token === 'this')).toBe(true);
      });

      it('should return JavaScript-specific rules', () => {
        const rules = getLanguageThemeRules('javascript', 'light');

        expect(rules.length).toBeGreaterThan(0);
        expect(rules.some(r => r.token === 'this')).toBe(true);
      });
    });

    describe('Rust', () => {
      it('should return Rust-specific rules', () => {
        const rules = getLanguageThemeRules('rust', 'light');

        expect(rules.length).toBeGreaterThan(0);
        expect(rules.some(r => r.token === 'lifetime')).toBe(true);
        expect(rules.some(r => r.token === 'macro')).toBe(true);
      });

      it('should style lifetimes with italic', () => {
        const rules = getLanguageThemeRules('rust', 'light');
        const lifetime = rules.find(r => r.token === 'lifetime');

        expect(lifetime?.fontStyle).toBe('italic');
      });
    });

    describe('Go', () => {
      it('should return Go-specific rules', () => {
        const rules = getLanguageThemeRules('go', 'light');

        expect(rules.length).toBeGreaterThan(0);
        expect(rules.some(r => r.token === 'package')).toBe(true);
        expect(rules.some(r => r.token === 'import')).toBe(true);
      });
    });
  });

  describe('Theme consistency', () => {
    it('should have matching number of rules in light and dark themes', () => {
      expect(lightTheme.rules.length).toBe(darkTheme.rules.length);
    });

    it('should have matching token types in light and dark themes', () => {
      const lightTokens = lightTheme.rules.map(r => r.token).sort();
      const darkTokens = darkTheme.rules.map(r => r.token).sort();

      expect(lightTokens).toEqual(darkTokens);
    });

    it('should define all required editor colors in both themes', () => {
      const requiredColors = [
        'editor.background',
        'editor.foreground',
        'editor.lineHighlightBackground',
        'editor.selectionBackground',
        'editorLineNumber.foreground',
        'editorGutter.background',
        'editorCursor.foreground',
      ];

      requiredColors.forEach(color => {
        expect(lightTheme.colors[color]).toBeDefined();
        expect(darkTheme.colors[color]).toBeDefined();
      });
    });
  });

  describe('Syntax highlighting coverage', () => {
    it('should support all major token types', () => {
      const requiredTokens = [
        'comment',
        'keyword',
        'string',
        'number',
        'function',
        'class',
        'variable',
        'constant',
        'operator',
        'type',
        'annotation',
      ];

      const lightTokens = lightTheme.rules.map(r => r.token);

      requiredTokens.forEach(token => {
        expect(lightTokens).toContain(token);
      });
    });

    it('should support markdown-specific tokens', () => {
      const markdownTokens = ['emphasis', 'strong', 'header', 'link'];
      const lightTokens = lightTheme.rules.map(r => r.token);

      markdownTokens.forEach(token => {
        expect(lightTokens).toContain(token);
      });
    });

    it('should support JSON-specific tokens', () => {
      const jsonTokens = ['key', 'property'];
      const lightTokens = lightTheme.rules.map(r => r.token);

      jsonTokens.forEach(token => {
        expect(lightTokens).toContain(token);
      });
    });
  });
});
