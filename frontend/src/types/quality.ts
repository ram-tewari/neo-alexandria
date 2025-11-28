export interface QualityScore {
  overall: number;
  dimensions: QualityDimension[];
  timestamp: Date;
}

export interface QualityDimension {
  name: string;
  score: number;
  maxScore: number;
  description: string;
  weight: number;
}

export interface QualityDistribution {
  bins: { min: number; max: number; count: number }[];
  mean: number;
  median: number;
  stdDev: number;
  total: number;
}

export interface QualityTrend {
  dimension: string;
  values: { date: Date; score: number }[];
}

export interface QualityOutlier {
  resourceId: string;
  title: string;
  score: number;
  issues: QualityIssue[];
  suggestions: string[];
}

export interface QualityIssue {
  type: 'missing_metadata' | 'low_citation' | 'incomplete_abstract' | 'no_classification' | 'poor_formatting';
  severity: 'low' | 'medium' | 'high';
  description: string;
  field?: string;
}

export interface ReviewQueueItem {
  resourceId: string;
  title: string;
  priority: number;
  issues: QualityIssue[];
  lastReviewed?: Date;
  status: 'pending' | 'in_progress' | 'completed';
}

export interface BulkEditOperation {
  field: string;
  operation: 'set' | 'append' | 'remove' | 'replace';
  value: any;
  oldValue?: any;
}

export interface DuplicateGroup {
  id: string;
  resources: {
    id: string;
    title: string;
    similarity: number;
    metadata: Record<string, any>;
  }[];
  suggestedPrimary: string;
}

export interface QualityMetrics {
  totalResources: number;
  averageQuality: number;
  qualityDistribution: QualityDistribution;
  topDimensions: { name: string; score: number }[];
  bottomDimensions: { name: string; score: number }[];
  recentTrends: QualityTrend[];
  outlierCount: number;
}

export const QUALITY_DIMENSION_NAMES = [
  'Completeness',
  'Accuracy',
  'Consistency',
  'Timeliness',
  'Relevance',
  'Accessibility',
] as const;

export type QualityDimensionName = typeof QUALITY_DIMENSION_NAMES[number];
