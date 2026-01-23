/**
 * QualityBadgeGutter Usage Example
 * 
 * This example demonstrates how to integrate the QualityBadgeGutter component
 * with Monaco Editor to display quality scores in the gutter.
 */

import { useEffect, useRef, useState } from 'react';
import Editor, { OnMount } from '@monaco-editor/react';
import type * as Monaco from 'monaco-editor';
import { QualityBadgeGutter } from './QualityBadgeGutter';
import { useQualityStore } from '@/stores/quality';
import { useEditorPreferencesStore } from '@/stores/editorPreferences';
import type { QualityDetails } from './types';

// ============================================================================
// Example Component
// ============================================================================

export function QualityBadgeGutterExample() {
  const [editor, setEditor] = useState<Monaco.editor.IStandaloneCodeEditor | null>(null);
  const [resourceId] = useState('example-resource-1');
  
  // Get quality data and preferences from stores
  const qualityData = useQualityStore((state) => state.qualityData);
  const qualityBadges = useEditorPreferencesStore((state) => state.qualityBadges);
  const toggleQualityBadges = useEditorPreferencesStore((state) => state.toggleQualityBadges);
  
  // Handle editor mount
  const handleEditorMount: OnMount = (editor) => {
    setEditor(editor);
  };
  
  // Handle badge click
  const handleBadgeClick = (line: number) => {
    console.log('Quality badge clicked at line:', line);
    // You could show a detailed quality panel here
  };
  
  // Example code content
  const codeContent = `function calculateScore(data) {
  // This function has high quality
  const total = data.reduce((sum, item) => sum + item.value, 0);
  const average = total / data.length;
  return average;
}

function processData(input) {
  // This function has medium quality
  const result = input.map(x => x * 2);
  return result;
}

function badFunction(x) {
  // This function has low quality
  return x;
}`;
  
  return (
    <div className="flex flex-col h-screen">
      {/* Header with controls */}
      <div className="flex items-center justify-between p-4 border-b">
        <h1 className="text-2xl font-bold">Quality Badge Gutter Example</h1>
        
        <div className="flex items-center gap-4">
          <button
            onClick={toggleQualityBadges}
            className={`px-4 py-2 rounded ${
              qualityBadges
                ? 'bg-primary text-primary-foreground'
                : 'bg-secondary text-secondary-foreground'
            }`}
          >
            {qualityBadges ? 'Hide' : 'Show'} Quality Badges
          </button>
        </div>
      </div>
      
      {/* Editor container */}
      <div className="flex-1 p-4">
        <div className="h-full border rounded-lg overflow-hidden">
          <Editor
            height="100%"
            defaultLanguage="javascript"
            defaultValue={codeContent}
            onMount={handleEditorMount}
            options={{
              readOnly: true,
              minimap: { enabled: false },
              lineNumbers: 'on',
              glyphMargin: true, // Enable gutter for badges
              folding: true,
              fontSize: 14,
            }}
          />
          
          {/* Quality Badge Gutter Overlay */}
          <QualityBadgeGutter
            editor={editor}
            qualityData={qualityData}
            visible={qualityBadges}
            resourceId={resourceId}
            onBadgeClick={handleBadgeClick}
          />
        </div>
      </div>
      
      {/* Info panel */}
      <div className="p-4 border-t bg-muted">
        <h2 className="text-lg font-semibold mb-2">Quality Badge Legend</h2>
        <div className="flex gap-6">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-green-600 border-2 border-green-600" />
            <span>High Quality (≥ 80%)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-yellow-500 border-2 border-yellow-500" />
            <span>Medium Quality (60-80%)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-red-500 border-2 border-red-500" />
            <span>Low Quality (&lt; 60%)</span>
          </div>
        </div>
        <p className="mt-2 text-sm text-muted-foreground">
          Hover over badges to see detailed quality metrics. Click badges to view more information.
        </p>
      </div>
    </div>
  );
}

// ============================================================================
// Integration Example with MonacoEditorWrapper
// ============================================================================

/**
 * Example showing how to integrate QualityBadgeGutter with MonacoEditorWrapper
 */
export function IntegratedEditorExample() {
  const editorRef = useRef<Monaco.editor.IStandaloneCodeEditor | null>(null);
  const [resourceId] = useState('example-resource-1');
  
  // Get stores
  const qualityData = useQualityStore((state) => state.qualityData);
  const qualityBadges = useEditorPreferencesStore((state) => state.qualityBadges);
  
  const handleEditorMount: OnMount = (editor) => {
    editorRef.current = editor;
  };
  
  return (
    <div className="h-screen">
      <Editor
        height="100%"
        defaultLanguage="typescript"
        defaultValue="// Your code here"
        onMount={handleEditorMount}
        options={{
          readOnly: true,
          glyphMargin: true,
        }}
      />
      
      {/* Add QualityBadgeGutter as an overlay */}
      <QualityBadgeGutter
        editor={editorRef.current}
        qualityData={qualityData}
        visible={qualityBadges}
        resourceId={resourceId}
      />
    </div>
  );
}

// ============================================================================
// Mock Data Example
// ============================================================================

/**
 * Example showing how to provide mock quality data for testing
 */
export function MockDataExample() {
  const [editor, setEditor] = useState<Monaco.editor.IStandaloneCodeEditor | null>(null);
  
  // Mock quality data
  const mockQualityData: QualityDetails = {
    resource_id: 'mock-resource',
    quality_dimensions: {
      accuracy: 0.85,
      completeness: 0.90,
      consistency: 0.80,
      timeliness: 0.75,
      relevance: 0.88,
    },
    quality_overall: 0.84,
    quality_weights: {
      accuracy: 0.25,
      completeness: 0.25,
      consistency: 0.20,
      timeliness: 0.15,
      relevance: 0.15,
    },
    quality_last_computed: new Date().toISOString(),
    is_quality_outlier: false,
    needs_quality_review: false,
  };
  
  return (
    <div className="h-screen">
      <Editor
        height="100%"
        defaultLanguage="python"
        defaultValue="def hello():\n    print('Hello, World!')"
        onMount={setEditor}
        options={{
          readOnly: true,
          glyphMargin: true,
        }}
      />
      
      <QualityBadgeGutter
        editor={editor}
        qualityData={mockQualityData}
        visible={true}
      />
    </div>
  );
}

// ============================================================================
// Usage Notes
// ============================================================================

/**
 * USAGE NOTES:
 * 
 * 1. Basic Setup:
 *    - Import QualityBadgeGutter component
 *    - Pass Monaco editor instance
 *    - Provide quality data from store or API
 *    - Set visible prop to control badge visibility
 * 
 * 2. Quality Data:
 *    - Quality data should come from useQualityStore
 *    - Store handles caching and API calls
 *    - Component supports lazy-loading with resourceId prop
 * 
 * 3. Visibility Control:
 *    - Use editorPreferencesStore.qualityBadges for visibility
 *    - User can toggle badges with keyboard shortcut (Cmd+Shift+Q)
 *    - Visibility preference is persisted to localStorage
 * 
 * 4. Badge Interaction:
 *    - Hover over badges to see detailed quality metrics
 *    - Click badges to trigger onBadgeClick callback
 *    - Use callback to show detailed quality panel or navigate
 * 
 * 5. Styling:
 *    - Badge colors are defined in editor.css
 *    - Green: High quality (>= 0.8)
 *    - Yellow: Medium quality (0.6 - 0.8)
 *    - Red: Low quality (< 0.6) with pulsing glow effect
 * 
 * 6. Performance:
 *    - Component uses lazy-loading for quality data
 *    - Scroll events are debounced (300ms)
 *    - Quality data is cached per resource
 *    - Decorations are batched for efficiency
 * 
 * 7. Integration with Other Overlays:
 *    - QualityBadgeGutter works alongside SemanticChunkOverlay
 *    - Each overlay uses different glyph margin positions
 *    - All overlays respect editor preferences
 */

