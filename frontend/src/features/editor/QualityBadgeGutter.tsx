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
 * - Real-time quality data from backend via TanStack Query
 * 
 * Performance optimizations:
 * - Memoized with React.memo to prevent unnecessary re-renders
 * - Callbacks memoized with useCallback
 * - TanStack Query caching (15 min stale time)
 * 
 * Phase: 2.5 Backend API Integration
 * Task: 8.3 Update quality store to use real data
 * Requirements: 5.1, 5.9, 5.10
 */

import { useEffect, useRef, useCallback, memo } from 'react';
import type * as Monaco from 'monaco-editor';
import type { QualityLevel } from './types';
import { useQualityStore } from '@/stores/quality';
import { useQualityDetails } from '@/lib/hooks/useEditorData';
import type { Resource } from '@/types/api';

// ============================================================================
// Types
// ============================================================================

export interface QualityBadgeGutterProps {
  editor: Monaco.editor.IStandaloneCodeEditor | null;
  visible: boolean;
  resourceId: string; // Required for fetching quality data
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
 * Extract quality badges from resource data
 * For now, we place a single badge at line 1 representing overall quality
 * In the future, this could be extended to show per-function or per-chunk quality
 */
function extractQualityBadges(resource: Resource): QualityBadge[] {
  if (!resource.quality_overall || !resource.quality_dimensions) {
    return [];
  }
  
  // For now, show overall quality at line 1
  // TODO: In future, extract per-chunk or per-function quality scores
  const badge: QualityBadge = {
    line: 1,
    score: resource.quality_overall,
    level: getQualityLevel(resource.quality_overall),
    dimensions: resource.quality_dimensions,
  };
  
  return [badge];
}

// ============================================================================
// Component
// ============================================================================

const QualityBadgeGutterComponent = ({
  editor,
  visible,
  resourceId,
  onBadgeClick,
}: QualityBadgeGutterProps) => {
  const decorationsRef = useRef<string[]>([]);
  
  // Get badge visibility from store
  const { badgeVisibility } = useQualityStore();
  
  // Fetch quality data using TanStack Query hook
  // This automatically handles caching, loading states, and errors
  const { data: resource, isLoading, isError } = useQualityDetails(resourceId, {
    enabled: visible && badgeVisibility && !!resourceId,
  });
  
  // Determine if badges should be shown
  const shouldShowBadges = visible && badgeVisibility && !isLoading && !isError && !!resource;
  
  // Update decorations when quality data or visibility changes
  useEffect(() => {
    if (!editor) return;
    
    // Clear existing decorations if not visible or no data
    if (!shouldShowBadges || !resource) {
      decorationsRef.current = editor.deltaDecorations(
        decorationsRef.current,
        []
      );
      return;
    }
    
    // Extract quality badges from resource data
    const badges = extractQualityBadges(resource);
    
    // If no badges, clear decorations
    if (badges.length === 0) {
      decorationsRef.current = editor.deltaDecorations(
        decorationsRef.current,
        []
      );
      return;
    }
    
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
  }, [editor, resource, shouldShowBadges]);
  
  // Handle badge clicks
  const handleBadgeClick = useCallback(
    (lineNumber: number) => {
      if (!resource || !onBadgeClick) return;
      
      const badges = extractQualityBadges(resource);
      const badge = badges.find((b) => b.line === lineNumber);
      
      if (badge) {
        onBadgeClick(lineNumber);
      }
    },
    [resource, onBadgeClick]
  );
  
  useEffect(() => {
    if (!editor || !shouldShowBadges || !resource || !onBadgeClick) return;
    
    // Listen for mouse down events in the glyph margin
    const disposable = editor.onMouseDown((e) => {
      // Check if click was in glyph margin
      if (e.target.type !== (window as any).monaco.editor.MouseTargetType.GUTTER_GLYPH_MARGIN) {
        return;
      }
      
      // Get the line number that was clicked
      const lineNumber = e.target.position?.lineNumber;
      if (lineNumber) {
        handleBadgeClick(lineNumber);
      }
    });
    
    return () => {
      disposable.dispose();
    };
  }, [editor, shouldShowBadges, resource, onBadgeClick, handleBadgeClick]);
  
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

// Memoize the component to prevent unnecessary re-renders
// Requirements: 7.2 - React optimization
export const QualityBadgeGutter = memo(QualityBadgeGutterComponent, (prevProps, nextProps) => {
  // Custom comparison function for better memoization
  return (
    prevProps.editor === nextProps.editor &&
    prevProps.visible === nextProps.visible &&
    prevProps.resourceId === nextProps.resourceId &&
    prevProps.onBadgeClick === nextProps.onBadgeClick
  );
});

QualityBadgeGutter.displayName = 'QualityBadgeGutter';
