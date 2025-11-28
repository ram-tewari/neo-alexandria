import { Resource } from './resource';

export interface SearchQuery {
  text: string;
  filters: SearchFilter[];
  weights: SearchWeights;
  method: 'fts5' | 'vector' | 'hybrid';
  booleanOperators?: BooleanExpression[];
}

export interface SearchFilter {
  field: string;
  operator: string;
  value: any;
}

export interface SearchWeights {
  keyword: number;
  semantic: number;
  sparse: number;
}

export interface BooleanExpression {
  operator: 'AND' | 'OR' | 'NOT';
  terms: string[];
}

export interface SearchResult {
  resource: Resource;
  score: number;
  explanation: RelevanceExplanation;
  highlights: Highlight[];
}

export interface RelevanceExplanation {
  keywordScore: number;
  semanticScore: number;
  sparseScore: number;
  factors: string[];
}

export interface Highlight {
  field: 'title' | 'abstract' | 'content';
  text: string;
  start: number;
  end: number;
}

export interface SearchSuggestion {
  text: string;
  type: 'resource' | 'collection' | 'tag' | 'author';
  highlight: [number, number][];
}

export interface QuickFilter {
  id: string;
  label: string;
  filter: SearchFilter;
}

export interface SavedSearch {
  id: string;
  name: string;
  query: SearchQuery;
  createdAt: Date;
}

export type SortOption = 'recent' | 'title' | 'quality' | 'relevance';
