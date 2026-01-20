import { apiRequest } from './apiUtils';
import { ResourceRead } from './types';

export type RecommendationCategory = 'fresh_finds' | 'similar_to_recent' | 'hidden_gems';

export interface RecommendationExplanation {
    reason: string;
    score?: number;
    context?: string;
}

export interface RecommendationItem extends ResourceRead {
    recommendation_id: string;
    category: RecommendationCategory;
    explanation: RecommendationExplanation;
}

export interface BackendRecommendationItem {
    resource_id: string;
    title: string;
    score: number;
    strategy: string;
    scores: any;
    rank: number;
    novelty_score: number;
    view_count: number;
}

export interface RecommendationFeedbackPayload {
    resource_id: string;
    feedback_type: 'thumbs_up' | 'thumbs_down';
    section?: RecommendationCategory;
}

export interface InteractionPayload {
    resource_id: string;
    event_type: 'view' | 'click' | 'open_detail';
    metadata?: Record<string, unknown>;
}

export interface RecommendationsMetrics {
    ctr: number;
    diversity_score: number;
    novelty_score: number;
    total_recommendations: number;
    total_interactions: number;
}

export const recommendationsApi = {
    getRecommendations: async (category?: RecommendationCategory): Promise<RecommendationItem[]> => {
        const params = new URLSearchParams();
        if (category) {
            params.append('category', category);
        }
        const response = await apiRequest<{ recommendations: BackendRecommendationItem[], metadata: any }>(`/api/recommendations?${params.toString()}`);

        return response.recommendations.map(item => ({
            id: item.resource_id,
            title: item.title,
            description: 'Description not available', // Placeholder
            type: 'article', // Placeholder
            subject: [], // Placeholder
            creator: 'Unknown', // Placeholder
            quality_score: 0, // Placeholder
            url: '', // Placeholder

            // ResourceRead required fields
            has_embedding: true,
            ingestion_status: 'completed',
            date_created: new Date().toISOString(),
            date_modified: new Date().toISOString(),

            recommendation_id: item.resource_id,
            category: category || 'fresh_finds',
            explanation: {
                reason: `Recommended based on ${item.strategy}`,
                score: item.score
            }
        })) as RecommendationItem[];
    },

    sendFeedback: async (payload: RecommendationFeedbackPayload): Promise<void> => {
        return apiRequest<void>('/recommendations/feedback', {
            method: 'POST',
            body: JSON.stringify(payload),
        });
    },

    trackInteraction: async (payload: InteractionPayload): Promise<void> => {
        return apiRequest<void>('/interactions', {
            method: 'POST',
            body: JSON.stringify(payload),
        });
    },

    getMetrics: async (): Promise<RecommendationsMetrics> => {
        return apiRequest<RecommendationsMetrics>('/recommendations/metrics');
    },
};
