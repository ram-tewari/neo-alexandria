export interface TaxonomyNode {
  id: string;
  name: string;
  parentId?: string;
  children: TaxonomyNode[];
  resourceCount: number;
  depth: number;
  path: string[];
  metadata?: Record<string, any>;
}

export interface ClassificationSuggestion {
  id: string;
  resourceId: string;
  category: string;
  confidence: number;
  reasoning: string[];
  status: 'pending' | 'accepted' | 'rejected';
  createdAt: Date;
}

export interface ActiveLearningItem {
  resourceId: string;
  title: string;
  abstract: string;
  suggestions: ClassificationSuggestion[];
  uncertainty: number;
  priority: number;
}

export interface ClassificationFeedback {
  suggestionId: string;
  resourceId: string;
  category: string;
  accepted: boolean;
  correctCategory?: string;
  timestamp: Date;
}

export interface ModelTrainingStatus {
  status: 'idle' | 'training' | 'completed' | 'failed';
  progress: number;
  stage: string;
  accuracy?: number;
  startedAt?: Date;
  completedAt?: Date;
  error?: string;
}

export interface TaxonomyStats {
  totalNodes: number;
  totalCategories: number;
  maxDepth: number;
  averageResourcesPerCategory: number;
  uncategorizedResources: number;
}

export interface ClassificationMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1Score: number;
  totalPredictions: number;
  correctPredictions: number;
  confusionMatrix?: number[][];
}

export const CONFIDENCE_THRESHOLDS = {
  high: 0.8,
  medium: 0.5,
  low: 0.3,
} as const;

export type ConfidenceLevel = 'high' | 'medium' | 'low';
