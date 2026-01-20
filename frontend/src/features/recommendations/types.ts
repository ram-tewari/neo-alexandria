/**
 * Recommendations Feature Types
 * Defines interfaces for personalized recommendations
 */

export interface Recommendation {
  id: string;
  title: string;
  description: string;
  reason: string; // e.g., "Similar to X", "Popular in Y"
  resource_type: string;
  quality_score: number;
  created_at: string;
}

export interface RecommendationsResponse {
  recommendations: Recommendation[];
  total: number;
}
