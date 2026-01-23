/**
 * Type definitions for Phase 2: Living Code Editor
 * 
 * These types define the domain models for the editor feature including
 * code files, semantic chunks, quality data, annotations, and references.
 */

// ============================================================================
// Core Editor Types
// ============================================================================

export interface CodeFile {
  id: string;
  resource_id: string;
  path: string;
  name: string;
  language: string;
  content: string;
  size: number;
  lines: number;
  created_at: string;
  updated_at: string;
}

export interface Position {
  line: number;
  column: number;
}

export interface Selection {
  start: Position;
  end: Position;
}

// ============================================================================
// Semantic Chunk Types
// ============================================================================

export interface SemanticChunk {
  id: string;
  resource_id: string;
  content: string;
  chunk_index: number;
  chunk_metadata: ChunkMetadata;
  embedding_id?: string;
  created_at: string;
}

export interface ChunkMetadata {
  function_name?: string;
  class_name?: string;
  start_line: number;
  end_line: number;
  language: string;
}

// ============================================================================
// Quality Types
// ============================================================================

export interface QualityDetails {
  resource_id: string;
  quality_dimensions: QualityDimensions;
  quality_overall: number;
  quality_weights: QualityWeights;
  quality_last_computed: string;
  is_quality_outlier: boolean;
  needs_quality_review: boolean;
}

export interface QualityDimensions {
  accuracy: number;
  completeness: number;
  consistency: number;
  timeliness: number;
  relevance: number;
}

export interface QualityWeights {
  accuracy: number;
  completeness: number;
  consistency: number;
  timeliness: number;
  relevance: number;
}

export type QualityLevel = 'high' | 'medium' | 'low';

// ============================================================================
// Annotation Types
// ============================================================================

export interface Annotation {
  id: string;
  resource_id: string;
  user_id: string;
  start_offset: number;
  end_offset: number;
  highlighted_text: string;
  note?: string;
  tags?: string[];
  color: string;
  context_before?: string;
  context_after?: string;
  is_shared: boolean;
  collection_ids?: string[];
  created_at: string;
  updated_at: string;
}

export interface AnnotationCreate {
  start_offset: number;
  end_offset: number;
  highlighted_text: string;
  note?: string;
  tags?: string[];
  color?: string;
  collection_ids?: string[];
}

export interface AnnotationUpdate {
  note?: string;
  tags?: string[];
  color?: string;
  is_shared?: boolean;
}

// ============================================================================
// Reference Types
// ============================================================================

export interface Reference {
  id: string;
  resource_id: string;
  line_number: number;
  reference_type: 'paper' | 'documentation' | 'external';
  title: string;
  authors?: string[];
  url?: string;
  pdf_id?: string; // Link to library PDF
  citation?: string;
  created_at: string;
}

// ============================================================================
// Hover Card Types
// ============================================================================

export interface HoverCardData {
  symbol: string;
  summary: string; // Node2Vec summary
  connections: SymbolConnection[];
  loading: boolean;
  error?: string;
}

export interface SymbolConnection {
  name: string;
  type: 'function' | 'class' | 'variable';
  relationship: 'calls' | 'imports' | 'defines';
  file: string;
}

// ============================================================================
// Editor Preferences Types
// ============================================================================

export interface EditorPreferences {
  theme: 'vs-light' | 'vs-dark';
  fontSize: number;
  lineNumbers: boolean;
  minimap: boolean;
  wordWrap: boolean;
  chunkBoundaries: boolean;
  qualityBadges: boolean;
  annotations: boolean;
  references: boolean;
}

// ============================================================================
// Monaco Decoration Types
// ============================================================================

export interface DecorationOptions {
  range: {
    startLineNumber: number;
    startColumn: number;
    endLineNumber: number;
    endColumn: number;
  };
  options: {
    isWholeLine?: boolean;
    className?: string;
    glyphMarginClassName?: string;
    glyphMarginHoverMessage?: { value: string };
    hoverMessage?: { value: string };
    inlineClassName?: string;
    inlineClassNameAffectsLetterSpacing?: boolean;
  };
}

// ============================================================================
// API Response Types
// ============================================================================

export interface ChunksResponse {
  chunks: SemanticChunk[];
  total: number;
}

export interface AnnotationsResponse {
  annotations: Annotation[];
  total: number;
}

export interface QualityResponse {
  quality: QualityDetails;
}

export interface ReferencesResponse {
  references: Reference[];
  total: number;
}
