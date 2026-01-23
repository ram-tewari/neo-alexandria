/**
 * Tests for Monaco Editor language configuration
 */

import { describe, it, expect } from 'vitest';
import {
  detectLanguage,
  getLanguageName,
  supportsSemanticHighlighting,
  extensionToLanguage,
} from '../languages';

describe('Monaco Languages', () => {
  describe('extensionToLanguage', () => {
    it('should map common JavaScript extensions', () => {
      expect(extensionToLanguage.js).toBe('javascript');
      expect(extensionToLanguage.jsx).toBe('javascript');
      expect(extensionToLanguage.mjs).toBe('javascript');
      expect(extensionToLanguage.cjs).toBe('javascript');
    });

    it('should map TypeScript extensions', () => {
      expect(extensionToLanguage.ts).toBe('typescript');
      expect(extensionToLanguage.tsx).toBe('typescript');
    });

    it('should map Python extensions', () => {
      expect(extensionToLanguage.py).toBe('python');
      expect(extensionToLanguage.pyw).toBe('python');
      expect(extensionToLanguage.pyi).toBe('python');
    });

    it('should map web technology extensions', () => {
      expect(extensionToLanguage.html).toBe('html');
      expect(extensionToLanguage.css).toBe('css');
      expect(extensionToLanguage.scss).toBe('scss');
    });

    it('should map data format extensions', () => {
      expect(extensionToLanguage.json).toBe('json');
      expect(extensionToLanguage.yaml).toBe('yaml');
      expect(extensionToLanguage.xml).toBe('xml');
    });
  });

  describe('detectLanguage', () => {
    it('should detect JavaScript files', () => {
      expect(detectLanguage('app.js')).toBe('javascript');
      expect(detectLanguage('component.jsx')).toBe('javascript');
      expect(detectLanguage('module.mjs')).toBe('javascript');
    });

    it('should detect TypeScript files', () => {
      expect(detectLanguage('app.ts')).toBe('typescript');
      expect(detectLanguage('Component.tsx')).toBe('typescript');
    });

    it('should detect Python files', () => {
      expect(detectLanguage('script.py')).toBe('python');
      expect(detectLanguage('__init__.py')).toBe('python');
    });

    it('should detect web files', () => {
      expect(detectLanguage('index.html')).toBe('html');
      expect(detectLanguage('styles.css')).toBe('css');
      expect(detectLanguage('styles.scss')).toBe('scss');
    });

    it('should detect data format files', () => {
      expect(detectLanguage('config.json')).toBe('json');
      expect(detectLanguage('config.yaml')).toBe('yaml');
      expect(detectLanguage('data.xml')).toBe('xml');
    });

    it('should detect markdown files', () => {
      expect(detectLanguage('README.md')).toBe('markdown');
      expect(detectLanguage('docs.markdown')).toBe('markdown');
    });

    it('should handle files with multiple dots', () => {
      expect(detectLanguage('app.test.ts')).toBe('typescript');
      expect(detectLanguage('config.dev.json')).toBe('json');
    });

    it('should handle uppercase extensions', () => {
      expect(detectLanguage('App.JS')).toBe('javascript');
      expect(detectLanguage('README.MD')).toBe('markdown');
    });

    it('should default to plaintext for unknown extensions', () => {
      expect(detectLanguage('file.unknown')).toBe('plaintext');
      expect(detectLanguage('file.xyz')).toBe('plaintext');
    });

    it('should default to plaintext for files without extension', () => {
      expect(detectLanguage('Makefile')).toBe('plaintext');
      expect(detectLanguage('LICENSE')).toBe('plaintext');
    });
  });

  describe('getLanguageName', () => {
    it('should return human-readable names for common languages', () => {
      expect(getLanguageName('javascript')).toBe('JavaScript');
      expect(getLanguageName('typescript')).toBe('TypeScript');
      expect(getLanguageName('python')).toBe('Python');
      expect(getLanguageName('html')).toBe('HTML');
      expect(getLanguageName('css')).toBe('CSS');
    });

    it('should return human-readable names for compiled languages', () => {
      expect(getLanguageName('java')).toBe('Java');
      expect(getLanguageName('cpp')).toBe('C++');
      expect(getLanguageName('c')).toBe('C');
      expect(getLanguageName('go')).toBe('Go');
      expect(getLanguageName('rust')).toBe('Rust');
    });

    it('should return human-readable names for data formats', () => {
      expect(getLanguageName('json')).toBe('JSON');
      expect(getLanguageName('yaml')).toBe('YAML');
      expect(getLanguageName('xml')).toBe('XML');
    });

    it('should return the language ID for unknown languages', () => {
      expect(getLanguageName('unknown')).toBe('unknown');
      expect(getLanguageName('custom-lang')).toBe('custom-lang');
    });
  });

  describe('supportsSemanticHighlighting', () => {
    it('should return true for languages with semantic support', () => {
      expect(supportsSemanticHighlighting('javascript')).toBe(true);
      expect(supportsSemanticHighlighting('typescript')).toBe(true);
      expect(supportsSemanticHighlighting('python')).toBe(true);
      expect(supportsSemanticHighlighting('java')).toBe(true);
      expect(supportsSemanticHighlighting('cpp')).toBe(true);
      expect(supportsSemanticHighlighting('c')).toBe(true);
      expect(supportsSemanticHighlighting('go')).toBe(true);
      expect(supportsSemanticHighlighting('rust')).toBe(true);
    });

    it('should return false for languages without semantic support', () => {
      expect(supportsSemanticHighlighting('html')).toBe(false);
      expect(supportsSemanticHighlighting('css')).toBe(false);
      expect(supportsSemanticHighlighting('json')).toBe(false);
      expect(supportsSemanticHighlighting('yaml')).toBe(false);
      expect(supportsSemanticHighlighting('markdown')).toBe(false);
      expect(supportsSemanticHighlighting('plaintext')).toBe(false);
    });
  });
});
