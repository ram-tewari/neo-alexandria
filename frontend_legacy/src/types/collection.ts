/**
 * Collection Types
 * 
 * Type definitions for collections matching backend schema
 */

import type { ResourceSummary } from './resource';

export interface Collection {
  id: string;
  name: string;
  description: string | null;
  owner_id: string;
  visibility: 'private' | 'shared' | 'public';
  parent_id: string | null;
  resource_count: number;
  created_at: string;
  updated_at: string;
}

export interface CollectionDetail extends Collection {
  resources: ResourceSummary[];
  subcollections: Collection[];
}

export interface CollectionCreate {
  name: string;
  description?: string;
  visibility?: 'private' | 'shared' | 'public';
  parent_id?: string;
  smart_definition?: SmartCollectionDefinition;
}

export interface CollectionUpdate {
  name?: string;
  description?: string;
  visibility?: 'private' | 'shared' | 'public';
  parent_id?: string;
}

export interface CollectionNode extends Collection {
  children: CollectionNode[];
  isExpanded: boolean;
  depth: number;
}

export interface CollectionListParams {
  page?: number;
  limit?: number;
  owner_id?: string;
  visibility?: 'private' | 'shared' | 'public';
}

export interface CollectionStats {
  resourceCount: number;
  avgQuality: number;
  lastUpdated: string;
  topTags: string[];
}

export type SmartCollectionRuleOperator = 'equals' | 'contains' | 'gt' | 'lt' | 'gte' | 'lte' | 'in';
export type SmartCollectionRuleField = 'quality' | 'classification' | 'tags' | 'created_at' | 'author';

export interface SmartCollectionRule {
  id: string;
  field: SmartCollectionRuleField;
  operator: SmartCollectionRuleOperator;
  value: string | number | string[];
}

export interface SmartCollectionDefinition {
  rules: SmartCollectionRule[];
  matchType: 'all' | 'any';
}
