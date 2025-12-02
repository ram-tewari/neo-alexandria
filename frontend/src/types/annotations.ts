/**
 * Type definitions for Annotations and Active Reading features
 */

// ============================================================================
// Core Annotation Types
// ============================================================================

export interface AnnotationHighlight {
    /** Zero-indexed character offset where highlight starts */
    startOffset: number;
    /** Zero-indexed character offset where highlight ends */
    endOffset: number;
    /** Page number in document (1-indexed) */
    pageNumber?: number;
    /** Highlight color from predefined palette */
    color: AnnotationColor;
    /** Selected text content */
    text: string;
    /** Optional coordinate metadata for precise positioning */
    coordinates?: {
        x: number;
        y: number;
        width: number;
        height: number;
    };
}

export type AnnotationColor = 'yellow' | 'green' | 'blue' | 'pink' | 'orange';

export interface AnnotationTag {
    id: string;
    name: string;
    color?: string;
}

export interface Annotation {
    id: string;
    resourceId: string;
    highlight: AnnotationHighlight;
    note?: string;
    tags: AnnotationTag[];
    createdAt: string;
    updatedAt: string;
    userId?: string;
}

// ============================================================================
// Request/Response Types
// ============================================================================

export interface AnnotationCreateRequest {
    highlight: AnnotationHighlight;
    note?: string;
    tags?: string[]; // Tag names or IDs
}

export interface AnnotationUpdateRequest {
    note?: string;
    tags?: string[];
    highlight?: Partial<AnnotationHighlight>;
}

export interface AnnotationListResponse {
    items: Annotation[];
    total: number;
    limit?: number;
    offset?: number;
}

// ============================================================================
// Search and Filter Types
// ============================================================================

export interface AnnotationSearchFilters {
    resourceId?: string;
    tags?: string[];
    color?: AnnotationColor;
    dateFrom?: string;
    dateTo?: string;
    query?: string; // Full-text search query
}

export interface AnnotationSearchResult {
    annotation: Annotation;
    snippet: string;
    matchScore: number;
    highlights?: Array<{
        field: string;
        matches: string[];
    }>;
}

export interface AnnotationSearchResponse {
    results: AnnotationSearchResult[];
    total: number;
    query: string;
}

// ============================================================================
// Semantic Search Types
// ============================================================================

export interface SemanticAnnotationResult {
    annotation: Annotation;
    similarityScore: number;
    relatedAnnotations: Array<{
        annotation: Annotation;
        score: number;
    }>;
}

export interface AnnotationCluster {
    id: string;
    label: string;
    topicKeywords: string[];
    annotationCount: number;
    annotations: Annotation[];
    color: string;
    centroid?: number[]; // Embedding centroid
}

export interface SemanticSearchResponse {
    results: SemanticAnnotationResult[];
    clusters: AnnotationCluster[];
    total: number;
    query: string;
}

// ============================================================================
// Export Types
// ============================================================================

export type ExportFormat = 'markdown' | 'json';

export interface ExportOptions {
    format: ExportFormat;
    filters?: AnnotationSearchFilters;
    includeMetadata?: boolean;
}

export interface ExportResponse {
    content: string;
    filename: string;
    mimeType: string;
}

// ============================================================================
// UI State Types
// ============================================================================

export interface TextSelection {
    text: string;
    startOffset: number;
    endOffset: number;
    pageNumber?: number;
    boundingRect: DOMRect;
}

export interface AnnotationEditorState {
    mode: 'create' | 'edit';
    annotation?: Annotation;
    selection?: TextSelection;
    isOpen: boolean;
    color: AnnotationColor;
}

export type AnnotationGrouping = 'chronological' | 'resource' | 'tag';

export interface AnnotationNotebookState {
    filters: AnnotationSearchFilters;
    grouping: AnnotationGrouping;
    searchQuery: string;
    isSemanticSearch: boolean;
}
