import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { useEditorPreferencesStore } from '../editorPreferences';

/**
 * Unit Tests for Editor Preferences Store
 * 
 * Feature: phase2-living-code-editor
 * Tests preference updates and persistence logic
 * Validates: Requirements 9.1, 9.3
 */

describe('Editor Preferences Store', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    
    // Reset store to default state
    useEditorPreferencesStore.getState().resetToDefaults();
  });

  afterEach(() => {
    localStorage.clear();
  });

  describe('Default Preferences', () => {
    it('should have correct default values', () => {
      const state = useEditorPreferencesStore.getState();
      
      expect(state.theme).toBe('vs-dark');
      expect(state.fontSize).toBe(14);
      expect(state.lineNumbers).toBe(true);
      expect(state.minimap).toBe(true);
      expect(state.wordWrap).toBe(false);
      expect(state.chunkBoundaries).toBe(true);
      expect(state.qualityBadges).toBe(true);
      expect(state.annotations).toBe(true);
      expect(state.references).toBe(true);
    });
  });

  describe('Update Preferences', () => {
    it('should update theme preference', () => {
      useEditorPreferencesStore.getState().updatePreference('theme', 'vs-light');
      expect(useEditorPreferencesStore.getState().theme).toBe('vs-light');
    });

    it('should update fontSize preference', () => {
      useEditorPreferencesStore.getState().updatePreference('fontSize', 16);
      expect(useEditorPreferencesStore.getState().fontSize).toBe(16);
    });

    it('should update lineNumbers preference', () => {
      useEditorPreferencesStore.getState().updatePreference('lineNumbers', false);
      expect(useEditorPreferencesStore.getState().lineNumbers).toBe(false);
    });

    it('should update minimap preference', () => {
      useEditorPreferencesStore.getState().updatePreference('minimap', false);
      expect(useEditorPreferencesStore.getState().minimap).toBe(false);
    });

    it('should update wordWrap preference', () => {
      useEditorPreferencesStore.getState().updatePreference('wordWrap', true);
      expect(useEditorPreferencesStore.getState().wordWrap).toBe(true);
    });
  });

  describe('Toggle Overlay Preferences', () => {
    it('should toggle chunk boundaries', () => {
      expect(useEditorPreferencesStore.getState().chunkBoundaries).toBe(true);
      
      useEditorPreferencesStore.getState().toggleChunkBoundaries();
      expect(useEditorPreferencesStore.getState().chunkBoundaries).toBe(false);
      
      useEditorPreferencesStore.getState().toggleChunkBoundaries();
      expect(useEditorPreferencesStore.getState().chunkBoundaries).toBe(true);
    });

    it('should toggle quality badges', () => {
      expect(useEditorPreferencesStore.getState().qualityBadges).toBe(true);
      
      useEditorPreferencesStore.getState().toggleQualityBadges();
      expect(useEditorPreferencesStore.getState().qualityBadges).toBe(false);
      
      useEditorPreferencesStore.getState().toggleQualityBadges();
      expect(useEditorPreferencesStore.getState().qualityBadges).toBe(true);
    });

    it('should toggle annotations', () => {
      expect(useEditorPreferencesStore.getState().annotations).toBe(true);
      
      useEditorPreferencesStore.getState().toggleAnnotations();
      expect(useEditorPreferencesStore.getState().annotations).toBe(false);
      
      useEditorPreferencesStore.getState().toggleAnnotations();
      expect(useEditorPreferencesStore.getState().annotations).toBe(true);
    });

    it('should toggle references', () => {
      expect(useEditorPreferencesStore.getState().references).toBe(true);
      
      useEditorPreferencesStore.getState().toggleReferences();
      expect(useEditorPreferencesStore.getState().references).toBe(false);
      
      useEditorPreferencesStore.getState().toggleReferences();
      expect(useEditorPreferencesStore.getState().references).toBe(true);
    });
  });

  describe('Reset to Defaults', () => {
    it('should reset all preferences to defaults', () => {
      // Change some preferences
      useEditorPreferencesStore.getState().updatePreference('theme', 'vs-light');
      useEditorPreferencesStore.getState().updatePreference('fontSize', 18);
      useEditorPreferencesStore.getState().toggleChunkBoundaries();
      useEditorPreferencesStore.getState().toggleQualityBadges();

      // Reset to defaults
      useEditorPreferencesStore.getState().resetToDefaults();

      const state = useEditorPreferencesStore.getState();
      expect(state.theme).toBe('vs-dark');
      expect(state.fontSize).toBe(14);
      expect(state.chunkBoundaries).toBe(true);
      expect(state.qualityBadges).toBe(true);
    });
  });

  describe('Persistence', () => {
    it('should persist preferences to localStorage', async () => {
      useEditorPreferencesStore.getState().updatePreference('theme', 'vs-light');
      useEditorPreferencesStore.getState().updatePreference('fontSize', 16);
      useEditorPreferencesStore.getState().toggleChunkBoundaries();

      // Wait for persistence
      await new Promise(resolve => setTimeout(resolve, 100));

      const stored = localStorage.getItem('editor-preferences-storage');
      expect(stored).toBeTruthy();
      
      if (stored) {
        const parsed = JSON.parse(stored);
        expect(parsed.state.theme).toBe('vs-light');
        expect(parsed.state.fontSize).toBe(16);
        expect(parsed.state.chunkBoundaries).toBe(false);
      }
    });

    it('should persist all overlay preferences', async () => {
      useEditorPreferencesStore.getState().toggleChunkBoundaries();
      useEditorPreferencesStore.getState().toggleQualityBadges();
      useEditorPreferencesStore.getState().toggleAnnotations();
      useEditorPreferencesStore.getState().toggleReferences();

      // Wait for persistence
      await new Promise(resolve => setTimeout(resolve, 100));

      const stored = localStorage.getItem('editor-preferences-storage');
      expect(stored).toBeTruthy();
      
      if (stored) {
        const parsed = JSON.parse(stored);
        expect(parsed.state.chunkBoundaries).toBe(false);
        expect(parsed.state.qualityBadges).toBe(false);
        expect(parsed.state.annotations).toBe(false);
        expect(parsed.state.references).toBe(false);
      }
    });

    it('should persist Monaco editor preferences', async () => {
      useEditorPreferencesStore.getState().updatePreference('lineNumbers', false);
      useEditorPreferencesStore.getState().updatePreference('minimap', false);
      useEditorPreferencesStore.getState().updatePreference('wordWrap', true);

      // Wait for persistence
      await new Promise(resolve => setTimeout(resolve, 100));

      const stored = localStorage.getItem('editor-preferences-storage');
      expect(stored).toBeTruthy();
      
      if (stored) {
        const parsed = JSON.parse(stored);
        expect(parsed.state.lineNumbers).toBe(false);
        expect(parsed.state.minimap).toBe(false);
        expect(parsed.state.wordWrap).toBe(true);
      }
    });
  });
});
