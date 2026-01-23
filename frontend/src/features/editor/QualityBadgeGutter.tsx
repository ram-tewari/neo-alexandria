/**
 * QualityBadgeGutter Component
 * 
 * Displays quality score badges in the Monaco editor glyph margin.
 * Badges are color-coded based on quality levels:
 * - Green: High quality (>= 0.8)
 * - Yellow: Medium quality (0.6 - 0.8)
 * - Red: Low quality (< 0.6)
 * 
 * Features:
 * - Renders badges in Monaco glyph margin
 * - Color coding based on quality scores
 * - Hover tooltips with detailed metrics
 * - Click events for badge interaction
 * - Visibility toggle support
 * - Lazy-loading with scroll-based updates
 * - Debounced quality data requests
 */

import { useEffect, useRef, useCallback } from 'react';
import type * as Monaco from 'monaco-editor';
import type { QualityDetails, QualityLevel } from './types';
import { useQualityStore } from '@/stores/quality';

// ============================================================================
// Types
// ============================================================================

export interface QualityBadgeGutterProps {
  editor: Monaco.editor.IStandaloneCodeEditor | null;
  qualityData: QualityDetails | null;
  visible: boolean;
  resourceId?: string; // For lazy-loading quality data
  onBadgeClick?: (line: number) => void;
}

interface QualityBadge {
  line: number;
  score: number;
  level: QualityLevel;
  dimensions: {
    accuracy: number;
    completeness: number;
    consistency: number;
    timeliness: number;
    relevance: number;
  };
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Determine quality level based on score
 */
function getQualityLevel(score: number): QualityLevel {
  if (score >= 0.8) return 'high';
  if (score >= 0.6) return 'medium';
  return 'low';
}

/**
 * Format quality score as percentage
 */
function formatScore(score: number): string {
  return `${(score * 100).toFixed(0)}%`;
}

/**
 * Generate hover message for quality badge
 */
function generateHoverMessage(badge: QualityBadge): string {
  const { score, dimensions } = badge;
  
  return [
    `**Quality Score: ${formatScore(score)}**`,
    '',
    '**Dimensions:**',
    `• Accuracy: ${formatScore(dimensions.accuracy)}`,
    `• Completeness: ${formatScore(dimensions.completeness)}`,
    `• Consistency: ${formatScore(dimensions.consistency)}`,
    `• Timeliness: ${formatScore(dimensions.timeliness)}`,
    `• Relevance: ${formatScore(dimensions.relevance)}`,
  ].join('\n');
}

/**
 * Extract quality badges from quality data
 * For now, we place a single badge at line 1 representing overall quality
 * In the future, this could be extended to show per-function or per-chunk quality
 */
function extractQualityBadges(qualityData: QualityDetails): QualityBadge[] {
  if (!qualityData) return [];
  
  // For now, show overall quality at line 1
  // TODO: In future, extract per-chunk or per-function quality scores
  const badge: QualityBadge = {
    line: 1,
    score: qualityData.quality_overall,
    level: getQualityLevel(qualityData.quality_overall),
    dimensions: qualityData.quality_dimensions,
  };
  
  return [badge];
}

// ============================================================================
// Component
// ============================================================================

export function QualityBadgeGutter({
  editor,
  qualityData,
  visible,
  resourceId,
  onBadgeClick,
}: QualityBadgeGutterProps) {
  const decorationsRef = useRef<string[]>([]);
  const scrollTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const lastFetchedResourceRef = useRef<string | null>(null);
  
  // Get quality store actions
  const { fetchQualityData, getCachedQuality } = useQualityStore();
  
  // Debounced quality data fetch
  const debouncedFetchQuality = useCallback(
    (resId: string) => {
      // Clear existing timeout
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
      
      // Set new timeout for debounced fetch
      scrollTimeoutRef.current = setTimeout(() => {
        // Check if we already have cached data
        const cached = getCachedQuality(resId);
        if (!cached && resId !== lastFetchedResourceRef.current) {
          fetchQualityData(resId);
          lastFetchedResourceRef.current = resId;
        }
      }, 300); // 300ms debounce
    },
    [fetchQualityData, getCachedQuality]
  );
  
  // Lazy-load quality data on scroll
  useEffect(() => {
    if (!editor || !visible || !resourceId) return;
    
    // Fetch quality data when component mounts or resourceId changes
    debouncedFetchQuality(resourceId);
    
    // Listen for scroll events to trigger lazy-loading
    const disposable = editor.onDidScrollChange(() => {
      if (visible && resourceId) {
        debouncedFetchQuality(resourceId);
      }
    });
    
    return () => {
      disposable.dispose();
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
    };
  }, [editor, visible, resourceId, debouncedFetchQuality]);
  
  // Update decorations when quality data or visibility changes
  useEffect(() => {
    if (!editor) return;
    
    // Clear existing decorations if not visible or no data
    if (!visible || !qualityData) {
      decorationsRef.current = editor.deltaDecorations(
        decorationsRef.current,
        []
      );
      return;
    }
    
    // Extract quality badges from quality data
    const badges = extractQualityBadges(qualityData);
    
    // Create Monaco decorations for each badge
    const newDecorations: Monaco.editor.IModelDeltaDecoration[] = badges.map(
      (badge) => ({
        range: new (window as any).monaco.Range(badge.line, 1, badge.line, 1),
        options: {
          glyphMarginClassName: `quality-badge quality-badge-${badge.level}`,
          glyphMarginHoverMessage: {
            value: generateHoverMessage(badge),
            isTrusted: true,
          },
        },
      })
    );
    
    // Apply decorations
    decorationsRef.current = editor.deltaDecorations(
      decorationsRef.current,
      newDecorations
    );
  }, [editor, qualityData, visible]);
  
  // Handle badge clicks
  useEffect(() => {
    if (!editor || !visible || !qualityData || !onBadgeClick) return;
    
    const badges = extractQualityBadges(qualityData);
    
    // Listen for mouse down events in the glyph margin
    const disposable = editor.onMouseDown((e) => {
      // Check if click was in glyph margin
      if (e.target.type !== (window as any).monaco.editor.MouseTargetType.GUTTER_GLYPH_MARGIN) {
        return;
      }
      
      // Get the line number that was clicked
      const lineNumber = e.target.position?.lineNumber;
      if (!lineNumber) return;
      
      // Check if there's a badge on this line
      const badge = badges.find((b) => b.line === lineNumber);
      if (badge) {
        onBadgeClick(lineNumber);
      }
    });
    
    return () => {
      disposable.dispose();
    };
  }, [editor, qualityData, visible, onBadgeClick]);
  
  // Cleanup decorations on unmount
  useEffect(() => {
    return () => {
      if (editor && decorationsRef.current.length > 0) {
        editor.deltaDecorations(decorationsRef.current, []);
      }
    };
  }, [editor]);
  
  // This component doesn't render anything directly
  // It only manages Monaco decorations
  return null;
}

