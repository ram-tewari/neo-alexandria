export interface Recommendation {
  resource: {
    id: string;
    title: string;
    authors: string[];
    abstract: string;
    type: 'pdf' | 'url' | 'arxiv';
    qualityScore: number;
    classification: string[];
    thumbnail?: string;
    createdAt: Date;
  };
  score: number;
  category: 'fresh' | 'similar' | 'hidden';
  explanation: string;
  reasons: string[];
}

export interface UserPreferences {
  interests: string[];
  diversity: number; // 0-1 scale
  novelty: number; // 0-1 scale
  recency: number; // 0-1 scale
  domains: string[];
}

export interface RecommendationMetrics {
  clickThroughRate: number;
  diversityScore: number;
  noveltyScore: number;
  userSatisfaction: number;
  totalRecommendations: number;
  totalClicks: number;
}

export interface RecommendationFeedback {
  recommendationId: string;
  resourceId: string;
  type: 'like' | 'dislike' | 'not_interested' | 'save';
  timestamp: Date;
}
