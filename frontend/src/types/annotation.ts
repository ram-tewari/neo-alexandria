export interface Annotation {
  id: string;
  resourceId: string;
  userId: string;
  type: 'highlight' | 'note' | 'tag';
  text: string;
  note?: string;
  tags: string[];
  color: string;
  position: AnnotationPosition;
  createdAt: Date;
  updatedAt: Date;
}

export interface AnnotationPosition {
  start: number;
  end: number;
  page?: number;
  rects?: DOMRect[];
}

export interface TextSelection {
  text: string;
  start: number;
  end: number;
  rects: DOMRect[];
}

export interface AnnotationFilters {
  resourceIds?: string[];
  tags?: string[];
  colors?: string[];
  dateRange?: [Date, Date];
  searchQuery?: string;
}

export interface AnnotationGroup {
  key: string;
  label: string;
  annotations: Annotation[];
}

export interface SemanticSearchResult {
  annotation: Annotation;
  similarity: number;
  relatedAnnotations: {
    annotation: Annotation;
    similarity: number;
  }[];
}

export interface ConceptCluster {
  id: string;
  label: string;
  annotations: Annotation[];
  centroid: number[];
  color: string;
}

export const HIGHLIGHT_COLORS = [
  { name: 'Yellow', value: '#fef08a', dark: '#fde047' },
  { name: 'Green', value: '#bbf7d0', dark: '#86efac' },
  { name: 'Blue', value: '#bfdbfe', dark: '#93c5fd' },
  { name: 'Purple', value: '#e9d5ff', dark: '#d8b4fe' },
  { name: 'Pink', value: '#fbcfe8', dark: '#f9a8d4' },
  { name: 'Orange', value: '#fed7aa', dark: '#fdba74' },
  { name: 'Red', value: '#fecaca', dark: '#fca5a5' },
] as const;

export type HighlightColor = typeof HIGHLIGHT_COLORS[number];
