import { apiRequest } from './apiUtils';

export interface UserProfile {
    id: string;
    name: string;
    email: string;
    avatar_url?: string;
    interest_tags: string[];
    research_domains: string[];
    preferences: {
        diversity: number; // 0-100
        novelty: number;   // 0-100
        recency: number;   // 0-100
    };
}

export interface UpdateProfilePayload {
    interest_tags?: string[];
    research_domains?: string[];
    preferences?: {
        diversity?: number;
        novelty?: number;
        recency?: number;
    };
}

export const profileApi = {
    getProfile: async (): Promise<UserProfile> => {
        return apiRequest<UserProfile>('/profile');
    },

    updateProfile: async (payload: UpdateProfilePayload): Promise<UserProfile> => {
        return apiRequest<UserProfile>('/profile', {
            method: 'PUT',
            body: JSON.stringify(payload),
        });
    },
};
